import directory


dependencies = [ "users" ]


templates = { "*" : "_index_" }


actions = { "refresh_users"  : { "CRON" : { "method" : directory.refresh_users } },
            "refresh_groups" : { "CRON" : { "method" : directory.refresh_groups } } }



