import os
import urllib
import pkgutil
import logging
import json
import datetime
import string
import random
import traceback

import lib.markdown


from google.appengine.api import users

import jinja2
import webapp2

import modules
from modules.common.errors import *
from modules.users.users import user_load_raw, user_create

log = logging.getLogger("engine")


jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


known_modules = {}
known_loaders = {}
custom_handlers = []

dependencies = set()

for importer, modname, ispkg in pkgutil.iter_modules(modules.__path__):
    log.info("Importing module %s" % modname)
    module = getattr(__import__(modules.__name__ + "." + modname), modname)

    if hasattr(module, "dependencies"):
        log.debug("    Found dependencies: %s" % module.dependencies)
        dependencies.update(module.dependencies)
    else:
        log.debug("    No dependencies")

    if hasattr(module, "types"):
        log.debug("    Found types: %s" % module.types)
        for loader_type in module.types:
            known_loaders[modname + "/" + loader_type] = module.types[loader_type]
    else:
        log.debug("    No types")

    if hasattr(module, "handlers"):
        for handler in module.handlers:
            log.debug("    Custom Handler: %s" % handler[0])
            custom_handlers.append(handler)

    known_modules[modname] = module

dependencies.difference_update(known_modules.keys())
for dependency in dependencies:
    log.warn("Dependency on '%s' not satisfied, some features may be broken" % dependency)

log.info("Module loading complete")


class RequestData:
    def __init__(self):
        self.user = None
        self.cache = {}
        self.redirection = None

    def load(self, type, *args, **kwargs):
        if type not in known_loaders:
            raise Exception("Loader '%s' not found" % type)

        # key = type + "/" + str(id)
        # if key in self.cache:
        #     log.debug("Cache hit for %s: %s" % (type, id))
        #     return self.cache[key]

        loader = known_loaders[type]
        log.debug("Loading %s: %s %s (%s)" % (type, args, kwargs, loader))
        # self.cache[key] = loader(self.user, *args, **kwargs)
        # return self.cache[key]
        try:
            return loader(self.user, *args, **kwargs)
        except Exception as ex:
            logging.exception("Loader Failed")
            raise

    def local_time(self, target):
        return target - datetime.timedelta(minutes=self.timezoneoffset)

    def redirect(self, url):
        self.redirection = url


class MainPage(webapp2.RequestHandler):

    def put(self):
        self.execute()

    def post(self):
        self.execute()

    def delete(self):
        self.execute()

    def get(self):
        self.execute()


    def execute(self):
        request_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
        try:
            request = RequestData()
            request.known_loaders = known_loaders
            request.user = users.get_current_user()

            try:
                request.user_obj = user_load_raw(users.get_current_user())
            except:
                request.user_obj = users.get_current_user()
                log.warn("User does not exist")
                if users.is_current_user_admin():
                    user_create(users.get_current_user(), user_id = users.get_current_user().email())
                    request.user_obj = user_load_raw(users.get_current_user())
                    log.warn("User created for admin")

            if "timezoneoffset" in self.request.cookies:
                request.timezoneoffset = int(self.request.cookies.get("timezoneoffset"))
            else:
                request.timezoneoffset = 0
    
            method = self.request.method
            if "_method_" in self.request.params:
                method = self.request.params["_method_"]

            path = self.request.path.strip("/")
            if path.startswith("cron/"):
                path = path[len("cron/"):]
                method = "CRON"

            if path.startswith("json/"):
                path = path[len("json/"):]
                request.format = "json"

            if method != "GET":
                redirect = self.action(method, path, request)

                if method == "CRON":
                    return

                xsrf = self.refresh_xsrf_cookie(True)
                if method == "CRON":
                    return
                elif redirect:
                    return self.redirect(redirect)
                else:
                    return
            else:
                xsrf = self.refresh_xsrf_cookie()
    
            self.render(request, path, xsrf)

        except Exception as e:
            log.exception(request_code)

            if not hasattr(e, "code"):
                e.code = 500
            e.request_code = request_code
            e.url = self.request.path
            e.stack = traceback.format_exc()

            self.response.set_status(e.code)
            self.render(request, "errors/%s" % e.code, self.refresh_xsrf_cookie(), \
                    { 'code':         e.code,
                      'request_code': e.request_code })

    def validate_xsrf_cookie(self):
        if not "_xsrf_" in self.request.params:
            log.warn("XSRF Failure")
            raise NotAllowedError()

        if not "xsrf" in self.request.cookies:
            log.warn("XSRF Failure")
            raise NotAllowedError()

        if self.request.cookies["xsrf"] != self.request.params["_xsrf_"]:
            log.warn("XSRF Failure")
            raise NotAllowedError()

        log.debug("XSRF Token Matched: %s" % self.request.params["_xsrf_"])


    def refresh_xsrf_cookie(self, force_replace=False):
        if force_replace or not "xsrf" in self.request.cookies:
            xsrf = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
            log.debug("New XSRF Token: %s" % xsrf)
        else:
            xsrf = self.request.cookies["xsrf"]
            log.debug("XSRF Token: %s" % xsrf)

        expires = datetime.datetime.now() + datetime.timedelta(hours=3)
        self.response.set_cookie("xsrf", xsrf, expires=expires, path="/", httponly=True, overwrite=True)
        return xsrf


    def action(self, method, path, request):
        format = self.get_data_type("Content_Type", request)

        log.info("%s %s : %s" % (method, path, format))

        path_segments = path.split("/")
        module_name, path_segments = path_segments[0], path_segments[1:]
        module = known_modules[module_name]

        if format == "json":
            if self.request.body == "":
                data = {}
            else:
                log.debug(self.request.body)
                data = json.loads(self.request.body)
        else:
            if method != "CRON":
                self.validate_xsrf_cookie()
            data = dict(dict(self.request.GET).items() + dict(self.request.POST).items())
            log.debug("GET:  %s" % dict(self.request.GET))
            log.debug("POST: %s" % dict(self.request.POST))

        data = dict(data.items() + self.request.cookies.items())

        if hasattr(module, "actions"):
            for pattern in module.actions:
                if pattern and method in module.actions[pattern]:
                    action = module.actions[pattern][method]
                    match = interpret_pattern(path_segments, pattern)
                    if match:
                        keys = match[1]
                        break
            else:
                if None in module.actions and method in module.actions[None]:
                    action = module.actions[None][method]
                    keys = {}
                else:
                    raise Exception("action not found")

            args = dict(keys.items() + data.items())
            log.debug("Performing action: %s(%s)" % (action, args))
            result = action["method"](request.user_obj, **args)
            if "redirect" in action:
                if action["redirect"]:
                    try:
                        return action["redirect"] % result
                    except:
                        return action["redirect"]
                else:
                    self.response.write(result)
                    return None
            else:
                return self.request.url

        raise Exception("action not found")


    def get_data_type(self, header, request):
        type = "html"
        if header in self.request.headers and self.request.headers[header].startswith("application/"):
            type = self.request.headers[header][len("application/"):]

        if "format" in self.request.GET:
            type = self.request.GET["format"]

        if "_format_" in self.request.GET:
            type = self.request.GET["format"]

        if type == "x-www-form-urlencoded":
            type = "html"

        if request and hasattr(request, "format"):
            type = request.format

        return type



    def render(self, request, path, xsrf, error=None):
        format = self.get_data_type("Accept", request)
        template, keys = self.find_template(format, path)
        if format == "html" and not template:
            format = "md"
            template, keys = self.find_template("md", path)

        if template:
            obj = {'query'        : self.request.GET,
                   'keys'         : keys,
                   'user'         : users.get_current_user(),
                   'is_admin'     : users.is_current_user_admin(),
                   'sign_out_url' : users.create_logout_url(path),
                   'load'         : request.load,
                   'local_time'   : request.local_time,
                   'redirect'     : request.redirect,
                   'xsrf'         : xsrf,
                   'error'        : error }
            log.debug("Rendering template %s: %s", template, obj)
            content = template.render(obj)

            if request.redirection:
                return self.redirect(request.redirection)

            if format == "md":
                content = format_markdown(content)

            self.response.write(content)
        else:
            log.error("Template not found")
            raise NotFoundError()


    def find_template(self, format, original_path):
        path_segments = original_path.split("/")
        module_name, path_segments = path_segments[0], path_segments[1:]
        template = None

        log.info("Rendering module '%s' path: %s (%s)" % (module_name, path_segments, format))

        if module_name != "" and module_name in known_modules:
            module = known_modules[module_name]
            base_path = "modules/%s/templates" % module_name
            keys = {}

            if path_segments:
                template = load_template("%s/%s.%s" % (base_path, "/".join(path_segments), format))
                if not template:
                    template = load_template("%s/%s/_index_.%s" % (base_path, "/".join(path_segments), format))
            else:
                template = load_template("%s/_index_.%s" % (base_path, format))

            if not template and hasattr(module, "templates"):
               for template_pattern in module.templates:
                    match = interpret_pattern(path_segments, template_pattern, module.templates[template_pattern])
                    if match:
                        path, keys = match
                        if path == "": path = "_index_"
                        template = load_template("%s/%s.%s" % (base_path, path, format))
                        if template:
                            log.debug("keys: %s" % keys)
                            break;

            if not template and hasattr(module, "get_template"):
                path, keys = module.get_template(path_segments)
                if path:
                    if path == "": path = "_index_"
                    template = load_template("%s/%s.%s" % (base_path, path, format))

        if not template:
            keys = {}
            if original_path == "":
                template = load_template("templates/_index_.%s" % format)
            else:
                template = load_template("templates/%s.%s" % (original_path.strip("/"), format))
                if not template:
                    template = load_template("templates/%s/_index_.%s" % (original_path.strip("/"), format))

        if template:
            return template, keys
        else:
            return None, None


def interpret_pattern(segments, pattern, template=None):
    log.debug("Checking template '%s' against '%s'" % (pattern, "/".join(segments)))
    if pattern == None:
        pattern_pieces = []
    else:
        pattern_pieces = pattern.split("/")

    keys = {}
    path = []
    last_key = None
    for i in range(len(pattern_pieces)):
        key = pattern_pieces[i]
        if key == "*":
            keys[last_key] = segments[i-1:]
            return (template or "/".join(path)), keys
        elif len(segments) <= i:
            # Pattern doesn't match
            return None
        elif key.startswith("{") and key.endswith("}"):
            last_key = key[1:-1]
            keys[last_key] = urllib.unquote(segments[i])
        elif key == segments[i]:
            path.append(key)
        else:
            return None

    if len(segments) != len(pattern_pieces):
        return None

    return (template or "/".join(path)), keys


def load_template(path):
    try:
        log.debug("Looking for template at %s" % path)
        return jinja.get_template(path)
    except jinja2.TemplateNotFound:
        return None


def format_json(obj):
    date_handler = lambda obj: (
        obj.isoformat()
        if isinstance(obj, datetime.datetime)
        or isinstance(obj, datetime.date)
        else None)

    return json.dumps(obj, 
                      default=date_handler, 
                      sort_keys=True,
                      indent=4)


def format_markdown(content):
    if not content:
        return ""

    return lib.markdown.markdown(content)


def build_date(year=None, month=None, day=None):
    if year:
        date = datetime.date(int(year), int(month), int(day))
    else:
        date = datetime.date.today()

    week = date - date.resolution * (date.isoweekday() % 7)

    def format_date(date):
        return { 'year'        : date.year,
                 'month'       : date.month,
                 'day'         : date.day,
                 'day_of_week' : date.strftime("%A"),
                 'month_abbrv' : date.strftime("%b"),
                 'path'        : date.strftime("%Y/%m/%d") }

    result                  = format_date(date)
    result["yesterday"]     = format_date(date - date.resolution)
    result["tomorrow"]      = format_date(date + date.resolution)
    result["this_week"]     = format_date(week)
    result["this_week_end"] = format_date(week + date.resolution * 6)
    result["last_week"]     = format_date(week - date.resolution * 7)
    result["next_week"]     = format_date(week + date.resolution * 7)

    return result



jinja.globals['json']       = format_json
jinja.globals['markdown']   = format_markdown
jinja.globals['build_date'] = build_date

custom_handlers.append(('/.*', MainPage))

app = webapp2.WSGIApplication(custom_handlers, debug=True)

