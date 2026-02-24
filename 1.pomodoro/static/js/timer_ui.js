// UI連携とタイマー制御
document.addEventListener('DOMContentLoaded', () => {
  // 設定管理
  const settings = new window.Settings();
  
  // UI要素の取得
  const startBtn = document.getElementById('startBtn');
  const resetBtn = document.getElementById('resetBtn');
  const timeLabel = document.querySelector('.time-label');
  const ring = document.querySelector('.ring');
  const settingsToggle = document.getElementById('settingsToggle');
  const settingsPanel = document.getElementById('settingsPanel');
  const closeSettings = document.getElementById('closeSettings');
  
  // 設定UI要素
  const workDurationButtons = document.querySelectorAll('[data-work-duration]');
  const breakDurationButtons = document.querySelectorAll('[data-break-duration]');
  const themeButtons = document.querySelectorAll('[data-theme]');
  const soundStartCheckbox = document.getElementById('soundStart');
  const soundEndCheckbox = document.getElementById('soundEnd');
  const soundTickCheckbox = document.getElementById('soundTick');

  // タイマー初期化
  let FULL_SECONDS = settings.get('workDuration') * 60;
  const TimerCtor = window.TimerLogic;
  let timer = new TimerCtor(FULL_SECONDS, { now: () => Date.now() });
  let tickInterval = null;
  
  // AudioContextを再利用
  let audioContext = null;
  function getAudioContext() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioContext;
  }

  function formatTime(sec){
    const m = String(Math.floor(sec/60)).padStart(2,'0');
    const s = String(sec%60).padStart(2,'0');
    return `${m}:${s}`;
  }

  function updateUI(){
    const remSec = Math.max(0, timer.remainingSecRounded());
    timeLabel.textContent = formatTime(remSec);
    const circumference = 2 * Math.PI * 52;
    const progress = 1 - (remSec / FULL_SECONDS);
    const offset = circumference * (1 - progress);
    ring.style.strokeDashoffset = offset;
    
    // タイマー終了チェック
    if (remSec === 0 && timer.isRunning()) {
      timer.pause();
      startBtn.textContent = '開始';
      playSound('end');
      stopTick();
    }
  }

  // サウンド再生（Web Audio APIを使用）
  function playSound(type) {
    if (!settings.getSound(type)) return;
    
    const ctx = getAudioContext();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    if (type === 'start') {
      oscillator.frequency.value = 523.25; // C5
      gainNode.gain.value = 0.3;
      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.1);
    } else if (type === 'end') {
      oscillator.frequency.value = 659.25; // E5
      gainNode.gain.value = 0.3;
      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.2);
    } else if (type === 'tick') {
      oscillator.frequency.value = 440; // A4
      gainNode.gain.value = 0.05;
      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.02);
    }
  }

  function startTick() {
    if (!settings.getSound('tick')) return;
    tickInterval = setInterval(() => {
      if (timer.isRunning()) {
        playSound('tick');
      }
    }, 1000);
  }

  function stopTick() {
    if (tickInterval) {
      clearInterval(tickInterval);
      tickInterval = null;
    }
  }

  // 定期的なUI更新
  setInterval(updateUI, 250);

  // タイマー制御
  startBtn.addEventListener('click', () => {
    if (timer.isRunning()) {
      timer.pause();
      startBtn.textContent = '開始';
      stopTick();
    } else {
      if (timer.remainingSecRounded() <= 0) {
        timer.reset();
      }
      timer.start();
      startBtn.textContent = '一時停止';
      playSound('start');
      startTick();
    }
    updateUI();
  });

  resetBtn.addEventListener('click', () => {
    timer.reset();
    startBtn.textContent = '開始';
    stopTick();
    updateUI();
  });

  // 設定パネルの表示/非表示
  settingsToggle.addEventListener('click', () => {
    settingsPanel.style.display = settingsPanel.style.display === 'none' ? 'block' : 'none';
  });

  closeSettings.addEventListener('click', () => {
    settingsPanel.style.display = 'none';
  });

  // 作業時間設定
  workDurationButtons.forEach(btn => {
    const duration = parseInt(btn.dataset.workDuration);
    if (duration === settings.get('workDuration')) {
      btn.classList.add('active');
    }
    
    btn.addEventListener('click', () => {
      // タイマー実行中の場合は変更を防ぐ
      if (timer.isRunning()) {
        alert('タイマーを停止してから作業時間を変更してください。');
        return;
      }
      
      const newDuration = parseInt(btn.dataset.workDuration);
      settings.set('workDuration', newDuration);
      FULL_SECONDS = newDuration * 60;
      
      // タイマーを再作成
      timer = new TimerCtor(FULL_SECONDS, { now: () => Date.now() });
      
      // ボタンのアクティブ状態更新
      workDurationButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      updateUI();
    });
  });

  // 休憩時間設定
  breakDurationButtons.forEach(btn => {
    const duration = parseInt(btn.dataset.breakDuration);
    if (duration === settings.get('breakDuration')) {
      btn.classList.add('active');
    }
    
    btn.addEventListener('click', () => {
      settings.set('breakDuration', parseInt(btn.dataset.breakDuration));
      
      // ボタンのアクティブ状態更新
      breakDurationButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // テーマ設定
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  themeButtons.forEach(btn => {
    const theme = btn.dataset.theme;
    if (theme === settings.get('theme')) {
      btn.classList.add('active');
    }
    
    btn.addEventListener('click', () => {
      const newTheme = btn.dataset.theme;
      settings.set('theme', newTheme);
      applyTheme(newTheme);
      
      // ボタンのアクティブ状態更新
      themeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // サウンド設定
  soundStartCheckbox.checked = settings.getSound('start');
  soundEndCheckbox.checked = settings.getSound('end');
  soundTickCheckbox.checked = settings.getSound('tick');

  soundStartCheckbox.addEventListener('change', (e) => {
    settings.setSound('start', e.target.checked);
  });

  soundEndCheckbox.addEventListener('change', (e) => {
    settings.setSound('end', e.target.checked);
  });

  soundTickCheckbox.addEventListener('change', (e) => {
    settings.setSound('tick', e.target.checked);
  });

  // 初期設定の適用
  applyTheme(settings.get('theme'));
  
  const circumference = 2 * Math.PI * 52;
  ring.style.strokeDasharray = `${circumference}`;
  ring.style.strokeDashoffset = `${circumference}`;
  updateUI();
});

