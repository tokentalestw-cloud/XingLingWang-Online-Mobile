from unittest import TestCase
import app

class SettledSummonResponse(TestCase):
    def test_snapshot_response_keeps_sender_coordinates_for_client_side_mapping(self):
        message = {"action": "counter_summon_response", "summonRequestId": "one", "countered": True,
                   "state": {"field": {"enemy_front": [{"summonedZone": "enemy_front", "card": {"id": "x"}}]}}}
        received = app.manager.flip_message_coordinates(message)
        self.assertEqual(received, message)
        received["state"]["field"]["enemy_front"][0]["card"]["id"] = "changed"
        self.assertEqual(message["state"]["field"]["enemy_front"][0]["card"]["id"], "x")
