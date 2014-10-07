import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from users.users import user_load


def build_blob_key(blob_id):
    return blob_private.key(blob_id)


def build_blob_keys(list):
    if isinstance(list, basestring):
        list = list.split(' ')

    return [build_blob_key(blob) for blob in filter(lambda a: a, list)]


def blob_create(actor, filename, *args, **kwargs):
    return blob_private.create(actor, filename, *args, **kwargs)


def blob_claim(actor, blob_id=None, blob_key=None, target=None):
    return blob_private.claim(actor, blob_id=blob_id, blob_key=blob_key, target=target)


def blob_delete(actor, *args, **kwargs):
    return blob_private.delete(actor, *args, **kwargs)


def blob_load(actor, blob_id=None, blob_key=None):
    return blob_to_model(actor, blob_private.get(actor, blob_id=blob_id, blob_key=blob_key))


def blob_to_model(viewer, blob):
    if not blob:
        return None

    return { 'id'            : blob.key.id(),
             'view_path'     : "/blob/view/%s" % blob.key.id(),
             'download_path' : "/blob/download/%s" % blob.key.id(),
             'filename'      : blob.filename,
             'creator_email' : blob.created_by.id(),
             'creator'       : user_load(viewer, user_key=blob.created_by, silent=True) }


import blob_private

