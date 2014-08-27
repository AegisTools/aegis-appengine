import sys
import os
import logging
import time
import re

from issue_rules import *

from google.appengine.ext import ndb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.permissions import permission_check, permission_is_root
from users.users import user_key, user_load, User
from projects.projects import Project
from remarks.remarks import remark_create, remark_list

log = logging.getLogger("issues")


def issue_key(issue_id):
    return ndb.Key("Issue", int(issue_id))


def issue_http_put(actor, issue_id, **kwargs):
    key = issue_key(issue_id)
    issue = key.get()
    if issue:
        if permission_check(actor, "issue", "update") or permission_is_root(actor):
            issue_update(actor, issue=issue, **kwargs)
        else:
            raise NotAllowedError()
    else:
        issue_http_post(actor, key=key, issue_id=issue_id, **kwargs)


def issue_http_post(actor, **kwargs):
    if permission_check(actor, "issue", "create") or permission_is_root(actor):
        issue_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def issue_create(actor, key=None, issue_id=None, name=undefined, active=True, **kwargs):
    if "reporter" not in kwargs: kwargs["reporter"] = actor
    if "assignee" not in kwargs: kwargs["assignee"] = actor
    if "verifier" not in kwargs: kwargs["verifier"] = actor

    if "status"   not in kwargs: kwargs["status"]   = "triage"
    if "priority" not in kwargs: kwargs["priority"] = 2
    if "severity" not in kwargs: kwargs["severity"] = 2

    issue = Issue()
    issue.created_by = user_key(actor)
    return issue_update(actor, issue=issue, active=True, name=name, **kwargs)


def issue_update(actor, issue_id=None, key=None, issue=None, summary=undefined, project=undefined, 
                 status=undefined, priority=undefined, severity=undefined, reporter=undefined, 
                 assignee=undefined, verifier=undefined, cc=undefined, depends_on=undefined, 
                 blocking=undefined, private=undefined, body="", **ignored):
    issue = issue or (key or issue_key(issue_id)).get()
    header = "**" + actor.email() + "** on " + time.strftime("%c") + "\n\n"


    # Rewrite input types if necessary
    def fix_user(field):
        if is_undefined(field):
            return field
        if field == "":
            return undefined
        if isinstance(field, User):
            return field
        return user_key(field)

    reporter = fix_user(reporter)
    assignee = fix_user(assignee)
    verifier = fix_user(verifier)

    if is_defined(cc):
        log.debug(cc)
        cc = [user_key(id) for id in re.split("[\\s,;]+", cc) if len(id) > 0]
        log.debug(cc)

    blocking = undefined

    if is_defined(private):
        private = private in (True, "yes", "true", 1)

    # Update all fields
    if is_defined(summary) and summary != issue.summary:
        header = header + "**Summary:** " + summary + "  \n"
        issue.summary = summary

    if is_defined(project) and project != issue.project:
        header = header + "**Project:** " + project + "  \n"
        issue.project = project

    if is_defined(status) and status != issue.status:
        if not status in issue_transitions:
            raise Exception("Status not recognized")
        if not status in issue_transitions[issue.status]:
            raise Exception("Status transition not allowed")
        header = header + "**Status:** " + status + "  \n"
        issue.status = status

    if is_defined(priority) and int(priority) != issue.priority:
        header = header + "**Priority:** " + str(priority) + "  \n"
        issue.priority = int(priority)

    if is_defined(severity) and int(severity) != issue.severity:
        header = header + "**Severity:** " + str(severity) + "  \n"
        issue.severity = int(severity)

    if is_defined(reporter) and reporter != issue.reporter:
        header = header + "**Reporter:** " + reporter.id() + "  \n"
        issue.reporter = reporter

    if is_defined(assignee) and assignee != issue.assignee:
        header = header + "**Assignee:** " + assignee.id() + "  \n"
        issue.assignee = assignee

    if is_defined(verifier) and verifier != issue.verifier:
        header = header + "**Verifier:** " + verifier.id() + "  \n"
        issue.verifier = verifier

    if is_defined(cc) and cc != issue.cc:
        header = header + "**CC:** " + ", ".join(map(lambda user: user.id(), cc)) + "  \n"
        issue.cc = cc

    if is_defined(depends_on) and depends_on != issue.depends_on:
        header = header + "**Depends On:** " + depends_on + "  \n"
        issue.depends_on = depends_on

    if is_defined(blocking) and blocking != issue.blocking:
        header = header + "**Blocking:** " + blocking + "  \n"
        issue.blocking = blocking

    if is_defined(private) and private != issue.private:
        header = header + "**Private:** " + str(private) + "  \n"
        issue.private = private

    issue.updated_by = user_key(actor)
    issue.put()
    log.debug(issue)

    issue.history = [ remark_create(actor, issue.key, body.strip(), header.strip()) ]

    return to_model(actor, issue)


def issue_deactivate(actor, issue_id=None, key=None, issue=None, **ignored):
    issue = issue_get(actor, issue_id, key, issue)
    issue.updated_by = user_key(actor)
    issue.active = False
    issue.put()


def issue_get(viewer, issue_id=None, key=None, issue=None):
    result = issue or (key or issue_key(issue_id)).get()
    if result:
        result.history = remark_list(viewer, result.key)
        return to_model(viewer, result)
    else:
        raise NotFoundError()


def issue_load(viewer, issue_id):
    if permission_check(viewer, "issue", "read") or permission_is_root(viewer):
        return issue_get(viewer, issue_id)
    else:
        raise NotAllowedError()


def issue_list(viewer):
    if permission_check(viewer, "issue", "read") or permission_is_root(viewer):
        result = []
        for issue in Issue.query().filter():
            issue.history = []
            result.append(viewer, to_model(issue))

        return result
    else:
        raise NotAllowedError()


def issue_search(viewer, simple=None, query=None, complex=None):
    if permission_check(viewer, "issue", "read") or permission_is_root(viewer):
        if not complex:
            if query:
                complex = query_to_complex_search(query)

        result = []
        ndb_query = complex_search_to_ndb_query(complex)
        log.debug(ndb_query)
        if ndb_query:
            dataset = Issue.query().filter(ndb_query)
        else:
            dataset = Issue.query()

        for issue in dataset:
            issue.history = []
            result.append(viewer, to_model(issue))

        return result
    raise NotAllowedError()


def query_to_complex_search(query):
    segments = []
    for i in range(int(query["c"])):
        field, operator, value = query["f" + str(i)], query["o" + str(i)], query["v" + str(i)]
        segments.append({ "field"    : query["f" + str(i)],
                          "operator" : query["o" + str(i)],
                          "value"    : query["v" + str(i)].split(",") })

    return { "boolean" : query["b"], "sub" : segments }


def complex_search_to_ndb_query(query):
    if not query:
        return None

    phrases = []
    for phrase in query["sub"]:
        if "boolean" in phrase:
            phrases.append(complex_search_to_ndb_query(phrase))
        elif phrase["field"] == "text":
            pass
        else:
            field = getattr(Issue, phrase["field"])
            subphrases = []
            if phrase["operator"] == "=" or phrase["operator"] == "==" or phrase["operator"] == "in":
                for value in phrase["value"]:
                    subphrases.append(field == value)
                phrases.append(ndb.OR(*subphrases))

            elif phrase["operator"] == "!=":
                for value in phrase["value"]:
                    subphrases.append(field != value)
                phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == ">":
                for value in phrase["value"]:
                    subphrases.append(field > value)
                phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == ">=":
                for value in phrase["value"]:
                    subphrases.append(field >= value)
                phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == "<":
                for value in phrase["value"]:
                    subphrases.append(field < value)
                phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == "<=":
                for value in phrase["value"]:
                    subphrases.append(field <= value)
                phrases.append(ndb.AND(*subphrases))


    if query["boolean"] == "or":
        return ndb.OR(*phrases)
    else:
        return ndb.AND(*phrases)


def to_model(viewer, issue):
    if not issue:
        return None

    return { 'id'         : issue.key.id(),
             'summary'    : issue.summary,
             'history'    : issue.history,
             'project'    : issue.project,
             'status'     : issue.status,
             'priority'   : issue.priority,
             'severity'   : issue.severity,
             'reporter'   : user_load(viewer, key=issue.reporter),
             'assignee'   : user_load(viewer, key=issue.assignee),
             'verifier'   : user_load(viewer, key=issue.verifier),
             'cc'         : [user_load(viewer, key=key) for key in issue.cc],
             'depends_on' : issue.depends_on,
             'blocking'   : issue.blocking,
             'private'    : issue.private,
             'created_by' : issue.created_by.id(),
             'created'    : issue.created,
             'updated_by' : issue.updated_by.id(),
             'updated'    : issue.updated }


class Issue(ndb.Model):
    summary = ndb.StringProperty(required=True)
    project = ndb.KeyProperty(kind=Project)
    status = ndb.StringProperty(required=True)
    priority = ndb.IntegerProperty(required=True)
    severity = ndb.IntegerProperty(required=True)
    reporter = ndb.KeyProperty(kind=User, required=True)
    assignee = ndb.KeyProperty(kind=User, required=True)
    verifier = ndb.KeyProperty(kind=User, required=True)
    cc = ndb.KeyProperty(kind=User, repeated=True)
    depends_on = ndb.KeyProperty(kind='Issue', repeated=True)
    blocking = ndb.KeyProperty(kind='Issue', repeated=True)
    private = ndb.BooleanProperty(default=False, required=True)
    created_by = ndb.KeyProperty(kind=User)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind=User)
    updated = ndb.DateTimeProperty(auto_now=True)



