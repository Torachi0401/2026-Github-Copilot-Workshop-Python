// sync_queue.js のテスト

const { SyncQueue } = require('./sync_queue.js');

// localStorage のモック
class LocalStorageMock {
  constructor() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key] || null;
  }

  setItem(key, value) {
    this.store[key] = value;
  }

  removeItem(key) {
    delete this.store[key];
  }

  clear() {
    this.store = {};
  }
}

// グローバルオブジェクトのモック
global.localStorage = new LocalStorageMock();
global.navigator = { onLine: true };
global.window = {
  addEventListener: jest.fn()
};
global.fetch = jest.fn();

describe('SyncQueue', () => {
  let syncQueue;

  beforeEach(() => {
    localStorage.clear();
    global.fetch.mockClear();
    global.window.addEventListener.mockClear();
    syncQueue = new SyncQueue();
  });

  test('初期化時にオンラインリスナーを設定する', () => {
    expect(window.addEventListener).toHaveBeenCalledWith('online', expect.any(Function));
    expect(window.addEventListener).toHaveBeenCalledWith('offline', expect.any(Function));
  });

  test('リクエストをキューに追加できる', () => {
    const url = '/api/test';
    const options = { method: 'POST', body: JSON.stringify({ test: true }) };
    
    const requestId = syncQueue.enqueue(url, options);
    
    expect(requestId).toBeDefined();
    const queue = syncQueue.getQueue();
    expect(queue).toHaveLength(1);
    expect(queue[0].url).toBe(url);
    expect(queue[0].options).toEqual(options);
  });

  test('キューからアイテムを削除できる', () => {
    const requestId = syncQueue.enqueue('/api/test', {});
    
    syncQueue.removeFromQueue(requestId);
    
    const queue = syncQueue.getQueue();
    expect(queue).toHaveLength(0);
  });

  test('キューの状態を取得できる', () => {
    syncQueue.enqueue('/api/test1', {});
    syncQueue.enqueue('/api/test2', {});
    
    const status = syncQueue.getQueueStatus();
    
    expect(status.count).toBe(2);
    expect(status.items).toHaveLength(2);
  });

  test('キューをクリアできる', () => {
    syncQueue.enqueue('/api/test', {});
    
    syncQueue.clearQueue();
    
    const queue = syncQueue.getQueue();
    expect(queue).toHaveLength(0);
  });

  test('ユニークIDを生成できる', () => {
    const id1 = syncQueue.generateId();
    const id2 = syncQueue.generateId();
    
    expect(id1).not.toBe(id2);
    expect(id1).toMatch(/^\d+-[a-z0-9]+$/);
  });

  test('オンライン時はfetchを直接呼び出す', async () => {
    syncQueue.isOnline = true;
    global.fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ success: true })
    });
    
    const response = await syncQueue.fetch('/api/test', { method: 'POST' });
    
    expect(global.fetch).toHaveBeenCalledWith('/api/test', { method: 'POST' });
    expect(response.ok).toBe(true);
  });

  test('オフライン時はリクエストをキューに追加する', async () => {
    syncQueue.isOnline = false;
    
    const response = await syncQueue.fetch('/api/test', { method: 'POST' });
    
    expect(response.status).toBe(202);
    const data = await response.json();
    expect(data.queued).toBe(true);
    
    const queue = syncQueue.getQueue();
    expect(queue).toHaveLength(1);
  });

  test('processRequestが成功するとJSONを返す', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({ result: 'success' })
    };
    global.fetch.mockResolvedValue(mockResponse);
    
    const request = {
      id: 'test-id',
      url: '/api/test',
      options: { method: 'POST' }
    };
    
    const result = await syncQueue.processRequest(request);
    
    expect(result).toEqual({ result: 'success' });
  });

  test('processRequestがHTTPエラーの場合は例外を投げる', async () => {
    const mockResponse = {
      ok: false,
      status: 500
    };
    global.fetch.mockResolvedValue(mockResponse);
    
    const request = {
      id: 'test-id',
      url: '/api/test',
      options: { method: 'POST' }
    };
    
    await expect(syncQueue.processRequest(request)).rejects.toThrow('HTTP error! status: 500');
  });
});
