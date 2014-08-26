import sys
import os
import logging
import time

from issue_rules import *

from google.appengine.ext import ndb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.permissions import permission_check, permission_is_root
from users.users import user_key, User
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
        header = header + "**Reporter:** " + reporter.email() + "  \n"
        issue.reporter = user_key(reporter)

    if is_defined(assignee) and assignee != issue.assignee:
        header = header + "**Assignee:** " + assignee.email() + "  \n"
        issue.assignee = user_key(assignee)

    if is_defined(verifier) and verifier != issue.verifier:
        header = header + "**Verifier:** " + verifier.email() + "  \n"
        issue.verifier = user_key(verifier)

    if is_defined(cc) and cc != issue.cc:
        header = header + "**CC:** " + reporter + "  \n"
        issue.cc = cc

    if is_defined(depends_on) and depends_on != issue.depends_on:
        header = header + "**Depends On:** " + reporter + "  \n"
        issue.depends_on = depends_on

    if is_defined(blocking) and blocking != issue.blocking:
        header = header + "**Blocking:** " + reporter + "  \n"
        issue.blocking = blocking

    if is_defined(private) and private != issue.private:
        header = header + "**Private:** " + reporter + "  \n"
        issue.private = private

    issue.updated_by = user_key(actor)
    issue.put()
    log.debug(issue)

    issue.history = [ remark_create(actor, issue.key, body.strip(), header.strip()) ]

    return to_model(issue)


def issue_deactivate(actor, issue_id=None, key=None, issue=None, **ignored):
    issue = issue_get(actor, issue_id, key, issue)
    issue.updated_by = user_key(actor)
    issue.active = False
    issue.put()


def issue_get(viewer, issue_id=None, key=None, issue=None):
    result = issue or (key or issue_key(issue_id)).get()
    if result:
        result.history = remark_list(viewer, result.key)
        return to_model(result)
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
            result.append(to_model(issue))

        return result
    else:
        raise NotAllowedError()


def to_model(issue):
    if not issue:
        return None

    return { 'id'         : issue.key.id(),
             'summary'    : issue.summary,
             'history'    : issue.history,
             'project'    : issue.project,
             'status'     : issue.status,
             'priority'   : issue.priority,
             'severity'   : issue.severity,
             'reporter'   : issue.reporter.id(),
             'assignee'   : issue.assignee.id(),
             'verifier'   : issue.verifier.id(),
             'cc'         : issue.cc,
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



