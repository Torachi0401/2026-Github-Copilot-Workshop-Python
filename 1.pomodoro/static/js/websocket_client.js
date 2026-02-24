/**
 * WebSocket リアルタイム同期クライアント
 */

(function() {
  'use strict';

  // Socket.ioクライアントが利用可能かチェック
  if (typeof io === 'undefined') {
    console.warn('Socket.io client not loaded. Real-time sync disabled.');
    return;
  }

  class WebSocketSync {
    constructor() {
      this.socket = null;
      this.room = 'default';
      this.isConnected = false;
      this.syncEnabled = false;
      
      // ローカルストレージから同期設定を読み込む
      this.loadSettings();
      this.setupUI();
    }

    /**
     * 設定を読み込む
     */
    loadSettings() {
      const settings = localStorage.getItem('websocket_settings');
      if (settings) {
        const parsed = JSON.parse(settings);
        this.syncEnabled = parsed.syncEnabled || false;
        this.room = parsed.room || 'default';
      }
    }

    /**
     * 設定を保存
     */
    saveSettings() {
      localStorage.setItem('websocket_settings', JSON.stringify({
        syncEnabled: this.syncEnabled,
        room: this.room
      }));
    }

    /**
     * UIセットアップ
     */
    setupUI() {
      // DOMContentLoadedを待つ
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.initUI());
      } else {
        this.initUI();
      }
    }

    /**
     * UIを初期化
     */
    initUI() {
      const checkbox = document.getElementById('enableWebSocketSync');
      if (checkbox) {
        // 保存された設定を反映
        checkbox.checked = this.syncEnabled;
        
        // チェックボックスのイベントリスナー
        checkbox.addEventListener('change', (e) => {
          if (e.target.checked) {
            this.enableSync();
          } else {
            this.disableSync();
          }
        });
      }
    }

    /**
     * WebSocket接続を初期化
     */
    connect() {
      if (this.socket) {
        console.log('WebSocket already connected');
        return;
      }

      try {
        this.socket = io({
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionAttempts: 5
        });

        this.setupEventHandlers();
        console.log('WebSocket connecting...');
      } catch (error) {
        console.error('WebSocket connection error:', error);
      }
    }

    /**
     * WebSocket切断
     */
    disconnect() {
      if (this.socket) {
        this.socket.disconnect();
        this.socket = null;
        this.isConnected = false;
        console.log('WebSocket disconnected');
      }
    }

    /**
     * イベントハンドラーをセットアップ
     */
    setupEventHandlers() {
      this.socket.on('connect', () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.socket.emit('join_sync', { room: this.room });
        
        // 通知を表示
        if (window.CSVManager && window.CSVManager.showNotification) {
          window.CSVManager.showNotification('リアルタイム同期が有効になりました', 'success');
        }
      });

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
      });

      this.socket.on('connection_response', (data) => {
        console.log('Connection response:', data);
      });

      this.socket.on('sync_status', (data) => {
        console.log('Sync status:', data);
      });

      this.socket.on('timer_sync', (data) => {
        console.log('Timer sync received:', data);
        this.handleTimerSync(data);
      });

      this.socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
      });
    }

    /**
     * タイマー同期イベントを処理
     */
    handleTimerSync(data) {
      if (!this.syncEnabled) {
        return;
      }

      const action = data.action;
      console.log(`Handling sync action: ${action}`);

      // TimerUIが利用可能かチェック
      if (!window.TimerUI) {
        console.warn('TimerUI not available');
        return;
      }

      try {
        switch (action) {
          case 'start':
            // 他のクライアントがタイマーを開始した
            if (window.TimerUI.syncStart) {
              window.TimerUI.syncStart(data);
            }
            break;
          case 'pause':
            // 他のクライアントがタイマーを一時停止した
            if (window.TimerUI.syncPause) {
              window.TimerUI.syncPause(data);
            }
            break;
          case 'resume':
            // 他のクライアントがタイマーを再開した
            if (window.TimerUI.syncResume) {
              window.TimerUI.syncResume(data);
            }
            break;
          case 'reset':
            // 他のクライアントがタイマーをリセットした
            if (window.TimerUI.syncReset) {
              window.TimerUI.syncReset(data);
            }
            break;
          case 'complete':
            // 他のクライアントがタイマーを完了した
            if (window.TimerUI.syncComplete) {
              window.TimerUI.syncComplete(data);
            }
            break;
        }
      } catch (error) {
        console.error('Error handling timer sync:', error);
      }
    }

    /**
     * タイマー開始を同期
     */
    broadcastTimerStart(type, duration) {
      if (!this.isConnected || !this.syncEnabled) {
        return;
      }

      this.socket.emit('timer_start', {
        room: this.room,
        type: type,
        duration: duration,
        timestamp: Date.now()
      });
    }

    /**
     * タイマー一時停止を同期
     */
    broadcastTimerPause(remaining) {
      if (!this.isConnected || !this.syncEnabled) {
        return;
      }

      this.socket.emit('timer_pause', {
        room: this.room,
        remaining: remaining,
        timestamp: Date.now()
      });
    }

    /**
     * タイマー再開を同期
     */
    broadcastTimerResume(remaining) {
      if (!this.isConnected || !this.syncEnabled) {
        return;
      }

      this.socket.emit('timer_resume', {
        room: this.room,
        remaining: remaining,
        timestamp: Date.now()
      });
    }

    /**
     * タイマーリセットを同期
     */
    broadcastTimerReset() {
      if (!this.isConnected || !this.syncEnabled) {
        return;
      }

      this.socket.emit('timer_reset', {
        room: this.room,
        timestamp: Date.now()
      });
    }

    /**
     * タイマー完了を同期
     */
    broadcastTimerComplete(sessionId) {
      if (!this.isConnected || !this.syncEnabled) {
        return;
      }

      this.socket.emit('timer_complete', {
        room: this.room,
        session_id: sessionId,
        timestamp: Date.now()
      });
    }

    /**
     * 同期を有効化
     */
    enableSync() {
      this.syncEnabled = true;
      this.saveSettings();
      if (!this.isConnected) {
        this.connect();
      }
      console.log('Real-time sync enabled');
    }

    /**
     * 同期を無効化
     */
    disableSync() {
      this.syncEnabled = false;
      this.saveSettings();
      this.disconnect();
      
      // 通知を表示
      if (window.CSVManager && window.CSVManager.showNotification) {
        window.CSVManager.showNotification('リアルタイム同期が無効になりました', 'info');
      }
      console.log('Real-time sync disabled');
    }

    /**
     * ルームを変更
     */
    changeRoom(newRoom) {
      if (this.isConnected) {
        this.socket.emit('leave_sync', { room: this.room });
        this.room = newRoom;
        this.socket.emit('join_sync', { room: this.room });
      } else {
        this.room = newRoom;
      }
      this.saveSettings();
      console.log(`Room changed to: ${newRoom}`);
    }
  }

  // グローバルインスタンスを作成
  const wsSync = new WebSocketSync();

  // DOMContentLoadedで自動接続（同期が有効な場合）
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (wsSync.syncEnabled) {
        wsSync.connect();
      }
    });
  } else {
    if (wsSync.syncEnabled) {
      wsSync.connect();
    }
  }

  // グローバルに公開
  window.WebSocketSync = wsSync;
})();
