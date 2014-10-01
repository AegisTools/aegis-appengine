import sys
import os
import logging

from google.appengine.ext import ndb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.users import build_user_key
from blob.blob import build_blob_key, blob_claim


log = logging.getLogger("remarks")


def remark_key(target_key, remark_id):
    return ndb.Key("Remark", remark_id, parent=target_key)


def remark_create(actor, target_key, text, subtext=None, blobs=[]):
    remark = Remark(parent=target_key)
    remark.target = target_key
    remark.text = text
    remark.subtext = subtext
    remark.blobs = [build_blob_key(blob) for blob in blobs]
    remark.created_by = build_user_key(actor)
    remark.put()

    for blob in blobs:
        blob_claim(actor, blob, remark.key)

    return to_model(remark)


def remark_get(target_key, remark_id):
    result = remark_key(target_key, remark_id).get()
    if result:
        return result
    else:
        raise NotFoundError()


def remark_list(viewer, target_key):
    result = []
    for remark in Remark.query(ancestor=target_key).filter(Remark.target == target_key).order(Remark.created):
        result.append(to_model(remark))

    return result


def to_model(remark):
    if not remark:
        return None

    return { 'key'        : remark.key.id(),
             'target'     : remark.target,
             'text'       : remark.text,
             'subtext'    : remark.subtext,
             'created_by' : remark.created_by.id(),
             'created'    : remark.created }


class Remark(ndb.Model):
    target = ndb.KeyProperty(required=True)
    text = ndb.TextProperty()
    subtext = ndb.TextProperty()
    blobs = ndb.KeyProperty(kind='Blob', repeated=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)



