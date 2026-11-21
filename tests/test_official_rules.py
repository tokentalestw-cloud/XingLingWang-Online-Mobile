from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
import app

class OfficialExtraZoneRules(TestCase):
    def test_extra_zone_has_no_100_card_total_limit(self):
        catalogue = [{"id": f"ART-{i:04d}", "name": f"card {i}", "type": "unit", "faction": "藝術品", "mana": 0,
                      "is_extra_deck": i >= 20, "extra_deck_limit": 1} for i in range(145)]
        saved = {}
        @contextmanager
        def store(owner, *, write=False):
            self.assertEqual(owner, "SF")
            yield saved
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/cards.json").write_text(json.dumps(catalogue), encoding="utf-8")
            with patch.object(app, "BASE", root), patch.object(app.deck_accounts, "require_account", return_value="SF"), patch.object(app.deck_accounts, "deck_store", store):
                result = app.save_deck(app.DeckSaveSchema(deck_name="藝術品_規則測試", card_ids=[c["id"] for c in catalogue[:20]], extra_card_ids=[c["id"] for c in catalogue[20:]]), None)
            self.assertEqual(result["status"], "success")
            self.assertEqual(len(saved["藝術品_規則測試_extra"]), 125)
