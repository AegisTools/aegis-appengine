import assets


types = { "asset"        : assets.asset_load,
          "asset_list"   : assets.asset_list,
          "asset_search" : assets.asset_search }


actions = { None             : { "POST"   : { "method"   : assets.asset_create,
                                              "redirect" : "/assets/%(asset_id)s" } },
            "{asset_id}"     : { "PUT"    : { "method"   : assets.asset_create_or_update },
                                 "POST"   : { "method"   : assets.asset_update },
                                 "DELETE" : { "method"   : assets.asset_delete } },
            "{asset_id}/out" : { "POST"   : { "method"   : assets.asset_check_out,
                                              "redirect" : "/assets/%(asset_id)s" } },
            "{asset_id}/in"  : { "POST"   : { "method"   : assets.asset_check_in, 
                                              "redirect" : "/assets/%(asset_id)s" } } }


templates = { "{asset_id}"      : "view",
              "{asset_id}/edit" : "edit" }

