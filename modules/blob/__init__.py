import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import blob_private


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    blob_info = self.get_uploads('file')[0]
    blob_private.uploaded(str(blob_info.key()), self.request.GET["filename"])
    self.response.out.write(blob_info.key())


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    blob = blob_private.key(urllib.unquote(resource)).get()

    blob_info = blobstore.BlobInfo.get(blob.key.id())

    self.response.headers["Content-Disposition"] = str("attachment; filename=\"%s\"" % blob.filename)
    self.send_blob(blob_info)


def blob_create_url(viewer, filename=None, *args, **kwargs):
    return blobstore.create_upload_url('/blob/uploaded?' + urllib.urlencode({'filename': filename}))


def blob_claim(actor, blob_id, *args, **kwargs):
    blob_private.claim(actor, blob_id, None)
    return { 'blob_id' : blob_id }


def blob_scrub(*args, **kwargs):
    blob_private.scrub()


types = { "create" : blob_create_url }


handlers = [('/blob/uploaded', UploadHandler),
            ('/blob/download/([^/]+)?', ServeHandler)]


actions = { "claim/{blob_id}" : { "POST"   : { "method"   : blob_claim,
                                               "redirect" : "/blob/download/%(blob_id)s" } },
            "scrub"           : { "CRON"   : { "method"   : blob_scrub } } }

