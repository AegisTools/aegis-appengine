import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from users.users import user_load


def build_blob_key(blob_id):
    return blob_private.key(blob_id)


def blob_create(actor, filename, *args, **kwargs):
    return blob_private.create(actor, filename, *args, **kwargs)


def blob_claim(actor, blob_id, target):
    return blob_private.claim(actor, blob_id, target)


def blob_delete(actor, *args, **kwargs):
    return blob_private.delete(actor, *args, **kwargs)


def blob_load(actor, blob_id=None, blob_key=None):
    return blob_to_model(actor, blob_private.get(actor, blob_id=blob_id, blob_key=blob_key))


def blob_to_model(viewer, blob):
    return { 'id'            : blob.key.id(),
             'path'          : "/blob/download/%s" % blob.key.id(),
             'filename'      : blob.filename,
             'creator_email' : blob.created_by.id(),
             'creator'       : user_load(viewer, user_key=blob.created_by, silent=True) }


import blob_private

