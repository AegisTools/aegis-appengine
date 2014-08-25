issue_default_state = "triage"

issue_transitions = { None       : [ "triage" ],
                      "triage"   : [ "assigned", "deferred", "rejected" ],
                      "assigned" : [ "triage", "working", "fixed", "deferred", "rejected" ],
                      "working"  : [ "triage", "assigned", "fixed", "deferred", "rejected" ],
                      "fixed"    : [ "triage", "assigned", "closed" ],
                      "closed"   : [ ],
                      "rejected" : [ "closed", "triage" ],
                      "deferred" : [ "triage", "assigned", "rejected" ] }
