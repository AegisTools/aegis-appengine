issue_default_state = "triage"

issue_transitions = { None       : [ "triage", "assigned" ],
                      "triage"   : [ "assigned", "deferred", "rejected", "closed" ],
                      "assigned" : [ "triage", "working", "fixed", "deferred", "rejected", "closed" ],
                      "working"  : [ "triage", "assigned", "fixed", "deferred", "rejected", "closed" ],
                      "fixed"    : [ "triage", "assigned", "closed" ],
                      "closed"   : [ ],
                      "rejected" : [ "closed", "triage" ],
                      "deferred" : [ "triage", "assigned", "rejected", "closed" ] }
