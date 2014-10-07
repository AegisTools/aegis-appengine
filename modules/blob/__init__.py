import re
import urllib
import logging
import json

from datetime import timedelta

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import blob_private


log = logging.getLogger("blob")


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    result = {}
    for blob_info in self.get_uploads('file'):
      log.debug(blob_info.filename)
      blob_private.uploaded(str(blob_info.key()), blob_info.filename)
      result[str(blob_info.key())] = blob_info.filename

    self.response.out.write(json.dumps(result))


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    blob = blob_private.key(urllib.unquote(resource)).get()

    blob_info = blobstore.BlobInfo.get(blob.key.id())

    self.response.headers["Content-Disposition"] = str("attachment; filename=\"%s\"" % blob.filename)
    self.send_blob(blob_info)


class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    blob = blob_private.key(urllib.unquote(resource)).get()

    blob_info = blobstore.BlobInfo.get(blob.key.id())

    self.response.headers["Content-Disposition"] = str("inline; filename=\"%s\"" % blob.filename)
    self.send_blob(blob_info)


def blob_create_url(viewer, *args, **kwargs):
    return blobstore.create_upload_url('/blob/uploaded')


def blob_claim(actor, blob_id, *args, **kwargs):
    blob_private.claim(actor, blob_id, None)
    return { 'blob_id' : blob_id }


blob_scrub_regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def blob_scrub(actor, age=None, *args, **kwargs):
    if age:
        parts = blob_scrub_regex.match(age)
        if parts:
            parts = parts.groupdict()
            time_params = {}
            for (name, param) in parts.iteritems():
                if param:
                    time_params[name] = int(param)
            blob_private.scrub(timedelta(**time_params))
            return

    blob_private.scrub()


types = { "create" : blob_create_url }


handlers = [('/blob/uploaded', UploadHandler),
            ('/blob/download/([^/]+)?', DownloadHandler),
            ('/blob/view/([^/]+)?', ViewHandler)]


actions = { "claim/{blob_id}" : { "POST"   : { "method"   : blob_claim,
                                               "redirect" : "/blob/download/%(blob_id)s" } },
            "scrub"           : { "CRON"   : { "method"   : blob_scrub } } }

