import json
from datetime import datetime, timezone


def test_start_and_complete(client):
    # start
    resp = client.post('/api/start', json={'type': 'work'})
    assert resp.status_code == 201
    data = resp.get_json()
    pid = data['id']

    # complete
    resp2 = client.post('/api/complete', json={'id': pid})
    assert resp2.status_code == 200

    # stats
    resp3 = client.get('/api/stats')
    assert resp3.status_code == 200
    stats = resp3.get_json()
    assert stats['completed_count'] >= 1


def test_stats_date_filter(client):
    # create a manual record in store with known end_time
    store = client.application.config['POMODORO_STORE']
    nid = client.application.config['POMODORO_NEXT_ID']
    now = datetime.now(timezone.utc)
    rec = {
        'id': nid,
        'start_time': (now.replace(hour=0, minute=0, second=0)).isoformat(),
        'end_time': now.isoformat(),
        'duration_sec': 1500,
        'status': 'completed',
        'type': 'work',
    }
    store.append(rec)
    client.application.config['POMODORO_NEXT_ID'] = nid + 1

    date_str = now.date().isoformat()
    resp = client.get(f'/api/stats?date={date_str}')
    data = resp.get_json()
    assert data['completed_count'] >= 1
    assert data['total_focus_seconds'] >= 1500
