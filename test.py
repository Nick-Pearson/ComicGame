import unittest
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

    def test_game_create(this):
        gid = this.db.create_game('3heuo');

        this.assertTrue(this.db.game_exists(gid));

if __name__ == '__main__':
    unittest.main()
