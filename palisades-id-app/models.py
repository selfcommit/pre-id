# ndb Models live here. Documentation can be found at:
# https://cloud.google.com/appengine/docs/python/ndb/

from google.appengine.ext import ndb


class PublicKey(ndb.Model):
    keystring = ndb.StringProperty()
    note = ndb.StringProperty(default='None Provided')

    date_added = ndb.DateTimeProperty(auto_now_add=True)
    date_updated = ndb.DateTimeProperty(auto_now=True)


class Identity(ndb.Model):
    email = ndb.StringProperty()
    pre_keys = ndb.KeyProperty(PublicKey, repeated=True)
    provider_id = ndb.StringProperty()
    name = ndb.StringProperty()

    date_added = ndb.DateTimeProperty(auto_now_add=True)
    date_updated = ndb.DateTimeProperty(auto_now=True)
