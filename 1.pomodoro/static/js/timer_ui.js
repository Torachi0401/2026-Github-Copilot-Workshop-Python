// 最低限のUI連携（タイマー本体ロジックは後で分離）
document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn')
  const resetBtn = document.getElementById('resetBtn')
  const timeLabel = document.querySelector('.time-label')
  const ring = document.querySelector('.ring')
  const particleContainer = document.getElementById('particleContainer')
  const rippleContainer = document.getElementById('rippleContainer')

  const FULL_SECONDS = 25 * 60
  const CIRCUMFERENCE = 2 * Math.PI * 52
  let particles = []

  // TimerLogic is provided by timer_logic.js (exposed as window.TimerLogic in browser)
  const TimerCtor = window.TimerLogic
  const timer = new TimerCtor(FULL_SECONDS, { now: () => Date.now() })

  function formatTime(sec){
    const m = String(Math.floor(sec/60)).padStart(2,'0')
    const s = String(sec%60).padStart(2,'0')
    return `${m}:${s}`
  }

  // Create particles for background effect
  function createParticle() {
    const particle = document.createElement('div')
    particle.className = 'particle'
    const size = Math.random() * 4 + 2
    particle.style.width = `${size}px`
    particle.style.height = `${size}px`
    particle.style.left = `${Math.random() * 100}%`
    particle.style.bottom = '0'
    particle.style.animationDuration = `${Math.random() * 10 + 10}s`
    particle.style.animationDelay = `${Math.random() * 5}s`
    particleContainer.appendChild(particle)
    particles.push(particle)
    
    // Remove particle after animation
    setTimeout(() => {
      if (particle.parentNode) {
        particle.parentNode.removeChild(particle)
      }
      particles = particles.filter(p => p !== particle)
    }, 20000)
  }

  // Initialize particles
  function initParticles() {
    for (let i = 0; i < 20; i++) {
      createParticle()
    }
  }

  // Get color based on progress (0-1)
  function getProgressColor(progress) {
    // progress: 1 (start) -> 0 (end)
    // blue (start) -> yellow (middle) -> red (end)
    if (progress > 0.5) {
      // Blue to Yellow
      const t = (progress - 0.5) * 2 // 0-1
      return interpolateColor('#4a90e2', '#f5d142', 1 - t)
    } else {
      // Yellow to Red
      const t = progress * 2 // 0-1
      return interpolateColor('#f5d142', '#e74c3c', 1 - t)
    }
  }

  // Interpolate between two hex colors
  function interpolateColor(color1, color2, factor) {
    const c1 = hexToRgb(color1)
    const c2 = hexToRgb(color2)
    const r = Math.round(c1.r + factor * (c2.r - c1.r))
    const g = Math.round(c1.g + factor * (c2.g - c1.g))
    const b = Math.round(c1.b + factor * (c2.b - c1.b))
    return `rgb(${r}, ${g}, ${b})`
  }

  // Convert hex to RGB
  function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  function updateUI(){
    const remSec = Math.max(0, timer.remainingSecRounded())
    timeLabel.textContent = formatTime(remSec)
    const progress = Math.max(0, remSec / FULL_SECONDS)
    const offset = CIRCUMFERENCE * (1 - progress)
    ring.style.strokeDashoffset = offset
    
    // Update ring color based on progress
    const color = getProgressColor(progress)
    ring.style.stroke = color
  }

  // periodic UI update
  setInterval(updateUI, 250)

  startBtn.addEventListener('click', ()=>{
    if(timer.isRunning()){
      timer.pause()
      startBtn.textContent = '開始'
      // Disable visual effects
      particleContainer.classList.remove('active')
      rippleContainer.style.display = 'none'
    } else {
      if(timer.remainingSecRounded() <= 0) timer.reset()
      timer.start()
      startBtn.textContent = '一時停止'
      // Enable visual effects
      particleContainer.classList.add('active')
      rippleContainer.style.display = 'block'
      initParticles()
    }
    updateUI()
  })

  resetBtn.addEventListener('click', ()=>{
    timer.reset()
    startBtn.textContent = '開始'
    // Disable visual effects
    particleContainer.classList.remove('active')
    rippleContainer.style.display = 'none'
    // Clear all particles more thoroughly
    while (particleContainer.firstChild) {
      particleContainer.removeChild(particleContainer.firstChild)
    }
    particles = []
    updateUI()
  })

  // 初期設定
  ring.style.strokeDasharray = `${CIRCUMFERENCE}`
  ring.style.strokeDashoffset = `${CIRCUMFERENCE}`
  rippleContainer.style.display = 'none'
  updateUI()
})