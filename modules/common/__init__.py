from google.appengine.ext import ndb
from google.appengine.api import memcache


def wipe(key):
    key.delete()
    ndb.delete_multi(ndb.Query(ancestor=key).iter(keys_only = True))
    memcache.flush_all()

