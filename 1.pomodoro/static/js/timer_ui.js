// 最低限のUI連携（タイマー本体ロジックは後で分離）
document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn')
  const resetBtn = document.getElementById('resetBtn')
  const timeLabel = document.querySelector('.time-label')
  const ring = document.querySelector('.ring')

  const FULL_SECONDS = 25 * 60
  let remaining = FULL_SECONDS
  let timerId = null

  function formatTime(sec){
    const m = String(Math.floor(sec/60)).padStart(2,'0')
    const s = String(sec%60).padStart(2,'0')
    return `${m}:${s}`
  }

  // 最低限のUI連携（タイマー本体ロジックは別モジュール）
  document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn')
    const resetBtn = document.getElementById('resetBtn')
    const timeLabel = document.querySelector('.time-label')
    const ring = document.querySelector('.ring')

    const FULL_SECONDS = 25 * 60

    // TimerLogic is provided by timer_logic.js (exposed as window.TimerLogic in browser)
    const TimerCtor = window.TimerLogic
    const timer = new TimerCtor(FULL_SECONDS, { now: () => Date.now() })

    function formatTime(sec){
      const m = String(Math.floor(sec/60)).padStart(2,'0')
      const s = String(sec%60).padStart(2,'0')
      return `${m}:${s}`
    }

    function updateUI(){
      const remSec = Math.max(0, timer.remainingSecRounded())
      timeLabel.textContent = formatTime(remSec)
      const circumference = 2 * Math.PI * 52
      const progress = 1 - (remSec / FULL_SECONDS)
      const offset = circumference * (1 - progress)
      ring.style.strokeDashoffset = offset
    }

    // periodic UI update
    setInterval(updateUI, 250)

    startBtn.addEventListener('click', ()=>{
      if(timer.isRunning()){
        timer.pause()
        startBtn.textContent = '開始'
      } else {
        if(timer.remainingSecRounded() <= 0) timer.reset()
        timer.start()
        startBtn.textContent = '一時停止'
      }
      updateUI()
    })

    resetBtn.addEventListener('click', ()=>{
      timer.reset()
      startBtn.textContent = '開始'
      updateUI()
    })

    // 初期設定
    const circumference = 2 * Math.PI * 52
    ring.style.strokeDasharray = `${circumference}`
    ring.style.strokeDashoffset = `${circumference}`
    updateUI()
  })
