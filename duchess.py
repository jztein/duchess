import webapp2
from jinja2 import Environment, PackageLoader
import urllib, urllib2, cookielib, urlparse
import base64
import cStringIO
import json
import time

from google.appengine.api import urlfetch
from google.appengine.ext import db

import Stalker

SHOP_URL = 'hedgehog.myshopify.com'
f = open('index.html')
html = f.read()
f.close()

# Datastore classes
class PidToFactorAndMin(db.Model):
    pid = db.StringProperty(required=True)
    factor = db.FloatProperty(required=True)
    min_price = db.FloatProperty(required=True)


# Request handlers


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
        print "Doing a dutch..."
        # 1. calculate lower price
        # 2. if lower price below minimum price, delete product
        # 3. else, PUT lower-priced product

        # fetch all products
        query = PidToFactorAndMin.all()
        pFMs = query.run(batch_size=1000)

        # limit: max 1000 products in the store supported
        pids, FMs = [], []
        for x in pFMs:
            pids.append(x.pid)
            FMs.append( (x.factor, x.min_price) )

        try:
            products = Stalker.getAllProducts()
            try:
                i = 0
                for product in products:
                    print ">>>", product['title']
                    pid = product['id']
                    idx = pids.index(str(pid))
                    factor, min_price = FMs[idx]
                    Stalker.changePrice(products, product['title'],
                                        discount=factor,
                                        min_price=min_price)
                    # shopify's api limit is avg 2 per second
                    if i % 2 == 1:
                        print "SLEEEPPiiingg ..... "
                        time.sleep(1)
                    i += 1
            except BaseException as e:
                print "ERROR in DUTCH PAGE: Couldn't change price"
        except BaseException as e:
            print "ERROR in DUTCH PAGE: couldn't get all products"

        print "Did a dutch"


GREEN_COLOR = "#ccffcc"
RED_COLOR = "#ffcccc"
YELLOW_COLOR = "#ddddaa"
SUBMIT_SUCCESS = "Submitted successfully!"
SUBMIT_FAIL = "ERROR: failed to submit. Check inputs."
SUBMIT_NA = "No submissions yet."

class AdminPage(webapp2.RequestHandler):

    def get(self):
        env = Environment(loader=PackageLoader('duchess', 'templates'))
        template = env.get_template('duke.html')

        products = Stalker.getAllProducts()
        for ps in products:
            print ps['id'], ps['title']
        print "=============="

        self.response.write(template.render(success=SUBMIT_NA,
                                            pid=None,
                                            factor=None,
                                            min_price=None,
                                            table_color=YELLOW_COLOR,
                                            products=products))


    def post(self):
        env = Environment(loader=PackageLoader('duchess', 'templates'))
        template = env.get_template('duke.html')
        products = Stalker.getAllProducts()

        try:
            pid = str(self.request.get('pid'))
            factor = float(self.request.get('factor'))
            min_price = float(self.request.get('min_price'))
        except:
            print "ERROR: could not get request params"
            self.response.write(template.render(success=SUBMIT_FAIL,
                                                pid=None,
                                                factor=None,
                                                min_price=None,
                                                table_color=RED_COLOR,
                                                products=products))
            return

        # try to get product
        req_status, pid_info = Stalker.getProductData(pid)
        # getting id failed = wrong id, don't continue - give ERROR page
        if req_status != 200:
            print "ERROR: Getting id failed"
            self.response.write(template.render(success=SUBMIT_FAIL,
                                                pid=None,
                                                factor=None,
                                                min_price=None,
                                                table_color=RED_COLOR,
                                                products=products))
            return


        if min_price <= 0 or factor <= 0 or factor >= 1:
            print "ERROR: bad input"
            self.response.write(template.render(success=SUBMIT_FAIL,
                                                pid=None,
                                                factor=None,
                                                min_price=None,
                                                table_color=RED_COLOR,
                                                products=products))
            return

        print "{{{{{{{{{{{{{{{{{{{{{"
        print pid_info
        print "}}}}}}}}}}}}}}}}}}}}}"

        
        pFM = PidToFactorAndMin(pid=pid, factor=factor, min_price=min_price)
        pFM.put()

        self.response.write(template.render(success=SUBMIT_SUCCESS,
                                            pid=pid,
                                            factor=factor,
                                            min_price=min_price,
                                            table_color=GREEN_COLOR,
                                            products=products))

application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/dutch', DutchPage),
        ('/duke', AdminPage),
], debug=True)

