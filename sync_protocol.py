"""Bounded, per-recipient replay journals. Game rules stay in the existing engine."""
import json
from collections import OrderedDict, deque
from uuid import uuid4


class RoomDelivery:
    MAX_EVENTS = 512
    MAX_BYTES = 8 * 1024 * 1024

    def __init__(self):
        self.epoch = uuid4().hex
        self.events = {role: deque() for role in ('player1', 'player2')}
        self.sequence = dict.fromkeys(self.events, 0)
        self.sizes = dict.fromkeys(self.events, 0)
        self.seen = {role: OrderedDict() for role in self.events}

    def duplicate(self, role, message_id):
        return message_id in self.seen[role]

    def remember(self, role, message_id):
        seen = self.seen[role]
        seen[message_id] = True
        while len(seen) > 4096:
            seen.popitem(last=False)

    def append(self, role, message):
        self.sequence[role] += 1
        event = dict(message, epoch=self.epoch, server_seq=self.sequence[role])
        size = len(json.dumps(event, ensure_ascii=False).encode('utf-8'))
        events = self.events[role]
        events.append((event, size))
        self.sizes[role] += size
        while len(events) > self.MAX_EVENTS or (self.sizes[role] > self.MAX_BYTES and len(events) > 1):
            _, removed_size = events.popleft()
            self.sizes[role] -= removed_size
        return event

    def replay(self, role, epoch, cursor):
        if epoch is not None and epoch != self.epoch:
            raise ValueError('伺服器對局紀錄已重建，為避免錯誤覆蓋，請雙方重新開局。')
        if not isinstance(cursor, int) or isinstance(cursor, bool) or not 0 <= cursor <= self.sequence[role]:
            raise ValueError('對局進度不符，已暫停同步以保護戰局。')
        events = self.events[role]
        if events and cursor < events[0][0]['server_seq'] - 1:
            raise ValueError('離線時間過長，完整補送紀錄已過期，請雙方重新開局。')
        return [event for event, _ in events if event['server_seq'] > cursor]
