import asyncio
import contextlib
import io
import unittest
from app import ConnectionManager
from test_online_sync import Socket


class RoomStabilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_50_independent_rooms_duplicate_retry_and_reconnect(self):
        asyncio.get_running_loop().set_debug(False)
        manager = ConnectionManager()

        async def run_room(number):
            room = f'stability-{number}'
            a, b = Socket(), Socket()
            await manager.connect(room, f'a-{number}', 'player1', a)
            await manager.connect(room, f'b-{number}', 'player2', b)
            async def send(pid, sock, message):
                await manager.broadcast_to_other(room, pid, message, sock)
            for pid, sock in [(f'a-{number}', a), (f'b-{number}', b)]:
                await send(pid, sock, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0})
                sock.messages.clear()
            for i in range(20):
                for pid, sock in [(f'a-{number}', a), (f'b-{number}', b)]:
                    operation = {'action': 'move_unit', 'message_id': f'{pid}-{i}', 'room_marker': room, 'idx': i % 5}
                    await send(pid, sock, operation)
                    await send(pid, sock, operation)
            for sock in [a, b]:
                events = [m for m in sock.messages if 'server_seq' in m]
                self.assertEqual([m['server_seq'] for m in events], list(range(1, 21)))
                self.assertTrue(all(m['room_marker'] == room for m in events))
            manager.disconnect(room, f'b-{number}', b)
            for i in range(5):
                await send(f'a-{number}', a, {'action': 'end_turn', 'message_id': f'offline-{i}', 'room_marker': room})
            replacement = Socket()
            await manager.connect(room, f'b-{number}', 'player2', replacement)
            epoch = manager.rooms[room]['delivery'].epoch
            await send(f'b-{number}', replacement, {'action': 'resume_delivery', 'epoch': epoch, 'cursor': 20})
            replay = [m for m in replacement.messages if 'server_seq' in m]
            self.assertEqual([m['server_seq'] for m in replay], list(range(21, 26)))
            self.assertTrue(all(m['room_marker'] == room for m in replay))
        with contextlib.redirect_stdout(io.StringIO()):
            await asyncio.gather(*(run_room(number) for number in range(50)))
        self.assertEqual(len(manager.rooms), 50)

    async def test_slow_room_does_not_block_other_room(self):
        manager = ConnectionManager()
        entered, release = asyncio.Event(), asyncio.Event()
        class SlowSocket(Socket):
            async def send_json(self, message):
                if message.get('type') == 'delivery_ack':
                    entered.set()
                    await release.wait()
                await super().send_json(message)
        with contextlib.redirect_stdout(io.StringIO()):
            sockets = {}
            for room in ['slow', 'healthy']:
                a = SlowSocket() if room == 'slow' else Socket()
                b = Socket()
                for pid, role, sock in [('a', 'player1', a), ('b', 'player2', b)]:
                    await manager.connect(room, pid, role, sock)
                    await manager.broadcast_to_other(room, pid, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0}, sock)
                sockets[room] = (a, b)
            pending = asyncio.create_task(manager.broadcast_to_other('slow', 'a', {'action': 'move_unit', 'message_id': 'one'}, sockets['slow'][0]))
            await asyncio.wait_for(entered.wait(), 2)
            try:
                await asyncio.wait_for(manager.broadcast_to_other('healthy', 'a', {'action': 'move_unit', 'message_id': 'two'}, sockets['healthy'][0]), 2)
                self.assertTrue(any(m.get('message_id') == 'two' for m in sockets['healthy'][1].messages))
            finally:
                release.set()
                await pending


    async def test_sender_ack_stall_does_not_delay_recipient(self):
        manager = ConnectionManager()
        entered, release, received = asyncio.Event(), asyncio.Event(), asyncio.Event()
        class Sender(Socket):
            async def send_json(self, message):
                if message.get('type') == 'delivery_ack':
                    entered.set()
                    await release.wait()
                await super().send_json(message)
        class Receiver(Socket):
            async def send_json(self, message):
                await super().send_json(message)
                if message.get('message_id') == 'accepted':
                    received.set()
        a, b = Sender(), Receiver()
        with contextlib.redirect_stdout(io.StringIO()):
            for pid, role, sock in [('a', 'player1', a), ('b', 'player2', b)]:
                await manager.connect('one', pid, role, sock)
                await manager.broadcast_to_other('one', pid, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0}, sock)
            pending = asyncio.create_task(manager.broadcast_to_other('one', 'a', {'action': 'end_turn', 'message_id': 'accepted'}, a))
            try:
                await asyncio.wait_for(entered.wait(), 1)
                await asyncio.wait_for(received.wait(), 1)
                self.assertFalse(pending.done())
            finally:
                release.set()
                await pending

    async def test_stuck_recipient_times_out_and_replays_after_reconnect(self):
        manager = ConnectionManager()
        manager.DELIVERY_SEND_TIMEOUT = 0.02
        class Stuck(Socket):
            async def send_json(self, message):
                if message.get('message_id') == 'recover':
                    await asyncio.Event().wait()
                await super().send_json(message)
        a, b = Socket(), Stuck()
        with contextlib.redirect_stdout(io.StringIO()):
            for pid, role, sock in [('a', 'player1', a), ('b', 'player2', b)]:
                await manager.connect('one', pid, role, sock)
                await manager.broadcast_to_other('one', pid, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0}, sock)
            await asyncio.wait_for(manager.broadcast_to_other('one', 'a', {'action': 'summon', 'message_id': 'recover'}, a), 1)
            self.assertTrue(b.closed)
            self.assertFalse(manager.rooms['one']['ready']['player2'])
            replacement = Socket()
            await manager.connect('one', 'b', 'player2', replacement)
            await manager.broadcast_to_other('one', 'b', {'action': 'resume_delivery', 'epoch': manager.rooms['one']['delivery'].epoch, 'cursor': 0}, replacement)
            replay = [m for m in replacement.messages if m.get('message_id') == 'recover']
            self.assertEqual(len(replay), 1)
            self.assertEqual(replay[0]['server_seq'], 1)


if __name__ == '__main__':
    unittest.main()
