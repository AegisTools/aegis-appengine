import sys
import os
import logging
import time
import re
import datetime

from issue_rules import *

from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import app_identity

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.arguments import *
from users.permissions import permission_verify, permission_is_root
from users.users import build_user_key, user_load
from projects.projects import Project
from remarks.remarks import remark_create, remark_list

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.common.errors import *
from system_settings import get_system_settings

import lib.markdown
import lib.parsedatetime

log = logging.getLogger("issues")


open_statuses = [ "triage", "assigned", "working", "rejected", "deferred", "fixed" ]

def issue_key(issue_id):
    return ndb.Key("Issue", int(issue_id))


def issue_http_put(actor, issue_id, **kwargs):
    key = issue_key(issue_id)
    issue = key.get()
    if issue:
        permission_verify(actor, "issue", "update")
        return issue_update(actor, issue=issue, **kwargs)
    else:
        return issue_http_post(actor, key=key, issue_id=issue_id, **kwargs)


def issue_http_post(actor, **kwargs):
    permission_verify(actor, "issue", "create")

    return issue_create(actor, **kwargs)


def issue_create(actor, key=None, issue_id=None, name=undefined, active=True, **kwargs):
    if "reporter" not in kwargs or kwargs["reporter"] == "": kwargs["reporter"] = actor
    if "assignee" not in kwargs or kwargs["assignee"] == "": kwargs["assignee"] = actor
    if "verifier" not in kwargs or kwargs["verifier"] == "": kwargs["verifier"] = actor

    if "status"   not in kwargs: kwargs["status"]   = "triage"
    if "priority" not in kwargs: kwargs["priority"] = 2
    if "severity" not in kwargs: kwargs["severity"] = 2

    issue = Issue()
    issue.created_by = build_user_key(actor)
    issue.privacy = "public"
    return issue_update(actor, issue=issue, active=True, name=name, **kwargs)


def issue_update(actor, issue_id=None, key=None, issue=None, summary=undefined, project=undefined, 
                 status=undefined, priority=undefined, severity=undefined, reporter=undefined, 
                 assignee=undefined, verifier=undefined, cc=undefined, depends_on=undefined, 
                 blocking=undefined, privacy=undefined, due_date=undefined, body="", send_mail=True, 
                 **args):
    issue = issue or (key or issue_key(issue_id)).get()
    header = "**" + actor.user.email() + "** on " + time.strftime("%c") + "\n\n"

    is_root = permission_is_root(actor)

    if not is_root and issue.privacy != "public" and \
            build_user_key(actor) not in issue.cc + [ issue.assignee, issue.reporter, issue.verifier ]:
        raise NotAllowedError()

    to_recipients = set([])
    if issue.assignee:
        to_recipients.add(issue.assignee)
    if issue.reporter:
        to_recipients.add(issue.reporter)
    if issue.verifier:
        to_recipients.add(issue.verifier)
    cc_recipients = set(issue.cc)

    if is_root or issue.privacy != "secure" or build_user_key(actor) in [ issue.assignee, issue.verifier ]:
        # Rewrite input types if necessary
        def fix_user(field):
            if is_undefined(field):
                return undefined
            if field == "":
                return undefined
            return build_user_key(field)
    
        reporter = fix_user(reporter)
        assignee = fix_user(assignee)
        verifier = fix_user(verifier)
    
        if is_defined(cc):
            cc = set([build_user_key(id) for id in re.split("[\\s,;]+", cc) if len(id) > 0])
    
        if is_defined(depends_on):
            depends_on = set([issue_key(id) for id in re.split("[\\s,;]+", depends_on) if len(id) > 0])
    
        if is_defined(blocking):
            blocking = set([issue_key(id) for id in re.split("[\\s,;]+", blocking) if len(id) > 0])

        if is_defined(due_date):
            if due_date == "":
                due_date = None
            else:
                if "timezoneoffset" in args:
                    offset = datetime.timedelta(minutes=int(args["timezoneoffset"]))
                    client_time = datetime.datetime.utcnow() - offset
                    parsed_time = lib.parsedatetime.Calendar().parse(due_date, client_time)
                    log.debug("client_time = %s" % client_time)
                else:
                    offset = datetime.timedelta(0)
                    parsed_time = lib.parsedatetime.Calendar().parse(due_date)

                if parsed_time[1] == 1:
                    due_date = datetime.datetime(*parsed_time[0][:3]) + offset
                else:
                    due_date = datetime.datetime(*parsed_time[0][:6]) + offset

        # Update all fields
        if is_defined(summary) and summary != issue.summary:
            header = header + "**Summary:** " + summary + "  \n"
            issue.summary = summary
            issue.summary_index = set(re.split("[^\\w\\d]+", summary.lower()))
    
        if is_defined(project) and project != issue.project:
            header = header + "**Project:** " + project + "  \n"
            issue.project = project

        if is_defined(status) and status != issue.status:
            if not status in issue_transitions:
                raise IllegalError("Status not recognized")
            if not status in issue_transitions[issue.status]:
                raise IllegalError("Status transition not allowed")
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
            to_recipients.add(reporter)
    
        if is_defined(assignee) and assignee != issue.assignee:
            header = header + "**Assignee:** " + assignee.id() + "  \n"
            issue.assignee = assignee
            to_recipients.add(assignee)
    
        if is_defined(verifier) and verifier != issue.verifier:
            header = header + "**Verifier:** " + verifier.id() + "  \n"
            issue.verifier = verifier
            to_recipients.add(verifier)
    
        if is_defined(cc) and cc != set(issue.cc):
            header = header + "**CC:** " + ", ".join([user.id() for user in cc]) + "  \n"
            issue.cc = list(cc)
            cc_recipients.update(cc)
    
        if is_defined(depends_on) and depends_on != set(issue.depends_on):
            header = header + "**Depends On:** " + ", ".join([str(iss.id()) for iss in depends_on]) + "  \n"
            issue.depends_on = list(depends_on)
    
        if is_defined(blocking) and blocking != set(issue.blocking):
            header = header + "**Blocking:** " + ", ".join([str(iss.id()) for iss in blocking]) + "  \n"
            issue.blocking = list(blocking)
    
        if is_defined(privacy) and privacy != issue.privacy:
            header = header + "**Privacy:** " + privacy + "  \n"
            issue.privacy = privacy

        if is_defined(due_date) and due_date != issue.due_date:
            header = header + "**Due Date:** " + str(due_date) + " UTC  \n"
            issue.due_date = due_date

    issue.score, issue.score_description = calculate_issue_score(issue)

    issue.text_index = set(issue.text_index) | \
                       set(issue.summary_index) | \
                       set(re.split("[^\\w\\d]+", body.lower()))

    issue.updated_by = build_user_key(actor)
    issue.put()

    issue.history = [ remark_create(actor, issue.key, body.strip(), header.strip()) ]

    if send_mail:
        settings = get_system_settings()
        if "host" in settings and settings["host"] and settings["host"] != "":
            host = settings["host"]
        else:
            host = "%s.appspot.com" % app_identity.get_application_id()
        message_id = "<issue-%s@%s>" % (issue.key.id(), app_identity.get_application_id())
        url = "http://%s/issues/%s" % (host, issue.key.id())
        text = "%s\n\n%s\n\n%s" % (header, body, url)
        html = "<div style='font-size: 0.8em'>%s</div><div>%s</div><div>%s</div>" % \
                    (lib.markdown.markdown(header), lib.markdown.markdown(body), url)
        if len(cc_recipients) > 0:
            mail.send_mail(sender=actor.user.email(),
                           to=[user.id() for user in to_recipients],
                           cc=[user.id() for user in cc_recipients],
                           reply_to=actor.user.email(),
                           subject="[" + str(issue.key.id()) + "] " + issue.summary,
                           body=text,
                           html=html,
                           headers={"In-Reply-To": message_id, "References":  message_id })
        else:
            mail.send_mail(sender=actor.user.email(),
                           to=[user.id() for user in to_recipients],
                           reply_to=actor.user.email(),
                           subject="[" + str(issue.key.id()) + "] " + issue.summary,
                           body=text,
                           html=html,
                           headers={"In-Reply-To": message_id, "References":  message_id })
        log.debug("Email sent to %s" % (to_recipients | cc_recipients))
        log.debug(text)

    return to_model(actor, issue)


def calculate_issue_score(issue):
    days_until_due = 30 if not issue.due_date else (issue.due_date - datetime.datetime.utcnow()).days

    score_priority = (6 - issue.priority) * 10                      # Range: 10 - 50
    score_due_date = 30 - max(min(30, days_until_due), -30)         # Range:  0 - 60

    return score_priority + score_due_date, \
            "= %s <sub>(Priority)</sub> + %s <sub>(Due Date)</sub>" % (score_priority, score_due_date)


def issue_refresh(actor, **kwargs):
    count = 0
    log.debug("Updating issue scores")
    for issue in Issue.query().filter(ndb.AND(Issue.due_date != None,
                                              Issue.status.IN(open_statuses))):
        score, score_description = calculate_issue_score(issue)
        if issue.score != score:
            count += 1
            log.debug("Updating score from %s to %s (%s)" % (issue.score, score, re.sub('<[^<]+?>', '', score_description)))
            issue.score = score
            issue.put()
    log.debug("Updated %s scores" % count)


def issue_deactivate(actor, issue_id=None, key=None, issue=None, **ignored):
    issue = issue_get(actor, issue_id, key, issue)
    issue.updated_by = build_user_key(actor)
    issue.active = False
    issue.put()


def issue_get(viewer, issue_id=None, key=None, issue=None, silent=False):
    result = issue or (key or issue_key(issue_id)).get()
    if result:
        if result.privacy == "public" or \
                build_user_key(viewer) in set(result.cc) | set([ result.assignee, result.reporter, result.verifier ]) or \
                permission_is_root(viewer):
            result.history = remark_list(viewer, result.key)
            return result
        elif silent:
            return None
        else:
            raise NotAllowedError()
    elif silent:
        return None
    else:
        raise NotFoundError()


def issue_load(viewer, issue_id):
    permission_verify(viewer, "issue", "read")
    return to_model(viewer, issue_get(viewer, issue_id))


def issue_list(viewer):
    permission_verify(viewer, "issue", "read")
    result = []
    for issue in Issue.query().filter():
        issue.history = []
        result.append(viewer, to_model(issue, get_related_issues=False))

    return result


def issue_search(viewer, simple=None, query=None, complex=None):
    permission_verify(viewer, "issue", "read")

    user_sort = None
    if not complex:
        if query:
            complex, user_sort = query_to_complex_search(query)
        else:
            # Status is open and assigned to me, or closing and verified by me.
            complex = { "boolean" : "or",
                        "sub"     : [ { "boolean" : "and",
                                        "sub"     : [ { "field"    : "status",
                                                        "operator" : "in",
                                                        "value"    : [ "triage", "assigned", "working" ] },
                                                      { "field"    : "assignee",
                                                        "operator" : "==",
                                                        "value"    : [ viewer ] } ] },
                                      { "boolean" : "and",
                                        "sub"     : [ { "field"    : "status",
                                                        "operator" : "in",
                                                        "value"    : [ "fixed", "rejected" ] },
                                                      { "field"    : "verifier",
                                                        "operator" : "==",
                                                        "value"    : [ viewer ] } ] } ] }

    result = []
    ndb_query, first_sort = complex_search_to_ndb_query(complex)
    if permission_is_root(viewer):
        if ndb_query:
            dataset = Issue.query().filter(ndb_query)
        else:
            dataset = Issue.query().filter()
    else:
        privacy_query = ndb.OR(Issue.privacy == "public",
                               Issue.assignee == build_user_key(viewer),
                               Issue.reporter == build_user_key(viewer),
                               Issue.verifier == build_user_key(viewer),
                               Issue.cc == build_user_key(viewer))
        if ndb_query:
            dataset = Issue.query().filter(ndb.AND(ndb_query, privacy_query))
        else:
            dataset = Issue.query().filter(privacy_query)

    # if first_sort:
    #     dataset = dataset.order(first_sort)

    # if user_sort:
    #     dataset = dataset.order(user_sort)

    # dataset = dataset.order(-Issue.score, -Issue.created)

    for issue in dataset:
        issue.history = []
        result.append(to_model(viewer, issue))

    return result


def query_to_complex_search(query):
    segments = []
    for i in range(int(query["c"])):
        segments.append({ "field"    : query["f" + str(i)],
                          "operator" : query["o" + str(i)],
                          "value"    : re.split("[\\s,;]+", query["v" + str(i)].strip()) })

    sort = None
    if "s" in query:
        sort = getattr(Issue, query["s"])

    return { "boolean" : query["b"], "sub" : segments }, sort


def complex_search_to_ndb_query(query):
    if not query:
        return None, None

    sort_order = None
    phrases = []
    for phrase in query["sub"]:
        if "boolean" in phrase:
            new_phrase, new_order = complex_search_to_ndb_query(phrase)
            if new_phrase:
                phrases.append(new_phrase)
                sort_order = sort_order or new_order
        elif phrase["field"] == "text":
            pass
        else:
            if phrase["field"] in [ "priority", "severity" ]:
                values = [ int(value) for value in phrase["value"] ]
            elif phrase["field"] in [ "created", "updated" ]:
                values = []
            elif phrase["field"] in [ "updated_by", "created_by", "assignee", "reporter", "verifier", "cc" ]:
                values = [ build_user_key(value) for value in phrase["value"] ]
            elif phrase["field"] in [ "summary_index", "text_index" ]:
                values = [ value.lower() for value in phrase["value"] ]
            else:
                values = phrase["value"]

            field = getattr(Issue, phrase["field"])
            subphrases = []
            if phrase["operator"] == "=" or phrase["operator"] == "==" or phrase["operator"] == "in":
                for value in values:
                    subphrases.append(field == value)
                if len(subphrases) > 0:
                    phrases.append(ndb.OR(*subphrases))

            elif phrase["operator"] == "!=":
                for value in values:
                    subphrases.append(field != value)
                if len(subphrases) > 0:
                    phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == ">":
                sort_order = field
                for value in values:
                    subphrases.append(field > value)
                if len(subphrases) > 0:
                    phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == ">=":
                sort_order = field
                for value in values:
                    subphrases.append(field >= value)
                if len(subphrases) > 0:
                    phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == "<":
                sort_order = field
                for value in values:
                    subphrases.append(field < value)
                if len(subphrases) > 0:
                    phrases.append(ndb.AND(*subphrases))

            elif phrase["operator"] == "<=":
                sort_order = field
                for value in values:
                    subphrases.append(field <= value)
                if len(subphrases) > 0:
                    phrases.append(ndb.AND(*subphrases))

    if len(phrases) > 0:
        if query["boolean"] == "or":
            return ndb.OR(*phrases), sort_order
        else:
            return ndb.AND(*phrases), sort_order
    else:
        return None, None


def to_model(viewer, issue, get_related_issues=True):
    if not issue:
        return None

    if get_related_issues:
        blocking   = { key.id(): to_model(viewer, issue_get(viewer, key=key, silent=True), False) 
                        for key in issue.blocking }
        depends_on = { key.id(): to_model(viewer, issue_get(viewer, key=key, silent=True), False)
                        for key in issue.depends_on }
    else:
        log.debug(issue)
        blocking   = { key.id(): None for key in issue.blocking }
        depends_on = { key.id(): None for key in issue.depends_on }

    cc = { key.id(): user_load(viewer, user_key=key, silent=True) for key in issue.cc }

    return { 'id'                : issue.key.id(),
             'summary'           : issue.summary,
             'history'           : issue.history,
             'project'           : issue.project,
             'status'            : issue.status,
             'priority'          : issue.priority,
             'severity'          : issue.severity,
             'reporter_email'    : issue.reporter.id(),
             'assignee_email'    : issue.assignee.id(),
             'verifier_email'    : issue.verifier.id(),
             'reporter'          : user_load(viewer, user_key=issue.reporter, silent=True),
             'assignee'          : user_load(viewer, user_key=issue.assignee, silent=True),
             'verifier'          : user_load(viewer, user_key=issue.verifier, silent=True),
             'cc'                : sorted(cc),
             'depends_on'        : sorted(depends_on),
             'blocking'          : sorted(blocking),
             'privacy'           : issue.privacy,
             'due_date'          : issue.due_date,
             'score'             : issue.score or 0,
             'score_description' : issue.score_description,
             'created_by'        : issue.created_by.id(),
             'created'           : issue.created,
             'updated_by'        : issue.updated_by.id(),
             'updated'           : issue.updated }


class Issue(ndb.Model):
    summary = ndb.StringProperty(required=True)
    summary_index = ndb.StringProperty(repeated=True)
    text_index = ndb.StringProperty(repeated=True)
    project = ndb.KeyProperty(kind=Project)
    status = ndb.StringProperty(required=True, choices=issue_transitions.keys())
    priority = ndb.IntegerProperty(required=True)
    severity = ndb.IntegerProperty(required=True)
    reporter = ndb.KeyProperty(kind='User', required=True)
    assignee = ndb.KeyProperty(kind='User', required=True)
    verifier = ndb.KeyProperty(kind='User', required=True)
    cc = ndb.KeyProperty(kind='User', repeated=True)
    depends_on = ndb.KeyProperty(kind='Issue', repeated=True)
    blocking = ndb.KeyProperty(kind='Issue', repeated=True)
    privacy = ndb.StringProperty(default="public", required=True, choices=["public", "private", "secure"])
    due_date = ndb.DateTimeProperty()
    score = ndb.IntegerProperty()
    score_description = ndb.StringProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)



