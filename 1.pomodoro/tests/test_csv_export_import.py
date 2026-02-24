"""CSV エクスポート/インポート機能のテスト"""
from io import BytesIO
import csv
from datetime import datetime, timezone


def test_export_csv_empty(client):
    """空のストアからCSVエクスポート"""
    resp = client.get('/api/export/csv')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/csv'
    assert 'attachment' in resp.headers['Content-Disposition']
    
    # ヘッダーのみが含まれることを確認
    data = resp.get_data(as_text=True)
    lines = data.strip().split('\n')
    assert len(lines) == 1  # ヘッダー行のみ
    assert 'id,start_time,end_time,duration_sec,status,type' in lines[0]


def test_export_csv_with_data(client, app):
    """データを含むCSVエクスポート"""
    # テストデータを追加
    with app.app_context():
        store = app.config['POMODORO_STORE']
        store.append({
            'id': 1,
            'start_time': '2026-02-24T10:00:00+00:00',
            'end_time': '2026-02-24T10:25:00+00:00',
            'duration_sec': 1500,
            'status': 'completed',
            'type': 'work'
        })
        store.append({
            'id': 2,
            'start_time': '2026-02-24T11:00:00+00:00',
            'end_time': None,
            'duration_sec': None,
            'status': 'running',
            'type': 'work'
        })
    
    resp = client.get('/api/export/csv')
    assert resp.status_code == 200
    
    # CSVデータを検証
    data = resp.get_data(as_text=True)
    lines = data.strip().split('\n')
    assert len(lines) == 3  # ヘッダー + 2データ行
    
    # CSV内容を解析
    reader = csv.DictReader(lines)
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]['id'] == '1'
    assert rows[0]['status'] == 'completed'
    assert rows[1]['id'] == '2'
    assert rows[1]['status'] == 'running'


def test_import_csv_no_file(client):
    """ファイル未指定でのインポート"""
    resp = client.post('/api/import/csv')
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data


def test_import_csv_invalid_extension(client):
    """不正な拡張子のファイル"""
    data = {'file': (BytesIO(b'test'), 'test.txt')}
    resp = client.post('/api/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert 'error' in json_data


def test_import_csv_valid_data(client, app):
    """正常なCSVインポート"""
    # CSVデータを準備
    csv_content = """id,start_time,end_time,duration_sec,status,type
1,2026-02-24T10:00:00+00:00,2026-02-24T10:25:00+00:00,1500,completed,work
2,2026-02-24T11:00:00+00:00,2026-02-24T11:25:00+00:00,1500,completed,work
"""
    
    data = {'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')}
    resp = client.post('/api/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    
    json_data = resp.get_json()
    assert json_data['ok'] is True
    assert json_data['imported_count'] == 2
    
    # ストアにデータが追加されたことを確認
    with app.app_context():
        store = app.config['POMODORO_STORE']
        assert len(store) == 2
        assert store[0]['id'] == 1
        assert store[1]['id'] == 2


def test_import_csv_duplicate_ids(client, app):
    """重複IDを持つCSVインポート"""
    # 既存データを追加
    with app.app_context():
        store = app.config['POMODORO_STORE']
        store.append({
            'id': 1,
            'start_time': '2026-02-24T10:00:00+00:00',
            'end_time': '2026-02-24T10:25:00+00:00',
            'duration_sec': 1500,
            'status': 'completed',
            'type': 'work'
        })
    
    # 重複IDを含むCSV
    csv_content = """id,start_time,end_time,duration_sec,status,type
1,2026-02-24T11:00:00+00:00,2026-02-24T11:25:00+00:00,1500,completed,work
2,2026-02-24T12:00:00+00:00,2026-02-24T12:25:00+00:00,1500,completed,work
"""
    
    data = {'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')}
    resp = client.post('/api/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    
    json_data = resp.get_json()
    assert json_data['imported_count'] == 1  # ID=2のみインポート
    
    # ストアの状態を確認
    with app.app_context():
        store = app.config['POMODORO_STORE']
        assert len(store) == 2  # 既存1 + 新規1


def test_export_import_roundtrip(client, app):
    """エクスポート→インポートのラウンドトリップテスト"""
    # 初期データを追加
    with app.app_context():
        store = app.config['POMODORO_STORE']
        store.append({
            'id': 1,
            'start_time': '2026-02-24T10:00:00+00:00',
            'end_time': '2026-02-24T10:25:00+00:00',
            'duration_sec': 1500,
            'status': 'completed',
            'type': 'work'
        })
    
    # エクスポート
    resp = client.get('/api/export/csv')
    assert resp.status_code == 200
    csv_data = resp.get_data()
    
    # ストアをクリア
    with app.app_context():
        app.config['POMODORO_STORE'].clear()
        app.config['POMODORO_NEXT_ID'] = 1
    
    # インポート
    data = {'file': (BytesIO(csv_data), 'export.csv')}
    resp = client.post('/api/import/csv', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    
    # データが復元されたことを確認
    with app.app_context():
        store = app.config['POMODORO_STORE']
        assert len(store) == 1
        assert store[0]['id'] == 1
        assert store[0]['status'] == 'completed'
