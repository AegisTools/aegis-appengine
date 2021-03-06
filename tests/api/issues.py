import sys
import os
import common
import time

from common import USER_ROOT, USER_A, USER_B

class IssueTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        time.sleep(0.5)
        self.assertEqual(0, len(self.get("issues", auth=USER_ROOT).json()))


    def test_root_create_issue(self):
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a" }', auth=USER_ROOT).status_code)

        list = self.get("issues", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["summary"])

        self.assertEqual("a", self.get("issues/" + str(list[0]["id"]), auth=USER_ROOT).json()["summary"])


    def test_root_create_issues(self):
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "b" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "c" }', auth=USER_ROOT).status_code)

        list = self.get("issues", auth=USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c" ]), set([ list[0]["summary"], list[1]["summary"], list[2]["summary"] ]))


    def test_root_normal_issue_flow(self):
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a" }', auth=USER_ROOT).status_code)
        id = str(self.get("issues", auth=USER_ROOT).json()[0]["id"])

        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "assigned" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "assigned" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "closed" }', auth=USER_ROOT).status_code)

        self.assertEqual("closed", self.get("issues/" + id, auth=USER_ROOT).json()["status"])


    def test_root_normal_issue_flow(self):
        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a" }', auth=USER_ROOT).status_code)
        id = str(self.get("issues", auth=USER_ROOT).json()[0]["id"])

        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "rejected" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "assigned" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "deferred" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "triage" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "deferred" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "assigned" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "fixed" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "deferred" }', auth=USER_ROOT).status_code)
        self.assertEqual(400, self.put("issues/" + id, payload='{ "status" : "rejected" }', auth=USER_ROOT).status_code)

        self.assertEqual("fixed", self.get("issues/" + id, auth=USER_ROOT).json()["status"])


    def test_privacy_private_not_allowed(self):
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "a@test.com" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "b@test.com" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a", "privacy" : "private" }', auth=USER_A).status_code)
        id = str(self.get("issues", auth=USER_A).json()[0]["id"])

        self.assertEqual(403, self.get("issues/" + id, auth=USER_B).status_code)
        self.assertEqual(403, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_B).status_code)


    def test_privacy_secure_not_allowed(self):
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "a@test.com" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "b@test.com" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.post("issues", payload='{ "summary" : "a", "privacy" : "secure" }', auth=USER_A).status_code)
        id = str(self.get("issues", auth=USER_A).json()[0]["id"])

        self.assertEqual(403, self.get("issues/" + id, auth=USER_B).status_code)
        self.assertEqual(403, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_B).status_code)


    def test_privacy_secure_view_only(self):
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "a@test.com" }', auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/issues/permission", payload='{ "user" : "b@test.com" }', auth=USER_ROOT).status_code)

        self.assertEqual(200, self.post("issues", 
                                        payload='{ "summary" : "a", "privacy" : "secure", "cc" : "b@test.com" }', 
                                        auth=USER_A).status_code)
        id = str(self.get("issues", auth=USER_A).json()[0]["id"])

        self.assertEqual("triage", self.get("issues/" + id, auth=USER_B).json()["status"])
        self.assertEqual(200, self.put("issues/" + id, payload='{ "status" : "working" }', auth=USER_B).status_code)
        self.assertEqual("triage", self.get("issues/" + id, auth=USER_B).json()["status"])






if __name__ == "__main__":
    unittest.main()

    
