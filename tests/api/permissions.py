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


    def test_root_revoke_permission(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", USER_ROOT).json()["allowed"])


    def test_root_revoke_parent_permission(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b/c", USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/permissions/user/action/kind", USER_ROOT).status_code)
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a", USER_ROOT).json()["allowed"])
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", USER_ROOT).json()["allowed"])
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c/d", USER_ROOT).json()["allowed"])



if __name__ == "__main__":
    unittest.main()

    
