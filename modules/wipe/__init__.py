import logging
from google.appengine.ext import db
from google.appengine.api import memcache

log = logging.getLogger("wipe")


dependencies = []


def wipe(viewer, keys, data):
     log.error("Wiping entire database")
     db.delete(db.Query(keys_only=True))
     memcache.flush_all()


actions = { "POST" : { None : wipe } }


