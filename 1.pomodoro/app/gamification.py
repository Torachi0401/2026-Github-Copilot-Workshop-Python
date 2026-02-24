"""ゲーミフィケーション機能のロジック"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List


# XPとレベルの設定
XP_PER_POMODORO = 10  # 1ポモドーロあたりのXP
XP_FOR_LEVEL = lambda level: 100 + (level - 1) * 50  # レベルアップに必要なXP


def calculate_level_and_xp(total_xp: int) -> Dict:
    """総XPからレベルと現在レベルでのXPを計算"""
    level = 1
    remaining_xp = total_xp
    
    while True:
        xp_needed = XP_FOR_LEVEL(level)
        if remaining_xp < xp_needed:
            break
        remaining_xp -= xp_needed
        level += 1
    
    xp_needed_for_next = XP_FOR_LEVEL(level)
    return {
        'level': level,
        'current_xp': remaining_xp,
        'xp_needed_for_next_level': xp_needed_for_next,
        'total_xp': total_xp
    }


def check_achievements(store: List[Dict]) -> List[Dict]:
    """達成したバッジをチェック"""
    achievements = []
    completed = [r for r in store if r['status'] == 'completed']
    
    if not completed:
        return achievements
    
    # 今日の完了数
    today = datetime.now(timezone.utc).date()
    today_completed = [r for r in completed if _is_same_date(r.get('end_time'), today)]
    
    # 今週の完了数
    week_completed = [r for r in completed if _is_in_current_week(r.get('end_time'))]
    
    # ストリーク計算
    streak = calculate_streak(completed)
    
    # バッジ判定
    badges = []
    
    # 今週10回完了
    if len(week_completed) >= 10:
        badges.append({
            'id': 'weekly_10',
            'name': '今週10回完了',
            'description': '今週10回のポモドーロを完了しました',
            'icon': '🏆',
            'unlocked_at': datetime.now(timezone.utc).isoformat()
        })
    
    # 3日連続
    if streak >= 3:
        badges.append({
            'id': 'streak_3',
            'name': '3日連続',
            'description': '3日連続でポモドーロを完了しました',
            'icon': '🔥',
            'unlocked_at': datetime.now(timezone.utc).isoformat()
        })
    
    # 7日連続
    if streak >= 7:
        badges.append({
            'id': 'streak_7',
            'name': '7日連続',
            'description': '1週間連続でポモドーロを完了しました',
            'icon': '⭐',
            'unlocked_at': datetime.now(timezone.utc).isoformat()
        })
    
    # 初回完了
    if len(completed) >= 1:
        badges.append({
            'id': 'first_pomodoro',
            'name': '初めてのポモドーロ',
            'description': '最初のポモドーロを完了しました',
            'icon': '🌱',
            'unlocked_at': completed[0].get('end_time')
        })
    
    # 50回完了
    if len(completed) >= 50:
        badges.append({
            'id': 'total_50',
            'name': '50回完了',
            'description': '合計50回のポモドーロを完了しました',
            'icon': '💯',
            'unlocked_at': datetime.now(timezone.utc).isoformat()
        })
    
    return badges


def calculate_streak(completed_records: List[Dict]) -> int:
    """連続日数を計算"""
    if not completed_records:
        return 0
    
    # end_timeでソート
    sorted_records = sorted(
        [r for r in completed_records if r.get('end_time')],
        key=lambda x: x['end_time'],
        reverse=True
    )
    
    if not sorted_records:
        return 0
    
    # 日付のセットを作成
    dates = set()
    for rec in sorted_records:
        try:
            dt = datetime.fromisoformat(rec['end_time'])
            dates.add(dt.date())
        except Exception:
            continue
    
    if not dates:
        return 0
    
    # 今日から逆算して連続日数を計算
    today = datetime.now(timezone.utc).date()
    streak = 0
    current_date = today
    
    # 今日の完了がない場合は昨日からチェック
    if today not in dates:
        current_date = today - timedelta(days=1)
    
    while current_date in dates:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak


def get_weekly_stats(store: List[Dict]) -> Dict:
    """週間統計を取得"""
    completed = [r for r in store if r['status'] == 'completed' and _is_in_current_week(r.get('end_time'))]
    
    total_count = len(completed)
    total_focus = sum((r.get('duration_sec') or 0) for r in completed)
    avg_focus = total_focus // total_count if total_count > 0 else 0
    
    # 日別の完了数
    daily_counts = {}
    for i in range(7):
        date = (datetime.now(timezone.utc) - timedelta(days=6-i)).date()
        day_completed = [r for r in completed if _is_same_date(r.get('end_time'), date)]
        daily_counts[date.isoformat()] = len(day_completed)
    
    return {
        'total_completed': total_count,
        'total_focus_seconds': total_focus,
        'average_focus_seconds': avg_focus,
        'daily_counts': daily_counts
    }


def get_monthly_stats(store: List[Dict]) -> Dict:
    """月間統計を取得"""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    completed = [r for r in store 
                 if r['status'] == 'completed' and _is_after_date(r.get('end_time'), month_start)]
    
    total_count = len(completed)
    total_focus = sum((r.get('duration_sec') or 0) for r in completed)
    avg_focus = total_focus // total_count if total_count > 0 else 0
    
    # 週別の完了数（最大5週）
    weekly_counts = {}
    for week in range(5):
        week_start = month_start + timedelta(weeks=week)
        week_end = week_start + timedelta(weeks=1)
        week_completed = [r for r in completed 
                         if _is_in_date_range(r.get('end_time'), week_start, week_end)]
        weekly_counts[f'week_{week+1}'] = len(week_completed)
    
    return {
        'total_completed': total_count,
        'total_focus_seconds': total_focus,
        'average_focus_seconds': avg_focus,
        'weekly_counts': weekly_counts,
        'completion_rate': round(total_count / 30, 2) if total_count > 0 else 0  # 1日1回を目標と仮定
    }


def _is_same_date(iso_string: str, target_date) -> bool:
    """ISO文字列の日付が指定日付と同じかチェック"""
    if not iso_string:
        return False
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.date() == target_date
    except Exception:
        return False


def _is_in_current_week(iso_string: str) -> bool:
    """ISO文字列の日付が過去7日間かチェック"""
    if not iso_string:
        return False
    try:
        dt = datetime.fromisoformat(iso_string)
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=6)
        seven_days_ago = seven_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt >= seven_days_ago
    except Exception:
        return False


def _is_after_date(iso_string: str, target_datetime) -> bool:
    """ISO文字列の日時が指定日時より後かチェック"""
    if not iso_string:
        return False
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt >= target_datetime
    except Exception:
        return False


def _is_in_date_range(iso_string: str, start_datetime, end_datetime) -> bool:
    """ISO文字列の日時が指定範囲内かチェック"""
    if not iso_string:
        return False
    try:
        dt = datetime.fromisoformat(iso_string)
        return start_datetime <= dt < end_datetime
    except Exception:
        return False
