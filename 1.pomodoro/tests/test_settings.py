def test_settings_js_available(client):
    """設定JavaScriptファイルが利用可能であることを確認"""
    resp = client.get('/static/js/settings.js')
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    assert 'class Settings' in data
    assert 'workDuration' in data
    assert 'breakDuration' in data
    assert 'theme' in data


def test_index_includes_settings(client):
    """インデックスページに設定関連の要素が含まれることを確認"""
    resp = client.get('/')
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    
    # 設定パネル関連の要素
    assert 'settingsPanel' in data
    assert '作業時間' in data
    assert '休憩時間' in data
    assert 'テーマ' in data
    assert 'サウンド' in data
    
    # 作業時間の選択肢
    assert '15分' in data
    assert '25分' in data
    assert '35分' in data
    assert '45分' in data
    
    # 休憩時間の選択肢
    assert '5分' in data
    assert '10分' in data
    
    # テーマの選択肢
    assert 'ライト' in data
    assert 'ダーク' in data
    assert 'フォーカス' in data
    
    # サウンド設定
    assert '開始音' in data
    assert '終了音' in data
    assert 'Tick音' in data


def test_settings_script_loaded(client):
    """設定スクリプトが正しくロードされることを確認"""
    resp = client.get('/')
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    assert '/static/js/settings.js' in data
    assert '/static/js/timer_logic.js' in data
    assert '/static/js/timer_ui.js' in data
