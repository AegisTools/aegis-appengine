import sys
import os
import common

from common import USER_ROOT

class TestUsers(common.AegisTestCase):

    def test_root_grant_permission(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c").status_code)

        list = self.get("users/a/permissions", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["user"])
        self.assertEqual("b", list[0]["type"])
        self.assertEqual("c", list[0]["action"])
        self.assertIsNone(list[0]["id"])


    def test_root_grant_permission_with_id(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c/d").status_code)

        list = self.get("users/a/permissions", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["user"])
        self.assertEqual("b", list[0]["type"])
        self.assertEqual("c", list[0]["action"])
        self.assertEqual("d", list[0]["id"])


    def test_root_grant_2_permissions(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c").status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/d").status_code)

        list = self.get("users/a/permissions", USER_ROOT).json()
        self.assertEqual(2, len(list))
        self.assertEqual("a", list[0]["user"])
        self.assertEqual("b", list[0]["type"])
        self.assertEqual("a", list[1]["user"])
        self.assertEqual("b", list[1]["type"])
        self.assertEqual(set([ "c", "d" ]), set([ list[0]["action"], list[1]["action"] ]))


    def test_root_grant_2_id_permissions(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c/d").status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c/e").status_code)

        list = self.get("users/a/permissions", USER_ROOT).json()
        self.assertEqual(2, len(list))
        self.assertEqual("a", list[0]["user"])
        self.assertEqual("b", list[0]["type"])
        self.assertEqual("c", list[0]["action"])
        self.assertEqual("a", list[1]["user"])
        self.assertEqual("b", list[1]["type"])
        self.assertEqual("c", list[0]["action"])
        self.assertEqual(set([ "d", "e" ]), set([ list[0]["id"], list[1]["id"] ]))


    def test_root_revoke_permissions(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/c").status_code)
        self.assertEqual(200, self.put("users/a/permissions/b/d").status_code)
        self.assertEqual(200, self.delete("users/a/permissions/b/d").status_code)

        list = self.get("users/a/permissions", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["user"])
        self.assertEqual("b", list[0]["type"])
        self.assertEqual("c", list[0]["action"])


if __name__ == "__main__":
    unittest.main()

    
