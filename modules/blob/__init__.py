import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import blob_private


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    blob_info = self.get_uploads('file')[0]
    blob_private.uploaded(str(blob_info.key()))
    self.response.out.write(blob_info.key())


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)


def blob_create_url(*args, **kwargs):
    return blobstore.create_upload_url('/blob/uploaded')


def blob_claim(actor, blob_id, *args, **kwargs):
    blob_private.claim(actor, blob_id, None)
    return { 'blob_id' : blob_id }


handlers = [('/blob/uploaded', UploadHandler),
            ('/blob/download/([^/]+)?', ServeHandler)]


types = { "create" : blob_create_url }


actions = { "claim/{blob_id}" : { "POST"   : { "method"   : blob_claim,
                                               "redirect" : "/blob/download/%(blob_id)s" } } }

