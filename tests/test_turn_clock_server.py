import unittest
from app import ConnectionManager
from test_online_sync import Socket

class TurnClockRelay(unittest.IsolatedAsyncioTestCase):
    async def test_clock_packets_are_ephemeral_and_holder_validated(self):
        manager=ConnectionManager()
        a,b=Socket(),Socket()
        await manager.connect('clock','a','player1',a)
        await manager.connect('clock','b','player2',b)
        a.messages.clear();b.messages.clear()
        clock={'turn':2,'owner':'player1','phase':'召喚階段','remaining':90000,'stageRemaining':30000,'paused':False}
        await manager.broadcast_to_other('clock','a',{'action':'turn_clock','clock':clock},a)
        self.assertEqual(b.messages[-1]['clock'],clock)
        self.assertNotIn('server_seq',b.messages[-1])
        self.assertEqual(a.messages,[])
        count=len(b.messages)
        for invalid in [{**clock,'owner':'player2'},{**clock,'remaining':999999},{**clock,'stageRemaining':-1}]:
            await manager.broadcast_to_other('clock','a',{'action':'turn_clock','clock':invalid},a)
        self.assertEqual(len(b.messages),count)
