import sys
import os
import logging
from google.appengine.api import mail

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import system_settings

log = logging.getLogger("issues")

def error_report(viewer, url=None, request_code=None, description=None, stack=None, **ignored):
    settings = system_settings.get_system_settings()

    sender = viewer.email()
    if "email_admin" in settings:
        sender = settings["email_admin"]
    
    body = "%s\n\nURL: %s\nRequest: %s\n\n%s" % (description, url, request_code, stack)
    log.debug("Sending Email to Admins from %s:" % sender)
    log.debug(body)
    mail.send_mail_to_admins(sender, "Aegis Error - %s" % url, body)


actions = { "report"     : { "POST"   : { "method"   : error_report,
                                          "redirect" : "/errors/reported" } } }



