#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Webbapp2 documentation: https://webapp-improved.appspot.com/
import webapp2
from os import path
import jinja2
# https://developers.google.com/identity/toolkit/web/reference/
from identitytoolkit import gitkitclient
from google.appengine.ext import ndb

from models import Identity, PublicKey

server_config_json = path.join(path.dirname(path.realpath(__file__)), 'gitkit-server-config.json')
gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(server_config_json)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        hello_world = "Hello World!"
        template_values = {'hello': hello_world}

        template = jinja_environment.get_template('index.htm')
        # self.response.write('Hello world!')
        self.response.out.write(template.render(template_values))


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        pre_keys = None
        email = self.request.get('email')
        if email:
            i = Identity.query(Identity.email == email).get()
            if i:
                pre_keys = i.pre_keys

        template_values = {'pre_keys': pre_keys, 'email': email}

        template = jinja_environment.get_template('search.htm')
        # self.response.write('Hello world!')
        self.response.out.write(template.render(template_values))


class ServerHandler(webapp2.RequestHandler):
    def get(self):

        template = jinja_environment.get_template('search.htm')
        # self.response.write('Hello world!')
        self.response.out.write(template.render(template_values))


class SubmitKeyHandler(webapp2.RequestHandler):
    def get(self):
        gtoken = self.request.cookies.get('gtoken')
        if gtoken:
            gitkit_user = gitkit_instance.VerifyGitkitToken(gtoken)
        else:
            return webapp2.redirect_to('widget', mode='select')
        i = Identity()
        i = i.get_or_insert(gitkit_user.user_id, name=gitkit_user.name,
                            email=gitkit_user.email, provider_id=gitkit_user.provider_id)
        template_values = {'i': i}

        template = jinja_environment.get_template('submit_key.htm')

        self.response.out.write(template.render(template_values))

    def post(self):
        gtoken = self.request.cookies.get('gtoken')
        if gtoken:
            try:
                gitkit_user = gitkit_instance.VerifyGitkitToken(gtoken)
                key_text = self.request.get("key_text")
                note_text = self.request.get("note_text")
                i_key = ndb.Key('Identity', gitkit_user.user_id)
                i = i_key.get()
                p = PublicKey()
                p.keystring = key_text
                p.note = note_text
                p = p.put()
                i.pre_keys.append(p)
                i.put()
                return webapp2.redirect_to('public_keys')
            except Exception, e:
                raise e
        else:
            self.abort(403)

    def delete(self):
        gtoken = self.request.cookies.get('gtoken')
        if gtoken:
            gitkit_user = gitkit_instance.VerifyGitkitToken(gtoken)
            key_id = self.request.get("id")
            obj = ndb.Key(urlsafe=key_id)
            i = Identity.query(Identity.email == gitkit_user.email).get()
            list_of_keys = ndb.get_multi(i.pre_keys)
            print i.pre_keys
            print obj
            if obj in i.pre_keys:
                obj.delete()
                i.pre_keys.remove(obj)
                i.put()
        else:
            self.abort(403)
        self.response.out.write("it works!")


class WidgetHandler(webapp2.RequestHandler):
    def get(self):

        template_values = {}

        template = jinja_environment.get_template('widget.htm')
        self.response.out.write(template.render(template_values))


template_dir = path.dirname(__file__) + '/templates'
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir))

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainHandler, name='home'),
    webapp2.Route(r'/public_key', handler=SubmitKeyHandler, methods=['GET', 'POST', 'DELETE'], name='public_keys'),
    webapp2.Route(r'/search', handler=SearchHandler, name='search'),
    webapp2.Route(r'/widget', handler=WidgetHandler, name='widget'),
    # Advanced route example: (passes variables 'appname' and 'keyname' to class SingleHandler)
    # can be referenced throughout the app as route 'single'
    # webapp2.Route(r'/<appname>/<keyname>', handler=SingleHandler, name='single'),
], debug=True)
