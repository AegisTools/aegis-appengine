import sys
import os
import urllib
import json

from google.appengine.api import urlfetch
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import system_settings
from modules.users.users import user_create_or_update, user_list_raw
from modules.users.aliases import alias_create
from modules.users.groups import group_create_or_update, build_group_key
from modules.users.members import group_members_add, group_members_clear


import logging
log = logging.getLogger("directory")


cron_user = users.User("cron")


def fetch(*args, **kwargs):
    try:
        response = urlfetch.fetch(*args, **kwargs)
    except:
        return {}

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


def refresh_users(actor, force=False, **ignored):
    settings = system_settings.get_system_settings()
    if not force and settings.get("directory_sync", "disabled") != "enabled":
        log.debug("Directory action disabled")
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
                alias_create(actor, alias_id=alias["address"], user_id=user["primaryEmail"])

        if not "nextPageToken" in result:
            break

        page_token = result["nextPageToken"]

    log.debug("Created or updated %s users, %s aliases" % (user_count, alias_count))


def refresh_groups(actor, force=False, **ignored):
    settings = system_settings.get_system_settings()
    if not force and settings.get("directory_sync", "disabled") != "enabled":
        log.debug("Directory action disabled")
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
    all_groups = {}
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

        for group in result["groups"]:
            group_data = { 'email':   group["email"],
                           'name':    group["name"],
                           'aliases': [],
                           'members': [] }

            all_groups[group["email"]] = group_data

            if "aliases" in group:
                group_data["aliases"] = group["aliases"]

            log.debug("Getting members of group %s" % group["email"])
            if int(group["directMembersCount"]) > 0:
                member_page_token = ""
                while (True):
                    member_result = fetch("https://www.googleapis.com/admin/directory/v1/groups/%s/members?%s" % (group["id"], \
                                urllib.urlencode({ "pageToken": member_page_token,
                                                   "fields":    ",".join([ "nextPageToken",
                                                                           "members/email",
                                                                           "members/type" ]) })), \
                                headers=auth_header)

                    if "members" in member_result:
                        group_data["members"].extend(member_result["members"])

                    if not "nextPageToken" in member_result:
                        break

                    member_page_token = member_result["nextPageToken"]

        if not "nextPageToken" in result:
            break

        page_token = result["nextPageToken"]

    all_users = { user.user.email(): user for user in user_list_raw(actor) }

    def get_group_members(group_id, members):
        result = []
        for member in members:
            if member["type"] == "GROUP":
                if member["email"] in all_groups:
                    result.extend(get_group_members(group_id, all_groups[member["email"]]["members"]))
                else:
                    log.warn("Could not find group: %s" % member["email"])
            elif member["type"] == "USER":
                if member["email"] in all_users:
                    result.append(all_users[member["email"]])
            elif member["type"] == "CUSTOMER":
                result.extend(all_users.values())
            else:
                log.debug("%s" % member)
        return result

    group_count += len(all_groups)
    for group_name in sorted(all_groups):
        log.debug("Creating or updating group %s" % group_name)

        group = all_groups[group_name]
        group_create_or_update(actor, group_id=group["email"], name=group["name"], active=True)
        group_obj = build_group_key(group_name).get()
        alias_create(actor, alias_id=group["email"], group=group_obj)
        group_members_clear(actor, group=group_obj)

        alias_count += len(group["aliases"]) + 1
        for alias in group["aliases"]:
            alias_create(actor, alias_id=alias, group=group_obj)

        for member in get_group_members(group["email"], group["members"]):
            group_members_add(actor, group=group_obj, user=member)


    log.debug("Created or updated %s groups, %s aliases, %s members" % (group_count, alias_count, member_count))

    

