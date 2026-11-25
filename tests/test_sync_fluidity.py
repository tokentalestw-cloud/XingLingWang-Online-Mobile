import json
import unittest
from sync_protocol import RoomDelivery

class CompactJournalTests(unittest.TestCase):
    def snapshot(self):
        return {'action':'sync_game_state','state':{'turn':60,'deck':[{'id':'CARD','_xlwInstanceId':str(i),'name':'千層派','effect_text':'吞食合體。'*30} for i in range(80)]}}

    def test_large_unicode_snapshot_is_compressed_and_replayed_losslessly(self):
        journal=RoomDelivery();message=self.snapshot();event=journal.append('player1',message)
        seq,payload,raw_size,compressed=journal.events['player1'][0]
        self.assertTrue(compressed)
        self.assertLess(len(payload),raw_size//4)
        self.assertEqual(journal.replay('player1',journal.epoch,0),[event])
        self.assertEqual(event['state'],message['state'])

    def test_replay_history_is_independent_of_source_and_previous_replay_mutations(self):
        journal=RoomDelivery();message=self.snapshot();journal.append('player1',message)
        message['state']['turn']=100
        result=journal.replay('player1',journal.epoch,0)
        self.assertEqual(result[0]['state']['turn'],60)
        result[0]['state']['deck'].clear()
        self.assertEqual(len(journal.replay('player1',journal.epoch,0)[0]['state']['deck']),80)

    def test_small_operations_keep_exact_order_and_have_no_compression_overhead(self):
        journal=RoomDelivery()
        for i in range(30):journal.append('player2',{'action':'move','i':i})
        self.assertTrue(all(not record[3] for record in journal.events['player2']))
        replay=journal.replay('player2',journal.epoch,10)
        self.assertEqual([m['server_seq'] for m in replay],list(range(11,31)))
        self.assertEqual(journal.replay('player1',journal.epoch,0),[])

    def test_uncompressed_byte_cap_still_bounds_replay_work_and_rejects_evicted_cursor(self):
        journal=RoomDelivery();size=len(json.dumps(self.snapshot(),ensure_ascii=False).encode())
        journal.MAX_BYTES=size*2
        for _ in range(6):journal.append('player1',self.snapshot())
        self.assertLessEqual(journal.sizes['player1'],journal.MAX_BYTES)
        self.assertEqual(journal.sizes['player1'],sum(item[2] for item in journal.events['player1']))
        with self.assertRaises(ValueError):journal.replay('player1',journal.epoch,0)
        first=journal.events['player1'][0][0]
        self.assertTrue(journal.replay('player1',journal.epoch,first-1))

    def test_last_oversized_event_is_retained_for_recovery(self):
        journal=RoomDelivery();journal.MAX_BYTES=1
        event=journal.append('player1',self.snapshot())
        self.assertEqual(journal.replay('player1',journal.epoch,0),[event])

    def test_event_cap_and_room_epochs_remain_independent(self):
        a,b=RoomDelivery(),RoomDelivery();a.MAX_EVENTS=2
        for i in range(3):a.append('player1',{'i':i})
        self.assertEqual(len(a.events['player1']),2)
        self.assertEqual(b.sequence['player1'],0)
        with self.assertRaises(ValueError):a.replay('player1',b.epoch,0)

class ClosedSocketLoopTests(unittest.IsolatedAsyncioTestCase):
    async def endpoint_case(self,mode):
        import asyncio
        from unittest.mock import patch
        from fastapi import WebSocketDisconnect
        import app
        class Manager:
            def __init__(self):self.rooms={};self.disconnected=0;self.broadcasts=0
            async def connect(self,*args):return True
            def disconnect(self,*args):self.disconnected+=1;return False
            async def broadcast_to_other(self,*args):
                self.broadcasts+=1
                if mode=='broadcast-error':raise RuntimeError('handler failed')
        class Socket:
            def __init__(self):self.reads=0;self.closes=0;self.messages=[]
            async def receive_text(self):
                await asyncio.sleep(0)
                self.reads+=1
                if mode=='closed':raise RuntimeError('WebSocket is not connected')
                if mode=='bad-json' and self.reads==1:return '{broken'
                if mode in ['bad-json','pong-error'] and self.reads<=2:return '{"action":"ping"}'
                if mode=='broadcast-error':return '{"action":"move_unit"}'
                raise WebSocketDisconnect()
            async def send_json(self,message):
                if mode=='pong-error':raise RuntimeError('connection closed while sending')
                self.messages.append(message)
            async def close(self,**kwargs):self.closes+=1
        manager,socket=Manager(),Socket()
        with patch.object(app,'manager',manager),patch('builtins.print'):
            await asyncio.wait_for(app.websocket_endpoint(socket,'room','player','player1'),timeout=.5)
        self.assertEqual(manager.disconnected,1)
        return manager,socket

    async def test_closed_transport_terminates_after_one_read_instead_of_busy_loop(self):
        _,socket=await self.endpoint_case('closed')
        self.assertEqual(socket.reads,1)
        self.assertEqual(socket.closes,1)

    async def test_lost_pong_transport_is_closed_once_and_disconnects_cleanly(self):
        _,socket=await self.endpoint_case('pong-error')
        self.assertEqual(socket.reads,1)
        self.assertEqual(socket.closes,1)

    async def test_failed_handler_cannot_spin_or_keep_a_dead_connection_registered(self):
        manager,socket=await self.endpoint_case('broadcast-error')
        self.assertEqual(manager.broadcasts,1)
        self.assertEqual(socket.closes,1)

    async def test_invalid_json_does_not_destroy_an_otherwise_healthy_connection(self):
        _,socket=await self.endpoint_case('bad-json')
        self.assertEqual(socket.reads,3)
        self.assertEqual(socket.messages,[{'action':'pong'}])
        self.assertEqual(socket.closes,0)
