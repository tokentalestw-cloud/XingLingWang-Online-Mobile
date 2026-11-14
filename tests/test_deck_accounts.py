from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

import app
import deck_accounts


class PersonalDeckTests(TestCase):
    def test_owner_scopes_name_collision_rename_and_delete(self):
        owners = {"SF": {"山羊族_我的牌組": ["sf"], "山羊族_我的牌組_extra": ["extra"]},
                  "HY": {"山羊族_我的牌組": ["hy"]}}

        @contextmanager
        def store(owner, *, write=False):
            yield owners[owner]

        def request(owner, method="GET", tab=None):
            return Request({"type": "http", "method": method, "headers": [
                (b"x-deck-account", (tab or owner).encode()),
                (b"cookie", f"{deck_accounts.COOKIE}={owner}".encode()),
            ]})

        def resolve_owner(req):
            return req.cookies.get(deck_accounts.COOKIE)

        with patch.object(deck_accounts, "account", side_effect=resolve_owner), patch.object(deck_accounts, "deck_store", store):
            name = "山羊族_我的牌組"
            self.assertEqual(app.get_decks(request("SF"), personal=True)[name], ["sf"])
            self.assertEqual(app.get_decks(request("HY"), personal=True)[name], ["hy"])
            with self.assertRaises(HTTPException) as err:
                app.delete_deck(app.DeckDeleteSchema(deck_name=name), request("HY", "POST", tab="SF"))
            self.assertEqual(err.exception.status_code, 409)
            app.rename_deck(app.DeckRenameSchema(old_name=name, new_name="山羊族_改名"), request("SF", "POST"))
            self.assertEqual(owners["SF"]["山羊族_改名_extra"], ["extra"])
            app.delete_deck(app.DeckDeleteSchema(deck_name="山羊族_改名"), request("SF", "POST"))
            self.assertEqual(owners["SF"], {})
            self.assertEqual(owners["HY"][name], ["hy"])

    def test_public_decks_and_anonymous_writes(self):
        request = Request({"type": "http", "method": "GET", "headers": []})
        self.assertIn("中立單位", app.get_decks(request))
        with self.assertRaises(HTTPException) as err:
            app.delete_deck(app.DeckDeleteSchema(deck_name="中立單位"), request)
        self.assertEqual(err.exception.status_code, 401)
