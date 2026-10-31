import asyncio
import unittest
from unittest.mock import patch
from app import ConnectionManager
from test_online_sync import Socket


class TurnOrderTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.manager = ConnectionManager()
        self.a, self.b = Socket(), Socket()
        await self.manager.connect('draw', 'a', 'player1', self.a)
        await self.manager.connect('draw', 'b', 'player2', self.b)
        for pid, socket in [('a', self.a), ('b', self.b)]:
            await self.send(pid, socket, action='resume_delivery', epoch=None, cursor=0)
        self.room = self.manager.rooms['draw']
        self.room['decks'] = {'player1': {}, 'player2': {}}
        self.a.messages.clear()
        self.b.messages.clear()

    async def send(self, pid, socket, **message):
        await self.manager.broadcast_to_other('draw', pid, message, socket)

    async def pick(self, selected=0, swap=0, message_id='pick'):
        with patch('app.secrets.randbelow', return_value=swap):
            await self.send('a', self.a, action='turn_order_pick', selected=selected, message_id=message_id)
        return self.room.get('turn_order')

    async def test_both_cards_and_both_shuffle_orders(self):
        for selected in (0, 1):
            for swap in (0, 1):
                self.room['turn_order'] = None
                state = await self.pick(selected, swap, f'pick-{selected}-{swap}')
                self.assertEqual(state['winner_role'], ['player1', 'player2'][selected ^ swap])
                events = [[m for m in s.messages if m.get('action') == 'turn_order_reveal'][-1] for s in (self.a, self.b)]
                self.assertEqual(events[0]['winner_role'], events[1]['winner_role'])
                self.assertEqual(events[0]['draw_id'], events[1]['draw_id'])

    async def test_duplicate_and_second_pick_never_redraw(self):
        state = dict(await self.pick())
        await self.pick(message_id='pick')
        await self.pick(1, 1, 'another')
        self.assertEqual(self.room['turn_order'], state)
        self.assertEqual(sum(m.get('action') == 'turn_order_reveal' for m in self.a.messages), 1)

    async def test_guest_and_invalid_indexes_rejected(self):
        await self.send('b', self.b, action='turn_order_pick', selected=0, message_id='guest')
        for value in (-1, 2, True, '0', None):
            await self.pick(value, message_id=f'bad-{value}')
        self.assertIsNone(self.room.get('turn_order'))

    async def test_both_decks_required(self):
        self.room['decks'].pop('player2')
        self.assertIsNone(await self.pick())

    async def test_only_actual_winner_can_choose(self):
        state = await self.pick()
        await self.send('b', self.b, action='turn_order_choice', draw_id=state['draw_id'], choice='first', message_id='fake-choice')
        self.assertIsNone(state['first_role'])
        await self.send('a', self.a, action='turn_order_choice', draw_id='stale', choice='first', message_id='stale')
        self.assertIsNone(state['first_role'])

    async def test_first_second_each_winner_and_confirmation_once(self):
        for swap in (0, 1):
            for choice in ('first', 'second'):
                self.room['turn_order'] = None
                state = await self.pick(swap=swap, message_id=f'pick-{swap}-{choice}')
                pid, socket = ('a', self.a) if state['winner_role'] == 'player1' else ('b', self.b)
                msg = dict(action='turn_order_choice', draw_id=state['draw_id'], choice=choice, message_id=f'choice-{swap}-{choice}')
                await self.send(pid, socket, **msg)
                first = state['winner_role'] if choice == 'first' else ('player2' if state['winner_role'] == 'player1' else 'player1')
                self.assertEqual(state['first_role'], first)
                count = sum(m.get('action') == 'turn_order_confirmed' for m in self.a.messages)
                await self.send(pid, socket, **msg)
                await self.send(pid, socket, **dict(msg, message_id=msg['message_id']+'-again'))
                self.assertEqual(sum(m.get('action') == 'turn_order_confirmed' for m in self.a.messages), count)

    async def test_offline_draw_and_confirm_replay_for_both(self):
        self.manager.disconnect('draw', 'b', self.b)
        state = await self.pick()
        await self.send('a', self.a, action='turn_order_choice', draw_id=state['draw_id'], choice='second', message_id='choose')
        replacement = Socket()
        await self.manager.connect('draw', 'b', 'player2', replacement)
        await self.send('b', replacement, action='resume_delivery', epoch=None, cursor=0)
        events = [m for m in replacement.messages if m.get('action', '').startswith('turn_order_')]
        self.assertEqual([e['action'] for e in events], ['turn_order_reveal', 'turn_order_confirmed'])
        self.assertEqual(events[-1]['first_role'], 'player2')

    async def test_simultaneous_picks_only_one_committed(self):
        await asyncio.gather(self.pick(0, message_id='left'), self.pick(1, message_id='right'))
        self.assertEqual(sum(m.get('action') == 'turn_order_reveal' for m in self.a.messages), 1)

    async def test_new_game_clears_opening(self):
        await self.pick()
        await self.send('a', self.a, action='new_game', message_id='new')
        self.assertIsNone(self.room['turn_order'])
