import sys
import os
import logging
import urllib

from datetime import datetime, timedelta

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from users.users import build_user_key
from users.permissions import permission_verify
from common.errors import *


log = logging.getLogger("blob")


def create(actor, filename, *args, **kwargs):
    permission_verify(actor, "blob", "create")

    upload_url = blobstore.create_upload_url('/blob/uploaded?' + urllib.urlencode({'filename': filename}))
    log.debug("Created Upload URL: %s" % upload_url)
    return upload_url


def uploaded(blob_id, filename=None):
    log.debug("Creating blob %s (%s)" % (blob_id, filename))
    blob = Blob(key=key(blob_id))
    blob.filename = filename
    blob.put()
    return blob


def claim(actor, blob_id=None, blob_key=None, target=None):
    blob_key = blob_key or key(blob_id)
    log.debug("Claiming blob %s for %s (%s)" % (blob_key.id(), actor.key.id(), target))

    blob = blob_key.get()
    if not blob:
        raise NotFoundError()

    if blob.created_by:
        raise IllegalError("Blob has already been claimed")

    blob.target = target
    blob.created_by = actor.key
    blob.put()
    return blob


def delete(actor, blob_id=None, blob_key=None, blob=None, **ignored):
    permission_verify(actor, "blob", "delete")
    blob = get(alias_id, alias_key, alias)
    blobstore.delete(blob.key.id())
    blob.delete()


def get(actor, blob_id=None, blob_key=None, blob=None):
    permission_verify(actor, "blob", "read")

    result = blob or (blob_key or key(blob_id)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def key(blob_id):
    return ndb.Key(Blob, blob_id)


def scrub(age=timedelta(days=1)):
    query = Blob.query().filter(ndb.AND(Blob.created_by == None,
                                        Blob.created < datetime.now() - age))

    count = 0
    for blob in query.fetch(keys_only=True):
        log.debug("Expiring blob %s" % blob.id())
        blobstore.delete(blob.id())
        blob.delete()
        count += 1

    log.debug("Expired %s blobs" % count)


class Blob(ndb.Model):
    target = ndb.KeyProperty()
    filename = ndb.StringProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)


