import asyncio
import copy
import unittest
from app import ConnectionManager
from sync_protocol import RoomDelivery


class Socket:
    def __init__(self, protocol='2'):
        self.query_params = {'protocol': protocol}
        self.messages = []
        self.closed = False
        self.fail_ack = False

    async def accept(self):
        pass

    async def close(self, **kwargs):
        self.closed = True

    async def send_json(self, message):
        await asyncio.sleep(0)
        if self.fail_ack and message.get('type') == 'delivery_ack':
            raise ConnectionError('simulated lost acknowledgement')
        self.messages.append(copy.deepcopy(message))


class DeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.manager = ConnectionManager()
        self.a, self.b = Socket(), Socket()
        await self.manager.connect('test', 'a', 'player1', self.a)
        await self.manager.connect('test', 'b', 'player2', self.b)
        await self.send('a', self.a, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0})
        await self.send('b', self.b, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0})
        self.a.messages.clear()
        self.b.messages.clear()

    async def send(self, pid, socket, message):
        await self.manager.broadcast_to_other('test', pid, message, socket)

    async def test_duplicate_operation_applied_once(self):
        message = {'action': 'summon', 'zone': 'player_front', 'idx': 0, 'message_id': 'one'}
        await self.send('a', self.a, message)
        await self.send('a', self.a, message)
        self.assertEqual(len(self.b.messages), 1)
        self.assertEqual(self.b.messages[0]['zone'], 'enemy_front')
        self.assertEqual(len(self.a.messages), 2)

    async def test_offline_operations_replayed_in_order(self):
        self.manager.disconnect('test', 'b', self.b)
        for i in range(30):
            await self.send('a', self.a, {'action': 'attack_declare', 'message_id': str(i), 'idx': i})
        replacement = Socket()
        await self.manager.connect('test', 'b', 'player2', replacement)
        await self.send('b', replacement, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0})
        replay = [m for m in replacement.messages if 'server_seq' in m]
        self.assertEqual([m['idx'] for m in replay], list(range(30)))
        self.assertEqual([m['server_seq'] for m in replay], list(range(1, 31)))

    async def test_resume_from_checkpoint_not_stale_peer_snapshot(self):
        for i in range(5):
            await self.send('a', self.a, {'action': 'move_unit', 'message_id': str(i)})
        epoch = self.manager.rooms['test']['delivery'].epoch
        self.manager.rooms['test']['client_backups']['player2'] = {
            'sync_metadata': {'epoch': epoch, 'cursor': 3}, 'hand': [],
        }
        replacement = Socket()
        await self.manager.connect('test', 'b', 'player2', replacement)
        await self.send('b', replacement, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0})
        self.assertEqual([m['server_seq'] for m in replacement.messages if 'server_seq' in m], [4, 5])
        self.assertTrue(any(m.get('type') == 'restore_client_backup' for m in replacement.messages))

    async def test_checkpoint_cursor_only_replays_later_events(self):
        for i in range(5):
            await self.send('a', self.a, {'action': 'move_unit', 'message_id': str(i)})
        replacement = Socket()
        await self.manager.connect('test', 'b', 'player2', replacement)
        epoch = self.manager.rooms['test']['delivery'].epoch
        await self.send('b', replacement, {'action': 'resume_delivery', 'epoch': epoch, 'cursor': 3})
        self.assertEqual([m['server_seq'] for m in replacement.messages if 'server_seq' in m], [4, 5])
        self.assertFalse(any(m.get('action') == 'sync_game_state' for m in replacement.messages))

    async def test_old_socket_cannot_send_or_disconnect_replacement(self):
        replacement = Socket()
        await self.manager.connect('test', 'a', 'player1', replacement)
        self.assertFalse(self.manager.disconnect('test', 'a', self.a))
        await self.send('a', self.a, {'action': 'end_turn', 'message_id': 'stale'})
        self.assertFalse(any(m.get('action') == 'end_turn' for m in self.b.messages))
        self.assertIs(self.manager.rooms['test']['player1'][1], replacement)

    async def test_role_cannot_be_taken_by_another_player(self):
        impostor = Socket()
        result = await self.manager.connect('test', 'stranger', 'player1', impostor)
        self.assertFalse(result)
        self.assertTrue(impostor.closed)
        self.assertIs(self.manager.rooms['test']['player1'][1], self.a)

    async def test_leave_during_recovery_releases_room(self):
        self.manager.rooms['test']['ready']['player1'] = False
        await self.send('a', self.a, {'action': 'leave_room', 'message_id': 'leave'})
        self.assertNotIn('test', self.manager.rooms)
        self.assertTrue(any(m.get('action') == 'leave_room' for m in self.b.messages))

    async def test_invalid_role_is_rejected(self):
        invalid = Socket()
        self.assertFalse(await self.manager.connect('test', 'new', 'administrator', invalid))
        self.assertTrue(invalid.closed)

    async def test_lost_sender_ack_does_not_drop_recipient_delivery(self):
        self.a.fail_ack = True
        await self.send('a', self.a, {'action': 'end_turn', 'message_id': 'lost-ack'})
        self.assertEqual(len(self.b.messages), 1)

    async def test_resume_concurrent_with_live_send_never_loses_an_event(self):
        replacement = Socket()
        await self.manager.connect('test', 'b', 'player2', replacement)
        await asyncio.gather(
            self.send('b', replacement, {'action': 'resume_delivery', 'epoch': None, 'cursor': 0}),
            *(self.send('a', self.a, {'action': 'move_unit', 'message_id': str(i)}) for i in range(40)),
        )
        self.assertEqual([m['server_seq'] for m in replacement.messages if 'server_seq' in m], list(range(1, 41)))


class JournalTests(unittest.TestCase):
    def test_expired_history_is_explicitly_rejected(self):
        journal = RoomDelivery()
        journal.MAX_EVENTS = 2
        for _ in range(3):
            journal.append('player1', {'action': 'x'})
        with self.assertRaises(ValueError):
            journal.replay('player1', journal.epoch, 0)
        self.assertEqual(len(journal.replay('player1', journal.epoch, 1)), 2)

    def test_server_restart_does_not_accept_old_epoch(self):
        with self.assertRaises(ValueError):
            RoomDelivery().replay('player1', 'old-room', 0)

    def test_snapshot_coordinates_only_flipped_by_client(self):
        manager = ConnectionManager()
        snapshot = {'action': 'sync_game_state', 'state': {'field': {'player_front': [None]}, 'target': 'player_front'}}
        self.assertEqual(manager.flip_message_coordinates(snapshot), snapshot)
        event = {'action': 'attack_declare', 'target': {'zone': 'enemy_back'}}
        self.assertEqual(manager.flip_message_coordinates(event)['target']['zone'], 'player_back')
        self.assertEqual(event['target']['zone'], 'enemy_back')


if __name__ == '__main__':
    unittest.main(verbosity=2)
