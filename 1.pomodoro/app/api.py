from flask import Blueprint, current_app, request, jsonify
from datetime import datetime, timezone, date
from .gamification import (
    calculate_level_and_xp, check_achievements, calculate_streak,
    get_weekly_stats, get_monthly_stats, XP_PER_POMODORO
)

bp = Blueprint('api', __name__)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


@bp.route('/start', methods=['POST'])
def start():
    payload = request.get_json() or {}
    ptype = payload.get('type', 'work')
    store = current_app.config['POMODORO_STORE']
    nid = current_app.config['POMODORO_NEXT_ID']
    rec = {
        'id': nid,
        'start_time': _now_iso(),
        'end_time': None,
        'duration_sec': None,
        'status': 'running',
        'type': ptype,
    }
    store.append(rec)
    current_app.config['POMODORO_NEXT_ID'] = nid + 1
    return jsonify({'id': rec['id']}), 201


@bp.route('/complete', methods=['POST'])
def complete():
    payload = request.get_json() or {}
    pid = payload.get('id')
    if pid is None:
        return jsonify({'error': 'id required'}), 400
    store = current_app.config['POMODORO_STORE']
    rec = next((r for r in store if r['id'] == pid), None)
    if rec is None:
        return jsonify({'error': 'not found'}), 404
    if rec['status'] == 'completed':
        return jsonify({'ok': True}), 200
    rec['end_time'] = _now_iso()
    # compute duration if start_time available
    try:
        st = datetime.fromisoformat(rec['start_time'])
        et = datetime.fromisoformat(rec['end_time'])
        rec['duration_sec'] = int((et - st).total_seconds())
    except Exception:
        rec['duration_sec'] = payload.get('duration_sec')
    rec['status'] = 'completed'
    
    # ゲーミフィケーション: XPを付与
    gamification_data = current_app.config['GAMIFICATION_DATA']
    old_xp = gamification_data['total_xp']
    gamification_data['total_xp'] += XP_PER_POMODORO
    
    # レベルアップチェック
    old_level_data = calculate_level_and_xp(old_xp)
    new_level_data = calculate_level_and_xp(gamification_data['total_xp'])
    level_up = new_level_data['level'] > old_level_data['level']
    
    return jsonify({
        'ok': True,
        'xp_gained': XP_PER_POMODORO,
        'total_xp': gamification_data['total_xp'],
        'level': new_level_data['level'],
        'level_up': level_up
    }), 200


@bp.route('/stats', methods=['GET'])
def stats():
    qdate = request.args.get('date')
    store = current_app.config['POMODORO_STORE']
    def in_date(rec, qdate_str):
        if rec.get('end_time') is None:
            return False
        try:
            et = datetime.fromisoformat(rec['end_time'])
        except Exception:
            return False
        if not qdate_str:
            return True
        d = datetime.fromisoformat(qdate_str)
        return et.date() == d.date()

    if qdate:
        # accept YYYY-MM-DD
        try:
            q_iso = datetime.fromisoformat(qdate)
        except Exception:
            # try parse plain date
            q_iso = datetime.fromisoformat(qdate + 'T00:00:00+00:00')
    else:
        q_iso = None

    completed = [r for r in store if r['status'] == 'completed' and (q_iso is None or in_date(r, q_iso.isoformat()))]
    count = len(completed)
    total_focus = sum((r.get('duration_sec') or 0) for r in completed)
    return jsonify({'completed_count': count, 'total_focus_seconds': total_focus}), 200


@bp.route('/gamification/stats', methods=['GET'])
def gamification_stats():
    """ゲーミフィケーション統計（レベル、XP、ストリーク）を取得"""
    gamification_data = current_app.config['GAMIFICATION_DATA']
    store = current_app.config['POMODORO_STORE']
    
    # レベルとXPを計算
    level_data = calculate_level_and_xp(gamification_data['total_xp'])
    
    # ストリークを計算
    completed = [r for r in store if r['status'] == 'completed']
    streak = calculate_streak(completed)
    
    return jsonify({
        'level': level_data['level'],
        'current_xp': level_data['current_xp'],
        'xp_needed_for_next_level': level_data['xp_needed_for_next_level'],
        'total_xp': level_data['total_xp'],
        'streak_days': streak
    }), 200


@bp.route('/gamification/achievements', methods=['GET'])
def achievements():
    """獲得したバッジ一覧を取得"""
    store = current_app.config['POMODORO_STORE']
    badges = check_achievements(store)
    
    return jsonify({
        'achievements': badges,
        'total_count': len(badges)
    }), 200


@bp.route('/gamification/weekly-stats', methods=['GET'])
def weekly_stats():
    """週間統計を取得"""
    store = current_app.config['POMODORO_STORE']
    stats = get_weekly_stats(store)
    
    return jsonify(stats), 200


@bp.route('/gamification/monthly-stats', methods=['GET'])
def monthly_stats():
    """月間統計を取得"""
    store = current_app.config['POMODORO_STORE']
    stats = get_monthly_stats(store)
    
    return jsonify(stats), 200

