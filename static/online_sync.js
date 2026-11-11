/* Reliable WebSocket delivery and ordered game-message processing. */
(function (global) {
  "use strict";
  class OnlineSync {
    constructor({ key, storage, process, checkpoint, fail, canBypass = () => false }) {
      this.key = key;
      this.canBypass = canBypass;
      this.storage = storage;
      this.process = process;
      this.checkpoint = checkpoint;
      this.fail = fail;
      this.epoch = null;
      this.cursor = 0;
      this.completed = new Set();
      this.queued = new Set();
      this.tail = Promise.resolve();
      this.failed = false;
      this.processing = 0;
      this.ready = false;
      this.wireReady = false;
      this.lastAttempt = new Map();
      this.pending = new Map();
      this.encodedPending = new Map();
      this.lastOutbox = null;
      this.backupTimer = null;
      this.latestBackup = null;
      try {
        const items = JSON.parse(storage.getItem(key + ':outbox') || '[]');
        for (const item of items) this.pending.set(item.message_id, item);
      } catch (_) {}
    }
    metadata() { return { epoch: this.epoch, cursor: this.cursor }; }
    restore(meta) {
      if (!meta || typeof meta.epoch !== 'string' || (!Number.isSafeInteger(meta.cursor) || meta.cursor < 0)) return;
      this.epoch = meta.epoch;
      this.cursor = meta.cursor;
    }
    persistOutbox() {
      try {
        const entries = [];
        for (const [id, message] of this.pending) {
          if (!this.encodedPending.has(id)) this.encodedPending.set(id, JSON.stringify(message));
          entries.push(this.encodedPending.get(id));
        }
        for (const id of this.encodedPending.keys()) {
          if (!this.pending.has(id)) this.encodedPending.delete(id);
        }
        const outbox = '[' + entries.join(',') + ']';
        if (outbox !== this.lastOutbox) {
          this.storage.setItem(this.key + ':outbox', outbox);
          this.lastOutbox = outbox;
        }
      }
      catch (_) { this.stop(new Error('瀏覽器無法儲存連線紀錄，請檢查儲存空間。')); throw new Error('Cannot persist outgoing game operation'); }
    }
    raw(message) {
      if (["end_turn","mulligan_confirm"].includes(message.action)) global.XLWInputDiagnostics?.mark("wire:send",{action:message.action,ready:this.ready,buffered:this.socket?.bufferedAmount});
      if (this.socket?.readyState === 1) {
        const encoded = message.message_id && this.pending.get(message.message_id) === message
          ? this.encodedPending.get(message.message_id) : null;
        try {
          this.originalSend.call(this.socket, encoded || JSON.stringify(message));
          if (message.message_id && this.pending.has(message.message_id)) this.lastAttempt.set(message.message_id, Date.now());
        } catch (_) {
          // A socket can fail between readyState and send. Keep the durable
          // outbox intact and let the normal reconnect handshake retry it.
          this.ready = false;
          this.wireReady = false;
          try { this.socket.close(); } catch (_) {}
        }
      }
    }
    queueBackup(message) {
      this.latestBackup = message;
      if (this.backupTimer !== null) return;
      this.backupTimer = setTimeout(() => {
        this.backupTimer = null;
        if (!this.ready || this.failed) return;
        // Bulk recovery data must never build an upload queue ahead of player input.
        if (this.pending.size || this.processing || this.socket?.bufferedAmount > 0) {
          this.queueBackup(this.latestBackup);
          return;
        }
        const latest = this.latestBackup;
        this.latestBackup = null;
        if (latest) this.raw(latest);
      }, 1000);
    }
    send(message) {
      if (message.action === 'leave_room') {
        message.message_id ||= global.crypto.randomUUID();
        this.raw(message);
        return;
      }
      if (message.action === 'backup_client_state') {
        if (this.ready) this.queueBackup(message);
        return;
      }
      if (['ping', 'pong'].includes(message.action)) {
        if (this.ready || message.action === 'ping') this.raw(message);
        return;
      }
      if (this.failed) throw new Error('Online synchronization is paused');
      message.message_id ||= global.crypto.randomUUID();
      if (["end_turn","mulligan_confirm"].includes(message.action)) global.XLWInputDiagnostics?.mark("send:entry",{action:message.action});
      if (this.pending.get(message.message_id) !== message) this.encodedPending.delete(message.message_id);
      this.pending.set(message.message_id, message);
      this.persistOutbox();
      // Persist locally-mutated game state before the peer can acknowledge this action.
      if (!this.processing) {
        this.sendingAction = message.action;
        try { this.checkpoint(); }
        catch (error) { this.stop(error); throw error; }
        finally { this.sendingAction = null; }
      }
      if (this.ready || this.wireReady) this.raw(message);
    }
    resend(force = true) {
      if (this.failed || (!this.ready && !this.wireReady)) return;
      // Do not queue repeated snapshots behind data the network is still uploading.
      if (this.socket?.bufferedAmount > 65536) return;
      for (const message of this.pending.values()) {
        if (!force && Date.now() - (this.lastAttempt.get(message.message_id) || 0) < 3000) continue;
        this.raw(message);
        if (this.socket?.bufferedAmount > 65536) break;
      }
    }
    attach(socket) {
      this.socket = socket;
      this.originalSend = socket.send;
      this.ready = false;
      this.wireReady = false;
      this.lastAttempt.clear();
      this.lastPong = Date.now();
      socket.send = value => this.send(JSON.parse(value));
      // Preserve the snapshot at the send boundary, including during retries.
      socket.sendObject = message => this.send(
        typeof global.structuredClone === 'function'
          ? global.structuredClone(message)
          : JSON.parse(JSON.stringify(message))
      );
      socket.onmessage = event => {
        if (socket !== this.socket || this.failed) return;
        let data;
        try { data = JSON.parse(event.data); }
        catch (error) { this.stop(error); return; }
        if (data.type === 'welcome') {
          if (data.sync_protocol !== 2) {
            this.stop(new Error('伺服器版本不同，請雙方重新整理後再連線。'));
            return;
          }
          this.raw({ action: 'resume_delivery', epoch: this.epoch, cursor: this.cursor });
          // Welcome contains no mutable game state and must not wait for a modal.
          Promise.resolve(this.process(data)).catch(error => this.stop(error));
          return;
        }
        if (data.type === 'delivery_ack') {
          const sent = this.pending.get(data.message_id);
          if (sent && ["end_turn","mulligan_confirm"].includes(sent.action)) global.XLWInputDiagnostics?.mark("wire:ack",{action:sent.action});
          this.pending.delete(data.message_id);
          this.lastAttempt.delete(data.message_id);
          this.persistOutbox();
          return;
        }
        if (data.action === 'pong') { this.lastPong = Date.now(); return; }
        if (data.type === 'sync_error' || data.type === 'error') {
          this.stop(new Error(data.message));
          return;
        }
        if (data.type === 'resume_complete') {
          if (this.epoch && data.epoch !== this.epoch) {
            this.stop(new Error('對局紀錄已重建，請重新開局。'));
            return;
          }
          // The server has completed replay and now accepts operations. Retry
          // persisted replies here: an active handler may be waiting for them,
          // so putting this retry behind tail would deadlock that handler.
          this.wireReady = true;
          this.resend();
          if (!this.wireReady) return;
          this.tail = this.tail.then(() => {
            if (socket !== this.socket || this.failed || !this.wireReady) return;
            this.epoch = data.epoch;
            this.ready = true;
            this.lastPong = Date.now();
            this.checkpoint();
            global.dispatchEvent?.(new Event('xlw-sync-ready'));
          }).catch(error => this.stop(error));
          return;
        }
        if (data.type === 'restore_client_backup') {
          this.tail = this.tail.then(async () => {
            if (socket !== this.socket || this.failed) return;
            await this.process(data);
            this.restore(data.state?.sync_metadata);
          }).catch(error => this.stop(error));
          return;
        }
        const seq = data.server_seq;
        if (Number.isSafeInteger(seq)) {
          if (seq <= this.cursor || this.queued.has(seq)) return;
          this.queued.add(seq);
        }
        const run = async () => {
          if (this.failed || (Number.isSafeInteger(seq) && seq <= this.cursor)) return;
          if (data.epoch) {
            if (this.epoch && data.epoch !== this.epoch) throw new Error('對局紀錄已重建，請重新開局。');
            this.epoch = data.epoch;
          }
          this.processing++;
          try { await this.process(data); }
          finally { this.processing--; }
          if (Number.isSafeInteger(seq)) {
            this.completed.add(seq);
            while (this.completed.delete(this.cursor + 1)) {
              this.queued.delete(++this.cursor);
            }
            // Save the applied state and its cursor together before acknowledging it.
            if (!this.processing) this.checkpoint();
            this.raw({ action: 'delivery_applied', epoch: this.epoch, cursor: this.cursor });
          }
        };
        // These replies release promises awaited by the current game handler.
        if (this.processing > 0 && this.canBypass(data.action, data)) run().catch(error => this.stop(error));
        else this.tail = this.tail.then(run).catch(error => this.stop(error));
      };
    }
    stop(error) {
      if (this.failed) return;
      if (this.backupTimer !== null) clearTimeout(this.backupTimer);
      this.backupTimer = null;
      this.latestBackup = null;
      this.failed = true;
      this.ready = false;
      this.wireReady = false;
      this.fail(error.message || String(error));
    }
  }
  global.XLWOnlineSync = OnlineSync;
})(typeof window === 'undefined' ? globalThis : window);
