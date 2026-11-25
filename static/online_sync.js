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
      this.durablePending = new Map();
      this.lastOutbox = null;
      this.backupTimer = null;
      this.latestBackup = null;
      this.lastYieldAt = Date.now();
      try {
        const saved = JSON.parse(storage.getItem(key + ':outbox') || '[]');
        if (Array.isArray(saved)) {
          // Migrate existing durable operations on the next write; never drop an old outbox.
          for (const item of saved) this.pending.set(item.message_id, item);
        } else if (saved?.version === 2 && Array.isArray(saved.ids)) {
          for (const id of saved.ids) {
            const encoded = storage.getItem(key + ':operation:' + id);
            const item = encoded && JSON.parse(encoded);
            if (!item || item.message_id !== id) throw new Error('連線操作紀錄不完整，請重新整理。');
            this.pending.set(id,item);
            this.encodedPending.set(id,encoded);
            this.durablePending.set(id,encoded);
          }
          this.lastOutbox=JSON.stringify(saved);
        } else throw new Error('無法辨識連線操作紀錄。');
      } catch (error) { this.stop(error); }
    }
    metadata() { return { epoch: this.epoch, cursor: this.cursor }; }
    restore(meta) {
      if (!meta || typeof meta.epoch !== 'string' || (!Number.isSafeInteger(meta.cursor) || meta.cursor < 0)) return;
      this.epoch = meta.epoch;
      this.cursor = meta.cursor;
    }
    persistOutbox() {
      try {
        for (const [id,message] of this.pending) {
          if(!this.encodedPending.has(id))this.encodedPending.set(id,JSON.stringify(message));
          const encoded=this.encodedPending.get(id);
          if(this.durablePending.get(id)!==encoded){
            this.storage.setItem(this.key+':operation:'+id,encoded);
            this.durablePending.set(id,encoded);
          }
        }
        // Commit the small index only after every referenced operation is durable.
        // Rewriting all large snapshots on each send AND each ACK caused quadratic stalls.
        const index=JSON.stringify({version:2,ids:[...this.pending.keys()]});
        if(index!==this.lastOutbox){
          this.storage.setItem(this.key+':outbox',index);
          this.lastOutbox=index;
        }
        for(const id of this.durablePending.keys())if(!this.pending.has(id)){
          if(this.storage.removeItem)this.storage.removeItem(this.key+':operation:'+id);
          else this.storage.setItem(this.key+':operation:'+id,'');
          this.durablePending.delete(id);
          this.encodedPending.delete(id);
        }
      } catch (_) {
        this.stop(new Error('瀏覽器無法儲存連線紀錄，請檢查儲存空間。'));
        throw new Error('Cannot persist outgoing game operation');
      }
    }
    discard() {
      this.clearBackup();
      this.ready=false;
      this.wireReady=false;
      const ids=new Set([...this.pending.keys(),...this.durablePending.keys()]);
      const remove=key=>{if(this.storage.removeItem)this.storage.removeItem(key);else this.storage.setItem(key,'');};
      try {
        // Explicit room exit abandons recovery and must also release large per-operation bodies.
        remove(this.key+':outbox');
        for(const id of ids)remove(this.key+':operation:'+id);
      } finally {
        this.pending.clear();this.encodedPending.clear();this.durablePending.clear();this.lastAttempt.clear();this.lastOutbox=null;
      }
    }
    raw(message) {
      if (["end_turn","mulligan_confirm"].includes(message.action)) global.XLWInputDiagnostics?.mark("wire:send",{action:message.action,ready:this.ready,buffered:this.socket?.bufferedAmount});
      if (this.socket?.readyState === 1) {
        const encoded = typeof message === 'string' ? message :
          message.message_id && this.pending.get(message.message_id) === message
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
    clearBackup() {
      if (this.backupTimer !== null) clearTimeout(this.backupTimer);
      this.backupTimer = null;
      this.latestBackup = null;
    }
    send(message) {
      // Display-only durations are replaceable; never checkpoint or replay each clock tick.
      if(message.action==='turn_clock'){if(this.ready&&!this.failed&&!this.pending.size&&!(this.socket?.bufferedAmount>65536))this.raw(message);return;}
      if(message.action==='duel_diagnostic_receipt'){if(this.ready&&!this.failed&&!this.pending.size&&!(this.socket?.bufferedAmount>65536))this.raw(message);return;}

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
      if (message.action === 'new_game') this.clearBackup();
      message.message_id ||= global.crypto.randomUUID();
      if(message.action!=='duel_diagnostic_receipt')global.XLWDuelDiagnostics?.record('send',{action:message.action,pending:this.pending.size});
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
      this.clearBackup();
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
      // Reuse the immutable JSON already written by the durable checkpoint.
      // Large recovery backups must not be cloned/encoded again for every action.
      socket.sendBackup = stateJSON => {
        if (this.ready && !this.failed) this.queueBackup('{"action":"backup_client_state","state":' + stateJSON + '}');
      };
      socket.onmessage = event => {
        if (socket !== this.socket || this.failed) return;
        let data;
        try { data = JSON.parse(event.data); }
        catch (error) { this.stop(error); return; }
        if (!data || typeof data !== 'object' || Array.isArray(data)) {
          this.stop(new Error('收到無法辨識的同步訊息，請重新整理。'));
          return;
        }
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
          try { this.persistOutbox(); }
          catch (_) { return; } // persistOutbox already pauses synchronization.
          return;
        }
        if(data.action==='duel_diagnostic_receipt'){Promise.resolve(this.process(data)).catch(()=>{});return;}
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
        if(data.action==='turn_clock'){Promise.resolve(this.process(data)).catch(error=>this.stop(error));return;}
        const seq = data.server_seq;
        if (Number.isSafeInteger(seq)) {
          if (seq <= this.cursor || this.queued.has(seq)) return;
          this.queued.add(seq);
        }
        const run = async (bypass = false) => {
          // Bound a burst of expensive snapshots without delaying replies that unblock a choice.
          if (!bypass && Date.now() - this.lastYieldAt >= 8 && global.document?.visibilityState === 'visible') {
            await new Promise(resolve => setTimeout(resolve, 0));
            this.lastYieldAt = Date.now();
          }
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
            // A burst shares one durable checkpoint. Never acknowledge a cursor
            // before both its state and metadata have been persisted.
            if (!this.processing && this.queued.size === 0) {
              this.checkpoint();
              this.raw({ action: 'delivery_applied', epoch: this.epoch, cursor: this.cursor });
            }
          }
        };
        // These replies release promises awaited by the current game handler.
        if (this.processing > 0 && this.canBypass(data.action, data)) run(true).catch(error => this.stop(error));
        else this.tail = this.tail.then(run).catch(error => this.stop(error));
      };
    }
    stop(error) {
      if (this.failed) return;
      this.clearBackup();
      this.failed = true;
      this.ready = false;
      this.wireReady = false;
      global.XLWDuelDiagnostics?.record('sync_stopped',{message:String(error.message||error).slice(0,180)});
      this.fail(error.message || String(error));
    }
  }
  global.XLWOnlineSync = OnlineSync;
})(typeof window === 'undefined' ? globalThis : window);
