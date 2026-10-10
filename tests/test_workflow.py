from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from homerelay.app import create_app
from homerelay.store import Conflict, Store


@pytest.fixture
def household(tmp_path):
    store = Store(tmp_path / 'home.db')
    alex, mira = store.add_member('Alex'), store.add_member('Mira')
    task = store.create('Collect parcel', alex['id'], '2026-10-12T17:00:00+05:30', 2, 'parcel-1')
    return store, alex, mira, task


def test_handoff_requires_recipient_then_completion(household):
    store, alex, mira, task = household
    pending = store.change(task['id'], alex['id'], 1, 'propose', mira['id'])
    assert pending['owner_id'] == alex['id']
    assert store.briefing(mira['id'])['pending_handoffs'][0]['id'] == task['id']
    with pytest.raises(Conflict, match='recipient'):
        store.change(task['id'], alex['id'], 2, 'accept')
    accepted = store.change(task['id'], mira['id'], 2, 'accept')
    assert accepted['owner_id'] == mira['id']
    with pytest.raises(Conflict, match='current owner'):
        store.change(task['id'], alex['id'], 3, 'complete')
    completed = store.change(task['id'], mira['id'], 3, 'complete')
    assert completed['status'] == 'done'
    assert len(store.history()) == 4


def test_retry_is_idempotent_and_reused_key_conflicts(household):
    store, alex, _, task = household
    duplicate = store.create('Collect parcel', alex['id'], '2026-10-12T11:30:00Z', 2, 'parcel-1')
    assert duplicate['id'] == task['id']
    assert len(store.list_tasks()) == len(store.history()) == 1
    with pytest.raises(Conflict, match='different'):
        store.create('Different errand', alex['id'], '2026-10-12T11:30:00Z', 2, 'parcel-1')


def test_concurrent_confirmation_only_one_wins(household):
    store, alex, mira, task = household
    def change(action):
        try:
            store.change(task['id'], alex['id'], 1, action, mira['id'])
            return 'ok'
        except Conflict:
            return 'conflict'
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(change, ['propose', 'complete'])) == ['conflict', 'ok']
    assert len(store.history()) == 2


def test_decline_preserves_owner_and_survives_restart(household):
    store, alex, mira, task = household
    store.change(task['id'], alex['id'], 1, 'propose', mira['id'])
    store.change(task['id'], mira['id'], 2, 'decline')
    recovered = Store(store.path)
    assert recovered.list_tasks()[0]['owner_id'] == alex['id']
    assert recovered.list_tasks()[0]['proposed_owner'] is None
    assert len(recovered.history()) == 3


def test_timezone_and_member_validation(household):
    store, alex, _, _ = household
    with pytest.raises(ValueError, match='timezone'):
        store.create('Errand', alex['id'], '2026-10-12T17:00', 2, 'bad-time')
    with pytest.raises(ValueError, match='Unknown'):
        store.create('Errand', 'missing', '2026-10-12T17:00Z', 2, 'missing-person')
    with pytest.raises(ValueError, match='title'):
        store.create('  ', alex['id'], '2026-10-12T17:00Z', 2, 'empty')


def test_rest_auth_and_cross_origin(tmp_path):
    with TestClient(create_app(tmp_path / 'api.db', token='test-only-token')) as client:
        assert client.get('/api/board').status_code == 401
        assert client.post('/mcp/', json={}).status_code == 401
        headers = {'Authorization': 'Bearer test-only-token'}
        assert client.get('/api/board', headers=headers).status_code == 200
        assert client.get('/api/board', headers={**headers, 'Origin':'https://example.com'}).status_code == 403
        assert client.post('/api/members', headers=headers, json={'name':' '}).status_code == 422


def test_rest_full_journey(tmp_path):
    with TestClient(create_app(tmp_path / 'api.db', token='')) as client:
        alex = client.post('/api/members',json={'name':'Alex'}).json()
        mira = client.post('/api/members',json={'name':'Mira'}).json()
        payload = {'title':'Water plants','owner_id':alex['id'],'due_at':'2026-10-01T12:00:00Z','priority':2,'request_id':'plants'}
        task = client.post('/api/tasks',json=payload).json()
        assert client.post('/api/tasks',json=payload).json()['id'] == task['id']
        path = '/api/tasks/' + task['id'] + '/change'
        assert client.post(path,json={'actor_id':alex['id'],'version':1,'action':'propose','target_id':mira['id']}).status_code == 200
        assert client.post(path,json={'actor_id':mira['id'],'version':1,'action':'accept'}).status_code == 409
        assert client.post(path,json={'actor_id':mira['id'],'version':2,'action':'accept'}).status_code == 200
        assert client.get('/api/briefing/'+mira['id']).json()['overdue_tasks'][0]['id'] == task['id']
        assert client.post(path,json={'actor_id':mira['id'],'version':3,'action':'complete'}).status_code == 200
        assert client.get('/api/board').json()['tasks'][0]['status'] == 'done'


def test_loopback_mode_rejects_remote_host_and_client(tmp_path):
    app = create_app(tmp_path / 'local.db', token='')
    with TestClient(app) as client:
        assert client.get('/api/board', headers={'Host': 'attacker.example'}).status_code == 403
    with TestClient(create_app(tmp_path / 'remote.db', token=''), client=('192.0.2.1', 50000)) as client:
        assert client.get('/api/board').status_code == 403
