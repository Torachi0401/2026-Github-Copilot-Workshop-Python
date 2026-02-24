// 同期キュー管理モジュール
// オフライン時のAPI呼び出しを localStorage に保存し、
// 接続復帰時にサーバへ再送する

class SyncQueue {
  constructor() {
    this.QUEUE_KEY = 'pomodoro_sync_queue';
    this.MAX_RETRIES = 5;
    this.BASE_DELAY = 1000; // 1秒
    this.isOnline = navigator.onLine;
    this.isProcessing = false;
    
    this.setupOnlineListener();
    
    // ページロード時にキューを処理
    if (this.isOnline) {
      this.processQueue();
    }
  }
  
  setupOnlineListener() {
    window.addEventListener('online', () => {
      console.log('Connection restored - processing sync queue');
      this.isOnline = true;
      this.processQueue();
    });
    
    window.addEventListener('offline', () => {
      console.log('Connection lost - queueing requests');
      this.isOnline = false;
    });
  }
  
  // キューにリクエストを追加
  enqueue(url, options, metadata = {}) {
    const queue = this.getQueue();
    const request = {
      id: this.generateId(),
      url,
      options,
      metadata,
      timestamp: Date.now(),
      retries: 0
    };
    
    queue.push(request);
    this.saveQueue(queue);
    
    console.log(`Request queued: ${url}`, request);
    return request.id;
  }
  
  // localStorage からキューを取得
  getQueue() {
    try {
      const queueData = localStorage.getItem(this.QUEUE_KEY);
      return queueData ? JSON.parse(queueData) : [];
    } catch (error) {
      console.error('Failed to load sync queue:', error);
      return [];
    }
  }
  
  // localStorage にキューを保存
  saveQueue(queue) {
    try {
      localStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }
  
  // キューからアイテムを削除
  removeFromQueue(requestId) {
    const queue = this.getQueue();
    const filtered = queue.filter(item => item.id !== requestId);
    this.saveQueue(filtered);
  }
  
  // キューを処理
  async processQueue() {
    if (this.isProcessing || !this.isOnline) {
      return;
    }
    
    this.isProcessing = true;
    const queue = this.getQueue();
    
    if (queue.length === 0) {
      this.isProcessing = false;
      return;
    }
    
    console.log(`Processing sync queue: ${queue.length} items`);
    
    for (const request of [...queue]) {
      try {
        await this.processRequest(request);
        this.removeFromQueue(request.id);
        console.log(`Request synced successfully: ${request.url}`);
      } catch (error) {
        console.error(`Failed to process request: ${request.url}`, error);
        await this.handleRetry(request);
      }
    }
    
    this.isProcessing = false;
  }
  
  // 個別のリクエストを処理
  async processRequest(request) {
    const response = await fetch(request.url, request.options);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
  
  // 再試行処理
  async handleRetry(request) {
    request.retries++;
    
    if (request.retries >= this.MAX_RETRIES) {
      console.error(`Max retries reached for request: ${request.url}`);
      this.removeFromQueue(request.id);
      return;
    }
    
    // 指数バックオフ: 1秒, 2秒, 4秒, 8秒, 16秒
    const delay = this.BASE_DELAY * Math.pow(2, request.retries - 1);
    console.log(`Retrying in ${delay}ms (attempt ${request.retries}/${this.MAX_RETRIES})`);
    
    // キューを更新
    const queue = this.getQueue();
    const index = queue.findIndex(item => item.id === request.id);
    if (index !== -1) {
      queue[index] = request;
      this.saveQueue(queue);
    }
    
    // 指数バックオフで待機後、再試行
    setTimeout(() => {
      if (this.isOnline && !this.isProcessing) {
        this.processQueue();
      }
    }, delay);
  }
  
  // API呼び出しラッパー
  async fetch(url, options = {}) {
    // オンラインの場合は通常通り送信
    if (this.isOnline) {
      try {
        const response = await window.fetch(url, options);
        return response;
      } catch (error) {
        // ネットワークエラーの場合はキューに追加
        console.warn('Network error - queueing request:', error);
        this.enqueue(url, options);
        throw error;
      }
    }
    
    // オフラインの場合はキューに追加
    console.log('Offline - queueing request');
    this.enqueue(url, options);
    
    // オフライン用のダミーレスポンスを返す
    return {
      ok: true,
      status: 202, // Accepted
      json: async () => ({ queued: true })
    };
  }
  
  // ユニークIDを生成
  generateId() {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }
  
  // キューの状態を取得
  getQueueStatus() {
    const queue = this.getQueue();
    return {
      count: queue.length,
      items: queue
    };
  }
  
  // キューをクリア（デバッグ用）
  clearQueue() {
    localStorage.removeItem(this.QUEUE_KEY);
    console.log('Sync queue cleared');
  }
}

// グローバルインスタンスを作成（ブラウザ環境のみ）
if (typeof window !== 'undefined') {
  window.syncQueue = new SyncQueue();
}

// Node.js環境用のエクスポート（テスト用）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SyncQueue };
}
