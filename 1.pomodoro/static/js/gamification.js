// ゲーミフィケーション機能のUI制御

class GamificationUI {
  constructor() {
    this.levelNum = document.getElementById('levelNum');
    this.xpBar = document.getElementById('xpBar');
    this.xpText = document.getElementById('xpText');
    this.streakText = document.getElementById('streakText');
    this.achievementsGrid = document.getElementById('achievementsGrid');
    this.weeklyCompleted = document.getElementById('weeklyCompleted');
    this.weeklyAvgTime = document.getElementById('weeklyAvgTime');
    this.levelUpNotification = document.getElementById('levelUpNotification');
    this.levelUpLevel = document.getElementById('levelUpLevel');
    this.weeklyChart = document.getElementById('weeklyChart');
    
    // 定数
    this.dayNames = ['日', '月', '火', '水', '木', '金', '土'];
    
    this.init();
  }
  
  async init() {
    await this.loadGamificationStats();
    await this.loadAchievements();
    await this.loadWeeklyStats();
    
    // 定期更新（30秒ごと）
    setInterval(() => {
      this.loadGamificationStats();
      this.loadAchievements();
      this.loadWeeklyStats();
    }, 30000);
  }
  
  async loadGamificationStats() {
    try {
      const response = await fetch('/api/gamification/stats');
      if (!response.ok) return;
      
      const data = await response.json();
      this.updateLevelDisplay(data);
      this.updateStreakDisplay(data.streak_days);
    } catch (error) {
      console.error('Failed to load gamification stats:', error);
    }
  }
  
  updateLevelDisplay(data) {
    this.levelNum.textContent = data.level;
    
    const xpPercent = (data.current_xp / data.xp_needed_for_next_level) * 100;
    this.xpBar.style.width = `${xpPercent}%`;
    
    this.xpText.textContent = `${data.current_xp} / ${data.xp_needed_for_next_level} XP`;
  }
  
  updateStreakDisplay(streakDays) {
    this.streakText.textContent = `${streakDays}日連続`;
  }
  
  async loadAchievements() {
    try {
      const response = await fetch('/api/gamification/achievements');
      if (!response.ok) return;
      
      const data = await response.json();
      this.renderAchievements(data.achievements);
    } catch (error) {
      console.error('Failed to load achievements:', error);
    }
  }
  
  renderAchievements(achievements) {
    if (achievements.length === 0) {
      this.achievementsGrid.innerHTML = '<div class="achievement-placeholder">バッジを獲得しよう！</div>';
      return;
    }
    
    this.achievementsGrid.innerHTML = achievements.map(badge => `
      <div class="achievement-badge" title="${badge.description}">
        <div class="badge-icon">${badge.icon}</div>
        <div class="badge-name">${badge.name}</div>
      </div>
    `).join('');
  }
  
  async loadWeeklyStats() {
    try {
      const response = await fetch('/api/gamification/weekly-stats');
      if (!response.ok) return;
      
      const data = await response.json();
      this.updateWeeklyStats(data);
      this.renderWeeklyChart(data);
    } catch (error) {
      console.error('Failed to load weekly stats:', error);
    }
  }
  
  updateWeeklyStats(data) {
    this.weeklyCompleted.textContent = data.total_completed;
    
    const avgMinutes = Math.round(data.average_focus_seconds / 60);
    this.weeklyAvgTime.textContent = `${avgMinutes}分`;
  }
  
  renderWeeklyChart(data) {
    const ctx = this.weeklyChart.getContext('2d');
    const dailyCounts = data.daily_counts;
    const dates = Object.keys(dailyCounts).sort();
    const counts = dates.map(date => dailyCounts[date]);
    
    // シンプルな棒グラフを描画
    const width = this.weeklyChart.width;
    const height = this.weeklyChart.height;
    const barWidth = width / dates.length;
    const maxCount = Math.max(...counts, 1);
    const scale = (height - 40) / maxCount;
    
    // クリア
    ctx.clearRect(0, 0, width, height);
    
    // グリッド線
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = (height - 20) - (i * (height - 40) / 5);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    // 棒グラフ
    counts.forEach((count, index) => {
      const x = index * barWidth;
      const barHeight = count * scale;
      const y = height - 20 - barHeight;
      
      // グラデーション
      const gradient = ctx.createLinearGradient(0, y, 0, height - 20);
      gradient.addColorStop(0, '#4CAF50');
      gradient.addColorStop(1, '#81C784');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x + barWidth * 0.1, y, barWidth * 0.8, barHeight);
      
      // 日付ラベル（曜日のみ）
      const date = new Date(dates[index]);
      const dayLabel = this.dayNames[date.getDay()];
      
      ctx.fillStyle = '#666';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(dayLabel, x + barWidth / 2, height - 5);
      
      // カウント表示
      if (count > 0) {
        ctx.fillStyle = '#333';
        ctx.font = 'bold 14px sans-serif';
        ctx.fillText(count, x + barWidth / 2, y - 5);
      }
    });
  }
  
  showLevelUpNotification(level) {
    this.levelUpLevel.textContent = `レベル ${level}`;
    this.levelUpNotification.classList.add('show');
    
    setTimeout(() => {
      this.levelUpNotification.classList.remove('show');
    }, 3000);
  }
  
  // ポモドーロ完了時に呼ばれる
  onPomodoroComplete(completeData) {
    if (completeData.level_up) {
      this.showLevelUpNotification(completeData.level);
    }
    
    // 即座に更新
    this.loadGamificationStats();
    this.loadAchievements();
    this.loadWeeklyStats();
  }
}

// グローバルインスタンスを作成
window.gamificationUI = null;
document.addEventListener('DOMContentLoaded', () => {
  window.gamificationUI = new GamificationUI();
});
