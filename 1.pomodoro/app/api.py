from flask import Blueprint, current_app, request, jsonify
from datetime import datetime, timezone, date

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
    return jsonify({'ok': True}), 200


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
