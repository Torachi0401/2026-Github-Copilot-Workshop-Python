// 設定管理モジュール
class Settings {
  constructor() {
    // デフォルト設定
    this.defaults = {
      workDuration: 25, // 分
      breakDuration: 5, // 分
      theme: 'light', // light, dark, focus
      sounds: {
        start: true,
        end: true,
        tick: false
      }
    };
    
    this.load();
  }
  
  // ローカルストレージから設定を読み込み
  load() {
    try {
      const stored = localStorage.getItem('pomodoroSettings');
      if (stored) {
        this.settings = { ...this.defaults, ...JSON.parse(stored) };
        // soundsオブジェクトをマージ
        if (this.settings.sounds) {
          this.settings.sounds = { ...this.defaults.sounds, ...this.settings.sounds };
        }
      } else {
        this.settings = { ...this.defaults };
      }
    } catch (e) {
      console.error('設定の読み込みに失敗しました:', e);
      this.settings = { ...this.defaults };
    }
  }
  
  // ローカルストレージに設定を保存
  save() {
    try {
      localStorage.setItem('pomodoroSettings', JSON.stringify(this.settings));
    } catch (e) {
      console.error('設定の保存に失敗しました:', e);
    }
  }
  
  // 設定値の取得
  get(key) {
    return this.settings[key];
  }
  
  // 設定値の更新
  set(key, value) {
    this.settings[key] = value;
    this.save();
    return this.settings[key];
  }
  
  // サウンド設定の取得
  getSound(type) {
    return this.settings.sounds[type];
  }
  
  // サウンド設定の更新
  setSound(type, enabled) {
    this.settings.sounds[type] = enabled;
    this.save();
  }
  
  // すべての設定を取得
  getAll() {
    return { ...this.settings };
  }
  
  // 設定をリセット
  reset() {
    this.settings = { ...this.defaults };
    this.save();
  }
}

// browser global
if (typeof window !== 'undefined') {
  window.Settings = Settings;
}

// Node/CommonJS export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Settings;
}
