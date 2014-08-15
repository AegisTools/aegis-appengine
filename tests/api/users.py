import sys
import os
import common

from common import USER_ROOT

class TestUsers(common.AegisTestCase):

    def test_root_create_user(self):
        self.assertIsNone(self.get("users/a", USER_ROOT).json())
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])


if __name__ == "__main__":
    unittest.main()

    
