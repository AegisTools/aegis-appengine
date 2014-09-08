import logging
from google.appengine.api import mail

log = logging.getLogger("issues")

def error_report(viewer, url=None, request_code=None, description=None, stack=None, **ignored):
    body = "%s\n\nURL: %s\nRequest: %s\n\n%s" % (description, url, request_code, stack)
    log.debug("Sending Email to Admins:")
    log.debug(body)
    mail.send_mail_to_admins(viewer.email(), "Aegis Error - %s" % url, body)


templates = { "{issue_id}"      : "view",
              "{issue_id}/edit" : "edit",
              "edit/{issue_id}" : "edit" }


actions = { "report"     : { "POST"   : { "method"   : error_report,
                                          "redirect" : "/errors/reported" } } }



