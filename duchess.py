import webapp2
from jinja2 import Environment, PackageLoader
import urllib, urllib2, cookielib, urlparse
import base64
import cStringIO
import json

from google.appengine.api import urlfetch

import shTalker

SHOP_URL = 'hedgehog.myshopify.com'
f = open('index.html')
html = f.read()
f.close()

class MainPage(webapp2.RequestHandler):
    def head(self):
        print "\n\n IN THE HEAD \n\n"
        self.get(self)

    def get(self):
        shTalker.getAllProducts()
        self.response.out.write(html)




application = webapp2.WSGIApplication([
        ('/', MainPage),
], debug=True)

