def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert 'ポモドーロタイマー' in resp.get_data(as_text=True)


def test_static_css(client):
    resp = client.get('/static/css/styles.css')
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    assert '.progress-ring' in data
