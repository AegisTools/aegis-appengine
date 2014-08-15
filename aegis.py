import os
import urllib
import pkgutil
import logging
import json
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import modules

log = logging.getLogger("engine")


class RequestData:
    def __init__(self):
        self.user = None
        self.cache = {}
        self.known_loaders = {}
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    def load(self, type, id=None):
        if type not in self.known_loaders:
            raise Exception("Loader '%s' not found" % type)

        key = type + "/" + str(id)
        if key in self.cache:
            log.debug("Cache hit for %s: %s" % (type, id))
            return self.cache[key]

        loader = self.known_loaders[type]
        log.debug("Loading %s: %s (%s)" % (type, id, loader))
        self.cache[key] = loader(self.user, id)
        return self.cache[key]

    
class MainPage(webapp2.RequestHandler):

    known_modules = {}
    known_loaders = {}

    def put(self):
        self.execute()

    def post(self):
        self.execute()

    def delete(self):
        self.execute()

    def get(self):
        self.execute()


    def execute(self):
        request = RequestData()
        request.user = users.get_current_user()
        request.known_loaders = self.known_loaders

        if not request.user:
            request.user = users.User("test@test.com")
            # return self.redirect(users.create_login_url(self.request.uri))

        self.init()
        path = self.request.path
        if self.request.method != "GET":
            path = self.action(request) or path

        self.render(request, path)


    def init(self):
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
                for type in module.types:
                    self.known_loaders[modname + "/" + type] = module.types[type]
            else:
                log.debug("    No types")

            self.known_modules[modname] = module

        dependencies.difference_update(self.known_modules.keys())
        for dependency in dependencies:
            log.warn("Dependency on '%s' not satisfied, some features may be broken" % dependency)

        log.info("Module loading complete")


    def action(self, request):
        log.info("%s %s" % (self.request.method, self.request.path.strip("/")))
        path_segments = self.request.path.strip("/").split("/")
        module_name, path_segments = path_segments[0], path_segments[1:] or ["_index_"]
        module = self.known_modules[module_name]

        data = {}

        if hasattr(module, "actions") and self.request.method in module.actions:
            for pattern in module.actions[self.request.method]:
                action = module.actions[self.request.method][pattern]
                impl, keys = self.interpret_pattern(path_segments, pattern, action)
                if impl:
                    return impl(request.user, keys, data)

        raise Exception("action not found")


    def render(self, request, path):
        jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

        jinja.globals['load'] = request.load
        jinja.globals['json'] = self.json

        format = "html"
        if "format" in self.request.GET: format = self.request.GET["format"]
        path_segments = path.strip("/").split("/")
        module_name, path_segments = path_segments[0], path_segments[1:] or ["_index_"]
        module = self.known_modules[module_name]
        base_path = "modules/%s/templates" % module_name

        log.info("Rendering module '%s' path: %s (%s)" % (module_name, path_segments, format))

        keys = {}
        template = self.load_template(jinja, "%s/%s.%s" % (base_path, "/".join(path_segments), format))

        if not template and hasattr(module, "templates"):
            for template_pattern in module.templates:
                path, keys = self.interpret_pattern(path_segments, template_pattern, module.templates[template_pattern])
                if path:
                    template = self.load_template(jinja, "%s/%s.%s" % (base_path, path, format))
                    if template:
                        log.debug("keys: %s" % keys)
                        break;

        if not template and hasattr(module, "get_template"):
            path, keys = module.get_template(path_segments)
            if path:
                template = self.load_template(jinja, "%s/%s.%s" % (base_path, path, format))

        if not template:
            raise Exception("Template not found")

        self.response.write(template.render({
            'keys' : keys,
            'user' : request.user,
            'sign_out_url' : users.create_logout_url(self.request.uri) }))


    def interpret_pattern(self, segments, pattern, template):
        log.debug("Checking template '%s' against '%s'" % (pattern, "/".join(segments)))
        pattern_pieces = pattern.split("/")
        keys = {}
        path = []
        for key, value in map(None, pattern.split("/"), segments):
            if not (key and value):
                # Pattern is the wrong length
                return None, None
            elif key.startswith("{") and key.endswith("}"):
                keys[key[1:-1]] = value
            elif key == value:
                path.append(key)
            else:
                # Pattern doesn't match
                return None, None

        return (template or "/".join(path)), keys;


    def load_template(self, jinja, path):
        try:
            log.debug("Looking for template at %s" % path)
            return jinja.get_template(path)
        except jinja2.TemplateNotFound:
            return None


    def json(self, obj):
        date_handler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime)
            or isinstance(obj, datetime.date)
            else None)

        return json.dumps(obj, default=date_handler)


app = webapp2.WSGIApplication([('/.*', MainPage)], debug=True)

