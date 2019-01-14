import unittest
import re, sys, os
from database import *
from imagestore import *

class TestDatabase(unittest.TestCase):
    def setUp(this):
        sys.stdout = open(os.devnull, 'w');
        this.db = get_database("memory");
        sys.stdout = sys.__stdout__;

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
            this.assertEqual(len(this.db.generate_id(4)), 4);

    def test_gid_collision(this):
        for i in range(0, 30):
            this.assertNotEqual(this.db.generate_id(4), this.db.generate_id(4));

        gid_one = this.db.create_game('erwt4');
        gid_two = this.db.create_game('gty86');
        this.assertNotEqual(gid_one, gid_two);

    def test_gid_valid(this):
        for j in [4, 10, 7, 100, 6]:
            prog = re.compile('^' + ('[a-z]' * j) + '$');
            for i in range(0, 500):
                gid = this.db.generate_id(j);
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
        this.assertTrue(this.db.add_user_to_game(gid, host, "heloe"));
        record = this.db.query_game_for_user(gid, host);
        this.assertTrue(record != None);
        this.assertTrue(record["is_host"]);
        this.assertFalse(record["is_spectator"]);
        this.assertEqual(len(record["players"]), 0);

        # test player is added only once
        for i in range(0,2):
            this.assertTrue(this.db.add_user_to_game(gid, player, "Nick" + str(i)));
            record = this.db.query_game_for_user(gid, player);
            this.assertTrue(record != None);
            this.assertEqual(len(record["players"]), 1);
            this.assertEqual(record["players"][0]["name"], "Nick0");
            this.assertEqual(record["players"][0]["id"], player);
            this.assertFalse(record["is_host"]);
            this.assertFalse(record["is_spectator"]);

        this.db.set_game_state(gid, 1, 0);
        this.assertTrue(this.db.add_user_to_game(gid, spec, "Benji"));
        record = this.db.query_game_for_user(gid, spec);
        this.assertTrue(record != None);
        this.assertEqual(len(record["players"]), 1);
        this.assertFalse(record["is_host"]);
        this.assertTrue(record["is_spectator"]);

    def test_create_image(this):
        uid = this.db.create_user('127.0.0.15');
        gid = this.db.create_game(uid);

        for i in range(0, 10):
            iid = this.db.create_image(uid, 0, gid);
            this.assertTrue(this.db.image_exists(iid));

    def test_panels(this):
        uid = this.db.create_user('127.0.0.16');
        gid = this.db.create_game(uid);

        iid = this.db.add_panel_to_game(gid, uid);
        this.assertTrue(this.db.image_exists(iid));

        panels = this.db.get_panels_in_game(gid);

        this.assertEqual(len(panels), 1);
        this.assertEqual(panels[0]["id"], iid);
        this.assertEqual(panels[0]["created_by"], uid);

        this.db.add_panel_to_game(gid, uid);
        panels = this.db.get_panels_in_game(gid);

        this.assertEqual(len(panels), 2);

        panels = this.db.get_panels_by_user(uid, -1);
        this.assertEqual(len(panels), 2);

        limits = [2, 1, 0, -10];
        for limit in limits:
            panels = this.db.get_panels_by_user(uid, limit);
            if limit < 0:
                limit = 2;

            this.assertEqual(len(panels), limit);

    def test_assignments(this):
        uid = this.db.create_user('127.0.0.17');
        gid = this.db.create_game(uid);

        player_one = "jd92";
        a_one = ["0", "1", "2"];
        player_two = "01s0";
        a_two = ["3", "4", "5"];

        assignments = {player_one: a_one, player_two: a_two};
        this.db.store_assignments(gid, assignments);

        res = this.db.get_assignments_for(gid, player_one);
        this.assertEqual(len(res), len(a_one));
        for i in a_one:
            this.assertTrue(True if i in res else False);

        res = this.db.get_assignments_for(gid, player_two);
        this.assertEqual(len(res), len(a_two));
        for i in a_two:
            this.assertTrue(True if i in res else False);

    def test_comics(this):
        uid = this.db.create_user('127.0.0.18');
        gid = this.db.create_game(uid);

        comic = ["1", "2", "3"];
        iid = this.db.add_comic_to_game(gid, uid, comic);

        this.assertTrue(iid != None);



class TestImageStore(unittest.TestCase):
    def setUp(this):
        sys.stdout = open(os.devnull, 'w');
        this.ims = get_image_store("folder");
        sys.stdout = sys.__stdout__;

    def test_image_store(this):
        im = 'iVBORw0KGgoAAAANSUhEUgAAAHAAAACgCAYAAADU3uhkAAAAXElEQVR4nO3BMQEAAADCoPVPbQsvoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOBvGK8AAQqLoVoAAAAASUVORK5CYII=';
        imid = '0192';

        this.ims.store_image(imid, im);


class TestServer(unittest.TestCase):
    def setUp():
        print("setup");



if __name__ == '__main__':
    unittest.main()
