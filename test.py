import unittest
import re
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(this):
        this.db = Database();

    def test_uid_size(this):
        for i in range(0, 30):
            this.assertEqual(len(this.db.generate_user_id()), 5);

    def test_uid_collision(this):
        for i in range(0, 30):
            this.assertNotEqual(this.db.generate_user_id(), this.db.generate_user_id());

        uid_one = this.db.create_user('127.0.0.1');
        uid_two = this.db.create_user('127.0.0.2');
        this.assertNotEqual(uid_one, uid_two);

    def test_user_create(this):
        uid = this.db.create_user('127.0.0.3');

        this.assertTrue(this.db.user_exists(uid));

    def test_gid_size(this):
        for i in range(0, 30):
            this.assertEqual(len(this.db.generate_game_id()), 4);

    def test_gid_collision(this):
        for i in range(0, 30):
            this.assertNotEqual(this.db.generate_game_id(), this.db.generate_game_id());

        gid_one = this.db.create_game('erwt4');
        gid_two = this.db.create_game('gty86');
        this.assertNotEqual(gid_one, gid_two);

    def test_gid_valid(this):
        prog = re.compile('^[a-z][a-z][a-z][a-z]$');
        for i in range(0, 500):
            gid = this.db.generate_game_id()
            result = prog.match(gid);
            this.assertEqual("" if result == None else result.string, gid);

    def test_game_create(this):
        gid = this.db.create_game('3heuo');

        this.assertTrue(this.db.game_exists(gid));

    def test_game_data(this):
        # tests that the game data enpoint returns correctly
        host = this.db.create_user('127.0.0.10');
        spec = this.db.create_user('127.0.0.11');
        gid = this.db.create_game(host);

        record = this.db.query_game_for_user(gid, host);
        this.assertTrue(record != None);
        this.assertEqual(record["state"], 0);
        this.assertTrue(record["is_host"]);
        this.assertFalse(record["is_spectator"]);
        this.assertEqual(record["game_id"], gid);
        this.assertEqual(len(record["players"]), 0);

        record = this.db.query_game_for_user(gid, spec);
        this.assertTrue(record != None);
        this.assertEqual(record["state"], 0);
        this.assertFalse(record["is_host"]);
        this.assertTrue(record["is_spectator"]);
        this.assertEqual(record["game_id"], gid);
        this.assertEqual(len(record["players"]), 0);

    def test_add_players(this):
        host = this.db.create_user('127.0.0.12');
        player = this.db.create_user('127.0.0.13');
        spec = this.db.create_user('127.0.0.14');

        gid = this.db.create_game(host);

        record = this.db.query_game_for_user(gid, host);
        this.assertTrue(record != None);
        this.assertTrue(record["is_host"]);
        this.assertEqual(len(record["players"]), 0);

        # test host is not added as a players
        this.db.add_user_to_game(gid, host, "heloe");
        record = this.db.query_game_for_user(gid, host);
        this.assertTrue(record != None);
        this.assertTrue(record["is_host"]);
        this.assertFalse(record["is_spectator"]);
        this.assertEqual(len(record["players"]), 0);

        # test player is added only once
        for i in range(0,1):
            this.db.add_user_to_game(gid, player, "Nick");
            record = this.db.query_game_for_user(gid, player);
            this.assertTrue(record != None);
            this.assertEqual(len(record["players"]), 1);
            this.assertEqual(record["players"][0]["name"], "Nick");
            this.assertFalse(record["is_host"]);
            this.assertFalse(record["is_spectator"]);

        this.db.set_game_state(gid, 1, 0);
        this.db.add_user_to_game(gid, spec, "Benji");
        record = this.db.query_game_for_user(gid, spec);
        this.assertTrue(record != None);
        this.assertEqual(len(record["players"]), 1);
        this.assertFalse(record["is_host"]);
        this.assertTrue(record["is_spectator"]);


if __name__ == '__main__':
    unittest.main()
