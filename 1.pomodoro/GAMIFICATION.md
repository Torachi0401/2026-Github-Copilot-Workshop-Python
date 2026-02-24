# ゲーミフィケーション機能ドキュメント

## 概要

ポモドーロタイマーにゲーミフィケーション要素を追加し、ユーザーのモチベーション維持と継続利用を促進します。

## 実装された機能

### 1. 経験値（XP）システム

- **XP付与**: ポモドーロを完了するごとに10 XPを獲得
- **レベルアップ**: 蓄積したXPに応じてレベルが上昇
  - レベル1→2: 100 XP必要
  - レベル2→3: 150 XP必要
  - 以降、50 XPずつ増加 (レベルn→n+1: 100 + (n-1) * 50 XP)

### 2. バッジシステム

実装されたバッジ：

| バッジ名 | アイコン | 獲得条件 | 説明 |
|---------|---------|---------|------|
| 初めてのポモドーロ | 🌱 | 最初のポモドーロを完了 | ポモドーロタイマーを初めて使用 |
| 今週10回完了 | 🏆 | 今週10回のポモドーロを完了 | 週間での継続的な利用 |
| 3日連続 | 🔥 | 3日連続でポモドーロを完了 | 継続的な習慣化 |
| 7日連続 | ⭐ | 7日連続でポモドーロを完了 | 1週間の継続達成 |
| 50回完了 | 💯 | 合計50回のポモドーロを完了 | 長期的な利用達成 |

### 3. ストリーク表示

- 連続して完了した日数を表示
- 炎のアイコン（🔥）とともに表示
- 連続が途切れると0にリセット

### 4. 統計機能

#### 週間統計
- 過去7日間の完了数
- 日別完了数の棒グラフ
- 平均集中時間

#### 月間統計
- 当月の完了数
- 週別の完了数
- 完了率（1日1回を基準）

## API エンドポイント

### ゲーミフィケーション統計取得

```
GET /api/gamification/stats
```

**レスポンス例:**
```json
{
  "level": 2,
  "current_xp": 50,
  "xp_needed_for_next_level": 150,
  "total_xp": 250,
  "streak_days": 5
}
```

### バッジ一覧取得

```
GET /api/gamification/achievements
```

**レスポンス例:**
```json
{
  "achievements": [
    {
      "id": "first_pomodoro",
      "name": "初めてのポモドーロ",
      "description": "最初のポモドーロを完了しました",
      "icon": "🌱",
      "unlocked_at": "2026-02-24T06:30:00.000000+00:00"
    }
  ],
  "total_count": 1
}
```

### 週間統計取得

```
GET /api/gamification/weekly-stats
```

**レスポンス例:**
```json
{
  "total_completed": 10,
  "total_focus_seconds": 15000,
  "average_focus_seconds": 1500,
  "daily_counts": {
    "2026-02-18": 1,
    "2026-02-19": 2,
    "2026-02-20": 1,
    "2026-02-21": 3,
    "2026-02-22": 1,
    "2026-02-23": 2,
    "2026-02-24": 0
  }
}
```

### 月間統計取得

```
GET /api/gamification/monthly-stats
```

**レスポンス例:**
```json
{
  "total_completed": 45,
  "total_focus_seconds": 67500,
  "average_focus_seconds": 1500,
  "weekly_counts": {
    "week_1": 8,
    "week_2": 12,
    "week_3": 15,
    "week_4": 10,
    "week_5": 0
  },
  "completion_rate": 1.5
}
```

### ポモドーロ完了（更新版）

```
POST /api/complete
```

**リクエスト:**
```json
{
  "id": 1
}
```

**レスポンス例:**
```json
{
  "ok": true,
  "xp_gained": 10,
  "total_xp": 110,
  "level": 2,
  "level_up": true
}
```

レベルアップが発生した場合、`level_up` が `true` になります。

## フロントエンド実装

### UI コンポーネント

1. **レベルとXP表示**
   - レベル番号
   - プログレスバー（次のレベルまでの進捗）
   - XPテキスト表示

2. **ストリーク表示**
   - 炎アイコンと連続日数

3. **バッジグリッド**
   - 獲得したバッジを表示
   - ホバー時に説明を表示

4. **週間統計グラフ**
   - Canvasで描画した棒グラフ
   - 過去7日間の日別完了数

5. **レベルアップ通知**
   - レベルアップ時にアニメーション付き通知を表示
   - 3秒後に自動で消える

### JavaScript API

`GamificationUI` クラスが提供するメソッド：

```javascript
// ゲーミフィケーション統計を読み込み
await loadGamificationStats()

// バッジを読み込み
await loadAchievements()

// 週間統計を読み込み
await loadWeeklyStats()

// レベルアップ通知を表示
showLevelUpNotification(level)

// ポモドーロ完了時の処理
onPomodoroComplete(completeData)
```

## テスト

実装されたテスト：

- `test_complete_gives_xp`: XP付与のテスト
- `test_level_up`: レベルアップのテスト
- `test_gamification_stats`: 統計APIのテスト
- `test_achievements`: バッジ獲得のテスト
- `test_streak_calculation`: ストリーク計算のテスト
- `test_weekly_stats`: 週間統計のテスト
- `test_monthly_stats`: 月間統計のテスト
- `test_weekly_10_badge`: 週間10回完了バッジのテスト

すべてのテストをpytestで実行：
```bash
python -m pytest tests/test_gamification.py -v
```

## 今後の拡張案

1. **追加バッジ**
   - 30日連続達成
   - 合計100回完了
   - 早朝完了（6時前）
   - 深夜完了（22時以降）

2. **ソーシャル機能**
   - フレンドとのランキング比較
   - バッジ共有機能

3. **カスタマイズ**
   - アバター選択
   - テーマカラー変更
   - XP倍率イベント

4. **リワード**
   - レベルアップ時の特典
   - バッジコンプリート報酬

## 注意事項

- 現在はメモリ内ストレージを使用しているため、サーバー再起動でデータが消失します
- 本番環境ではデータベース（SQLite/PostgreSQL）への移行が推奨されます
- ストリーク計算はUTCタイムゾーンで行われます

---

作成日: 2026-02-24
