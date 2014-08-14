import os
import urllib
import pkgutil
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import modules

log = logging.getLogger("engine")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


RESPONSE_TYPE_HTML = 1
RESPONSE_TYPE_JSON = 2
RESPONSE_TYPE_XML  = 3


DATA_TYPE_USER = 1
DATA_TYPE_PERMISSION = 2


class MainPage(webapp2.RequestHandler):

    known_modules = {}
    known_loaders = {}

    cache = {}

    def init(self):
        user = users.get_current_user()
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))

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

        JINJA_ENVIRONMENT.globals['load'] = self.load



    def get(self):
        self.init()
        self.execute("get")


    def execute(self, verb):
        self.render(self.request.path, "html")

    def render(self, path, format):
        path_segments = path.strip("/").split("/")
        module_name, path_segments = path_segments[0], path_segments[1:] or ["_index_"]
        log.info("Rendering module '%s' path: %s (%s)" % (module_name, path_segments, format))
        module = self.known_modules[module_name]
        base_path = "modules/%s/templates" % module_name

        keys = {}
        template = self.load_template("%s/%s.%s" % (base_path, "/".join(path_segments), format))

        if not template and hasattr(module, "templates"):
            for template_pattern in module.templates:
                path, keys = self.interpret_template_pattern(path_segments, template_pattern, module.templates[template_pattern])
                if path:
                    template = self.load_template("%s/%s.%s" % (base_path, path, format))
                    if template:
                        log.debug("keys: %s" % keys)
                        break;

        if not template and hasattr(module, "get_template"):
            path, keys = module.get_template(path_segments)
            if path:
                template = self.load_template("%s/%s.%s" % (base_path, path, format))

        if not template:
            raise Exception("Template not found")

        self.response.write(template.render(keys or {}))


    def interpret_template_pattern(self, segments, pattern, template):
        log.debug("Checking template pattern: %s" % pattern)
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


    def load_template(self, path):
        try:
            log.debug("Looking for template at %s" % path)
            return JINJA_ENVIRONMENT.get_template(path)
        except jinja2.TemplateNotFound:
            return None


    def load(self, type, id):
        if type not in self.known_loaders:
            raise Exception("Loader '%s' not found" % type)

        key = type + "/" + str(id)
        if key in self.cache:
            log.debug("Cache hit for %s: %s" % (type, id))
            return self.cache[key]

        loader = self.known_loaders[type]
        log.debug("Loading %s: %s (%s)" % (type, id, loader))
        self.cache[key] = loader(id)
        return self.cache[key]


app = webapp2.WSGIApplication([('/.*', MainPage)], debug=True)

