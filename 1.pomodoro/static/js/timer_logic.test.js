const TimerLogic = require('./timer_logic')

describe('TimerLogic', () => {
  test('counts down from initial duration', () => {
    let now = 1000000
    const clock = () => now
    const t = new TimerLogic(10, { now: clock })
    // start at t=1000000
    t.start()
    // advance 3.2s
    now += 3200
    expect(t.remainingSecRounded()).toBe(7)
  })

  test('pause stops progression and resume continues', () => {
    let now = 2000000
    const clock = () => now
    const t = new TimerLogic(5, { now: clock })
    t.start()
    now += 1500
    // pause
    t.pause()
    const remAfterPause = t.remainingSecRounded()
    now += 3000 // time passes while paused
    // remaining unchanged while paused
    expect(t.remainingSecRounded()).toBe(remAfterPause)
    t.resume()
    now += 1000
    expect(t.remainingSecRounded()).toBe(Math.ceil((t.initialDuration*1000 - (1500 + 1000))/1000))
  })

  test('reset restores initial duration and stops', () => {
    let now = 3000000
    const clock = () => now
    const t = new TimerLogic(3, { now: clock })
    t.start()
    now += 2000
    t.reset()
    expect(t.isRunning()).toBe(false)
    expect(t.remainingSecRounded()).toBe(3)
  })
})
