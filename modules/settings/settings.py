import sys
import os
import urllib
import json
import logging

from google.appengine.api import urlfetch

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import system_settings


log = logging.getLogger("issues")


def settings_load(viewer):
    return system_settings.get_system_settings()


def settings_update_site(actor, host, **ignored):
    system_settings.save_system_settings(actor, { 'host': host.strip() })


def settings_update_oauth(actor, oauth2_google_client_id, oauth2_google_client_secret, **ignored):
    system_settings.save_system_settings(actor, \
            { 'oauth2_google_client_id':     oauth2_google_client_id.strip(),
              'oauth2_google_client_secret': oauth2_google_client_secret.strip(),
              'oauth2_google_request_token': "" })


def settings_oauth_token_exchange(actor, code):
    settings = system_settings.get_system_settings()

    log.debug(settings)
    url = "https://accounts.google.com/o/oauth2/token"
    payload = urllib.urlencode({ "code":          code,
                                 "client_id":     settings["oauth2_google_client_id"],
                                 "client_secret": settings["oauth2_google_client_secret"],
                                 "redirect_uri":  "http://%s/settings/oauth/token" % settings["host"],
                                 "grant_type":    "authorization_code",
                                 "scope":         "" })

    response = urlfetch.fetch("https://accounts.google.com/o/oauth2/token", payload=payload, method=urlfetch.POST)
    if response.status_code < 400:
        result = json.loads(response.content)
        system_settings.save_system_settings(actor, \
                { 'oauth2_google_request_token': str(result["refresh_token"]) })
    else:
        log.debug(response.status_code)
        log.debug(response.content)
        raise Exception()

