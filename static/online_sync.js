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
      this.pending = new Map();
      try {
        const items = JSON.parse(storage.getItem(key + ':outbox') || '[]');
        for (const item of items) this.pending.set(item.message_id, item);
      } catch (_) {}
    }
    metadata() { return { epoch: this.epoch, cursor: this.cursor }; }
    restore(meta) {
      if (!meta || typeof meta.epoch !== 'string' || !Number.isSafeInteger(meta.cursor)) return;
      this.epoch = meta.epoch;
      this.cursor = meta.cursor;
    }
    persistOutbox() {
      try { this.storage.setItem(this.key + ':outbox', JSON.stringify([...this.pending.values()])); }
      catch (_) { this.stop(new Error('瀏覽器無法儲存連線紀錄，請檢查儲存空間。')); throw new Error('Cannot persist outgoing game operation'); }
    }
    raw(message) {
      if (this.socket?.readyState === 1) this.originalSend.call(this.socket, JSON.stringify(message));
    }
    send(message) {
      if (message.action === 'leave_room') {
        message.message_id ||= global.crypto.randomUUID();
        this.raw(message);
        return;
      }
      if (['ping', 'pong', 'backup_client_state'].includes(message.action)) {
        if (this.ready || message.action === 'ping') this.raw(message);
        return;
      }
      if (this.failed) throw new Error('Online synchronization is paused');
      message.message_id ||= global.crypto.randomUUID();
      this.pending.set(message.message_id, message);
      this.persistOutbox();
      // Persist locally-mutated game state before the peer can acknowledge this action.
      if (!this.processing) {
        this.sendingAction = message.action;
        try { this.checkpoint(); }
        catch (error) { this.stop(error); throw error; }
        finally { this.sendingAction = null; }
      }
      if (this.ready) this.raw(message);
    }
    resend() {
      if (!this.ready || this.failed) return;
      for (const message of this.pending.values()) this.raw(message);
    }
    attach(socket) {
      this.socket = socket;
      this.originalSend = socket.send;
      this.ready = false;
      socket.send = value => this.send(JSON.parse(value));
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
          this.pending.delete(data.message_id);
          this.persistOutbox();
          return;
        }
        if (data.action === 'pong') { this.lastPong = Date.now(); return; }
        if (data.type === 'sync_error' || data.type === 'error') {
          this.stop(new Error(data.message));
          return;
        }
        if (data.type === 'resume_complete') {
          this.tail = this.tail.then(() => {
            if (socket !== this.socket || this.failed) return;
            this.epoch = data.epoch;
            this.ready = true;
            this.lastPong = Date.now();
            this.checkpoint();
            this.resend();
            global.dispatchEvent?.(new Event('xlw-sync-ready'));
          }).catch(error => this.stop(error));
          return;
        }
        if (data.type === 'restore_client_backup') {
          this.tail = this.tail.then(async () => {
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
        if (this.processing > 0 && this.canBypass(data.action)) run().catch(error => this.stop(error));
        else this.tail = this.tail.then(run).catch(error => this.stop(error));
      };
    }
    stop(error) {
      if (this.failed) return;
      this.failed = true;
      this.ready = false;
      this.fail(error.message || String(error));
    }
  }
  global.XLWOnlineSync = OnlineSync;
})(typeof window === 'undefined' ? globalThis : window);
