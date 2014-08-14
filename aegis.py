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


    def get(self):
        self.init()
        self.execute("get")


    def execute(self, verb):
        user = users.get_current_user()
        if not user:
            return self.redirect(users.create_login_url(self.request.uri))

        JINJA_ENVIRONMENT.globals['load'] = self.load

        cache = {}
        log.debug(self.load("permissions/permission_list", 1, cache))
        log.debug(self.load("permissions/permission_list", 1, cache))

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def load(self, type, id, cache):
        if type not in self.known_loaders:
            raise Exception("Loader '%s' not found" % type)

        key = type + "/" + str(id)
        if key in cache:
            log.debug("Cache hit for %s: %s" % (type, id))
            return cache[key]

        loader = self.known_loaders[type]
        log.debug("Loading %s: %s (%s)" % (type, id, loader))
        cache[key] = loader(id)
        return cache[key]


app = webapp2.WSGIApplication([('/', MainPage)], debug=True)

