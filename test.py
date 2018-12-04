import unittest
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(this):
        this.db = Database();

    def test_uid_size(this):
        this.assertEqual(len(this.db.generate_user_id()), 5);

    def test_uid_collision(this):
        this.assertNotEqual(this.db.generate_user_id(), this.db.generate_user_id());

        uid_one = this.db.create_user('127.0.0.1');
        uid_two = this.db.create_user('127.0.0.2');
        this.assertNotEqual(uid_one, uid_two);

if __name__ == '__main__':
    unittest.main()
