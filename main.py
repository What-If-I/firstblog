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
import os

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname('__file__'), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Posts(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


class MainPage(Handler):
    def get(self):
        posts = Posts.all().order('-created').fetch(limit=10)
        self.render('index.html', posts=posts)


class PostView(Handler):
    def get(self, post_id):
        post_id = int(post_id)
        post = Posts.get_by_id(int(post_id))
        if post:
            self.render("post.html", title="Post", post=post)
        else:
            self.error(404)
            self.write("404 Page not found")


class SubmitPostPage(Handler):
    def render_front(self, title="", content="", error=""):
        self.render("submit.html", title=title, content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('subject')
        content = self.request.get('content')

        if title and content:
            post = Posts(title=title, content=content)
            post.put()
            post_id = post.key().id()
            return self.redirect("/blog/%s" % post_id)
        else:
            error = "We need both title and artwork!"
            self.render_front(title=title, content=content, error=error)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/', MainPage),
    ('/blog/newpost', SubmitPostPage),
    ('/blog/newpost/', SubmitPostPage),
    webapp2.Route(r'/blog/<post_id:\d+>', handler=PostView)
], debug=True)
