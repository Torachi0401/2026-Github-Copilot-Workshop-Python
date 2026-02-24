// Pure timer logic module. Works with injected clock for testability.
class TimerLogic {
  constructor(durationSec, options = {}) {
    this.initialDuration = Math.max(0, Math.floor(durationSec));
    this.now = options.now || (() => Date.now()); // ms
    this._running = false
    this._startTs = null
    this._accumulatedMs = 0
  }

  start() {
    if (this._running) return
    this._startTs = this.now()
    this._running = true
  }

  pause() {
    if (!this._running) return
    const elapsed = this.now() - this._startTs
    this._accumulatedMs += elapsed
    this._startTs = null
    this._running = false
  }

  resume() {
    if (this._running) return
    this._startTs = this.now()
    this._running = true
  }

  reset() {
    this._running = false
    this._startTs = null
    this._accumulatedMs = 0
  }

  isRunning() { return this._running }

  // remaining seconds (float) based on current time
  remainingMs() {
    let acc = this._accumulatedMs
    if (this._running && this._startTs !== null) {
      acc += (this.now() - this._startTs)
    }
    const rem = Math.max(0, this.initialDuration * 1000 - acc)
    return rem
  }

  remainingSecRounded() {
    return Math.ceil(this.remainingMs() / 1000)
  }
}

// Node/CommonJS export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TimerLogic
} else {
  // browser global
  window.TimerLogic = TimerLogic
}
