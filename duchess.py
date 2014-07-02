import webapp2
from jinja2 import Environment, PackageLoader
import urllib, urllib2, cookielib, urlparse
import base64
import cStringIO
import json
import time

from google.appengine.api import urlfetch

import Stalker

SHOP_URL = 'hedgehog.myshopify.com'
f = open('index.html')
html = f.read()
f.close()

class MainPage(webapp2.RequestHandler):
    def head(self):
        print "\n\n IN THE HEAD of Main Page\n\n"
        self.get(self)

    def get(self):
        self.response.out.write(html)


class DutchPage(webapp2.RequestHandler):
    def head(self):
        print "\n\n IN THE HEAD \n\n"
        self.get(self)

    def get(self):
        try:
            products = Stalker.getAllProducts()
            try:
                i = 0
                for product in products:
                    print ">>>", product['title']
                    Stalker.changePrice(products, product['title'],
                                        discount=0.10)
                    # shopify's api limit is avg 2 per second
                    if i % 2 == 1:
                        print "SLEEEEEEEPPiiingg ..... "
                        time.sleep(1)
                    i += 1
            except BaseException as e:
                print "ERROR in DUTCH PAGE: Couldn't change price"
                print e.read()
        except BaseException as e:
            print "ERROR in DUTCH PAGE: couldn't get all products"
            print e.read()

        print "Did a dutch"


application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/dutch', DutchPage),
], debug=True)

