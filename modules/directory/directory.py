import sys
import os
import urllib
import json

from google.appengine.api import urlfetch
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import system_settings
from modules.users.users import user_create_or_update, user_alias_create


import logging
log = logging.getLogger("directory")


cron_user = users.User("cron")


def fetch(*args, **kwargs):
    response = urlfetch.fetch(*args, **kwargs)

    if response.status_code >= 400:
        log.debug(response.status_code)
        log.debug(response.content)
        raise Exception()

    return json.loads(response.content)


def get_access_token_header(settings=None):
    settings = settings or system_settings.get_system_settings()
    if not "oauth2_google_client_id" in settings:
        raise Exception("OAuth2 Client ID not set")
    if not "oauth2_google_client_secret" in settings:
        raise Exception("OAuth2 Client Secret not set")
    if not "oauth2_google_request_token" in settings:
        raise Exception("OAuth2 Request Token not set")

    url = "https://accounts.google.com/o/oauth2/token"
    payload = urllib.urlencode({ "client_id":     settings["oauth2_google_client_id"],
                                 "client_secret": settings["oauth2_google_client_secret"],
                                 "grant_type":    "refresh_token",
                                 "refresh_token": settings["oauth2_google_request_token"] })

    result = fetch(url, payload=payload, method=urlfetch.POST)

    token_type = str(result["token_type"])
    access_token = str(result["access_token"])

    log.debug("Access Token: %s %s" % (token_type, access_token))

    return { 'Authorization': "%s %s" % (token_type, access_token) }


def refresh_users(actor, **ignored):
    settings = system_settings.get_system_settings()
    if settings.get("directory_sync", "disabled") != "enabled":
        return

    if not "directory_domain" in settings:
        raise Exception("Directory domain not set")

    actor = actor or cron_user
    log.debug("Refreshing user list from directory: %s" % actor)

    auth_header = get_access_token_header(settings)

    user_count = 0
    alias_count = 0
    page_token = ""
    while (True):
        result = fetch("https://www.googleapis.com/admin/directory/v1/users?%s" % \
                    urllib.urlencode({ "domain":     settings["directory_domain"],
                                       "pageToken":  page_token,
                                       "maxResults": 500,
                                       "fields":     "nextPageToken,users/primaryEmail,users/name,users/emails" }), \
                    headers=auth_header)

        user_count += len(result["users"])
        for user in result["users"]:
            user_create_or_update(actor, 
                                  user_id=user["primaryEmail"],
                                  first_name=user["name"]["givenName"],
                                  last_name=user["name"]["familyName"])

            alias_count += len(user["emails"])
            for alias in user["emails"]:
                user_alias_create(actor, user_id=user["primaryEmail"], alias_id=alias["address"])

        if not "nextPageToken" in result:
            break

        page_token = result["nextPageToken"]

    log.debug("Created or updated %s users, %s aliases" % (user_count, alias_count))


def refresh_groups(actor, **ignored):
    settings = system_settings.get_system_settings()
    if settings.get("directory_sync", "disabled") != "enabled":
        return

    if not "directory_domain" in settings:
        raise Exception("Directory domain not set")

    actor = actor or cron_user
    log.debug("Refreshing group list from directory: %s" % actor)

    auth_header = get_access_token_header(settings)

    group_count = 0
    alias_count = 0
    member_count = 0
    page_token = ""
    while (True):
        result = fetch("https://www.googleapis.com/admin/directory/v1/groups?%s" % \
                    urllib.urlencode({ "domain":     settings["directory_domain"],
                                       "pageToken":  page_token,
                                       "maxResults": 500,
                                       "fields":     ",".join([ "nextPageToken",
                                                                "groups/email",
                                                                "groups/name",
                                                                "groups/aliases",
                                                                "groups/id",
                                                                "groups/directMembersCount" ]) }), \
                    headers=auth_header)

        group_count += len(result["groups"])
        alias_count += len(result["groups"])
        for group in result["groups"]:
            log.warn("TODO: Create group: %s %s" % (group["email"], group["name"]))
            log.warn("TODO: Create group alias: %s %s" % (group["email"], group["email"]))

            if "aliases" in group:
                alias_count += len(group["aliases"])
                for alias in group["aliases"]:
                    log.warn("TODO: Create group alias: %s %s" % (group["email"], alias))

            log.warn("TODO: Remove all users from group: %s" % group["email"])

            log.debug(group)
            if int(group["directMembersCount"]) > 0:
                member_page_token = ""
                while (True):
                    member_result = fetch("https://www.googleapis.com/admin/directory/v1/groups/%s/members?%s" % (group["id"], \
                                urllib.urlencode({ "pageToken": page_token,
                                                   "fields":    ",".join([ "nextPageToken",
                                                                           "members/email",
                                                                           "members/type" ]) })), \
                                headers=auth_header)

                    log.debug(member_result)
                    if "members" in member_result:
                        member_count += len(member_result["members"])
                        for member in member_result["members"]:
                            if "email" in member:
                                log.warn("TODO: Add group member: %s %s (%s)" % (group["email"], member["email"], member["type"]))

                    if not "nextPageToken" in member_result:
                        break

                    member_page_token = member_result["nextPageToken"]


        if not "nextPageToken" in result:
            break

        page_token = result["nextPageToken"]

    log.debug("Created or updated %s groups, %s aliases, %s members" % (group_count, alias_count, member_count))

    

