import asyncio
import json
import subprocess
import sys
import time
import tempfile
import urllib.request
from pathlib import Path
from uuid import uuid4
import websockets

root = Path(__file__).resolve().parents[1]
base = 'http://127.0.0.1:18743'

async def receive(socket, predicate):
    async with asyncio.timeout(10):
        while True:
            data = json.loads(await socket.recv())
            if predicate(data):
                return data

async def connect(room, player, role, epoch=None, cursor=0):
    socket = await websockets.connect(f'ws://127.0.0.1:18743/ws/battle/{room}/{player}/{role}?protocol=2')
    welcome = await receive(socket, lambda d: d.get('type') == 'welcome')
    assert welcome['sync_protocol'] == 2
    await socket.send(json.dumps({'action': 'resume_delivery', 'epoch': epoch, 'cursor': cursor}))
    return socket, welcome

async def main():
    room = 'regression-' + uuid4().hex
    a, welcome = await connect(room, 'a', 'player1')
    await receive(a, lambda d: d.get('type') == 'resume_complete')
    b, _ = await connect(room, 'b', 'player2')
    await receive(b, lambda d: d.get('type') == 'resume_complete')
    try:
        event = {'action': 'attack_declare', 'attZone': 'player_front', 'targetZone': 'enemy_front', 'message_id': 'attack1'}
        await a.send(json.dumps(event))
        ack = await receive(a, lambda d: d.get('type') == 'delivery_ack')
        assert ack['message_id'] == 'attack1'
        relayed = await receive(b, lambda d: d.get('action') == 'attack_declare')
        assert relayed['attZone'] == 'enemy_front' and relayed['targetZone'] == 'player_front'
        assert relayed['server_seq'] == 1
        # Simulate a lost acknowledgement: retry the identical operation.
        await a.send(json.dumps(event))
        await receive(a, lambda d: d.get('type') == 'delivery_ack')
        await b.close()
        for i in range(2, 22):
            await a.send(json.dumps({'action': 'move_unit', 'message_id': f'move-{i}', 'idx': i}))
            await receive(a, lambda d: d.get('type') == 'delivery_ack')
        b, _ = await connect(room, 'b', 'player2', welcome['epoch'], 1)
        replay = []
        while True:
            data = json.loads(await asyncio.wait_for(b.recv(), 10))
            if data.get('type') == 'resume_complete':
                break
            if data.get('server_seq'):
                replay.append(data)
        assert [d['server_seq'] for d in replay] == list(range(2, 22))
        assert [d['idx'] for d in replay] == list(range(2, 22))
        await b.send(json.dumps({'action': 'ping'}))
        await receive(b, lambda d: d.get('action') == 'pong')
        # Snapshot is carried intact; front-end owns its one perspective flip.
        await a.send(json.dumps({'action': 'sync_game_state', 'message_id': 'snapshot', 'state': {'enemyHand': [], 'enemyDeck': [], 'field': {'player_front': [None]}}}))
        snapshot = await receive(b, lambda d: d.get('action') == 'sync_game_state')
        assert snapshot['state']['enemyHand'] == [] and 'player_front' in snapshot['state']['field']
        print('Real two-client WebSocket integration: PASS (handshake, ACK/retry, coordinate mapping, 20 offline operations, ordered replay, heartbeat, snapshot)')
    finally:
        await a.close()
        await b.close()

with tempfile.TemporaryFile() as log:
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '18743'], cwd=root,
                               stdout=log, stderr=log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    try:
        for _ in range(30):
            try:
                with urllib.request.urlopen(base, timeout=1) as response:
                    html = response.read().decode('utf8')
                    assert '20261031-sync-v2' in html
                break
            except OSError:
                time.sleep(.25)
        else:
            raise RuntimeError('Test server did not start')
        asyncio.run(main())
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
