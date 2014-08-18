import sys
import os
import common

from common import USER_ROOT

class PermissionTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", USER_ROOT).json()["allowed"])


    def test_root_grant_permission_no_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind", USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/other_action/kind", USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a", USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a", USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/b", USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_multipart_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b/c", USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a/b/d", USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_multipart_key_chaining(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b", USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c/d/e", USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a/c/d/e", USER_ROOT).json()["allowed"])


    def test_root_grant_permission_chaining(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", USER_ROOT).json()["allowed"])


#     def test_root_grant_permission_with_id(self):
#         self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/c/d").status_code)
# 
#         list = self.get("users/a/permissions", USER_ROOT).json()
#         self.assertEqual(1, len(list))
#         self.assertEqual("a", list[0]["user"])
#         self.assertEqual("b", list[0]["type"])
#         self.assertEqual("c", list[0]["action"])
#         self.assertEqual("d", list[0]["id"])
# 
# 
#     def test_root_grant_2_permissions(self):
#         self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/c").status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/d").status_code)
# 
#         list = self.get("users/a/permissions", USER_ROOT).json()
#         self.assertEqual(2, len(list))
#         self.assertEqual("a", list[0]["user"])
#         self.assertEqual("b", list[0]["type"])
#         self.assertEqual("a", list[1]["user"])
#         self.assertEqual("b", list[1]["type"])
#         self.assertEqual(set([ "c", "d" ]), set([ list[0]["action"], list[1]["action"] ]))
# 
# 
#     def test_root_grant_2_id_permissions(self):
#         self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/c/d").status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/c/e").status_code)
# 
#         list = self.get("users/a/permissions", USER_ROOT).json()
#         self.assertEqual(2, len(list))
#         self.assertEqual("a", list[0]["user"])
#         self.assertEqual("b", list[0]["type"])
#         self.assertEqual("c", list[0]["action"])
#         self.assertEqual("a", list[1]["user"])
#         self.assertEqual("b", list[1]["type"])
#         self.assertEqual("c", list[0]["action"])
#         self.assertEqual(set([ "d", "e" ]), set([ list[0]["id"], list[1]["id"] ]))
# 
# 
#     def test_root_revoke_permissions(self):
#         self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/c").status_code)
#         self.assertEqual(200, self.put("users/a/permissions/b/d").status_code)
#         self.assertEqual(200, self.delete("users/a/permissions/b/d").status_code)
# 
#         list = self.get("users/a/permissions", USER_ROOT).json()
#         self.assertEqual(1, len(list))
#         self.assertEqual("a", list[0]["user"])
#         self.assertEqual("b", list[0]["type"])
#         self.assertEqual("c", list[0]["action"])


if __name__ == "__main__":
    unittest.main()

    
