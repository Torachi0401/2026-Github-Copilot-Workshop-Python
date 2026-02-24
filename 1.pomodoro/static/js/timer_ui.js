// 最低限のUI連携（タイマー本体ロジックは別モジュール）
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

  const FULL_SECONDS = 25 * 60

  // TimerLogic is provided by timer_logic.js (exposed as window.TimerLogic in browser)
  const TimerCtor = window.TimerLogic
  const timer = new TimerCtor(FULL_SECONDS, { now: () => Date.now() })

  let currentPomodoroId = null

  function formatTime(sec){
    const m = String(Math.floor(sec/60)).padStart(2,'0');
    const s = String(sec%60).padStart(2,'0');
    return `${m}:${s}`;
  }

  function updateUI(){
    const remSec = Math.max(0, timer.remainingSecRounded())
    timeLabel.textContent = formatTime(remSec)
    const circumference = 2 * Math.PI * 52
    const progress = 1 - (remSec / FULL_SECONDS)
    const offset = circumference * (1 - progress)
    ring.style.strokeDashoffset = offset

    // タイマー完了チェック
    if (remSec === 0 && timer.isRunning()) {
      handlePomodoroComplete()
      timer.pause()
      startBtn.textContent = '開始'
    }
  }

  // ポモドーロ開始時のAPI呼び出し
  async function startPomodoro() {
    try {
      const response = await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'work' })
      })
      if (response.ok) {
        const data = await response.json()
        currentPomodoroId = data.id
      }
    } catch (error) {
      console.error('Failed to start pomodoro:', error)
    }
  }

  // ポモドーロ完了時のAPI呼び出し
  async function handlePomodoroComplete() {
    if (!currentPomodoroId) return

    try {
      const response = await fetch('/api/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: currentPomodoroId })
      })
      if (response.ok) {
        const data = await response.json()
        
        // ゲーミフィケーションUIに通知
        if (window.gamificationUI) {
          window.gamificationUI.onPomodoroComplete(data)
        }
        
        currentPomodoroId = null
      }
    } catch (error) {
      console.error('Failed to complete pomodoro:', error)
    }
  }

  // periodic UI update
  setInterval(updateUI, 250)

  startBtn.addEventListener('click', ()=>{
    if(timer.isRunning()){
      timer.pause()
      startBtn.textContent = '開始'
    } else {
      if(timer.remainingSecRounded() <= 0) {
        timer.reset()
      }
      timer.start()
      startBtn.textContent = '一時停止'
      
      // ポモドーロ開始時にAPI呼び出し
      if (!currentPomodoroId) {
        startPomodoro()
      }
    }
    updateUI()
  })

  resetBtn.addEventListener('click', ()=>{
    timer.reset()
    startBtn.textContent = '開始'
    currentPomodoroId = null
    updateUI()
  })

  // 初期設定
  const circumference = 2 * Math.PI * 52
  ring.style.strokeDasharray = `${circumference}`
  ring.style.strokeDashoffset = `${circumference}`
  updateUI()
})
