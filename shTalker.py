import httplib
import urllib2, urllib, cookielib, urlparse
import base64, cStringIO, json

from google.appengine.api import urlfetch

f = open('admin.secret', 'r')
secrets = f.readlines()
f.close()

API_KEY = secrets[0]
SHARED_SECRET = secrets[1]
SHOP_URL = 'https://hedgehog.myshopify.com/admin'
GEN_SHOP_URL = 'hedgehog.myshopify.com'

auth = base64.b64encode("%s:%s" % (API_KEY, SHARED_SECRET))
HEADERS = { 'Authorization': "Basic " + auth }
JSON_HEADERS = { 'Authorization': "Basic " + auth,
                 'Content-Type': 'application/json'}

class UrlFetchException(IOError):
    pass

def addProduct():
    goat = json.dumps({"product": {"title": "Burton Custom Freestlye 151","body_html": "<strong>Good snowboard!</strong>","vendor": "Burton","product_type": "Snowboard","tags": "Barnes & Noble, John's Fav, \"Big Air\""}})

    headers['Content-Type'] = 'application/json'
    b = urlfetch.fetch(url="https://%s/admin/products.json" % SHOP_URL,
                       method=urlfetch.POST,
                       payload =goat,
                       headers=headers)
    print b.status_code
    print b.content

def getAllProducts():
    url = '%s/products.json' % SHOP_URL
    resp = urlfetch.fetch(url, headers=HEADERS)
    if resp.status_code == 200:
        jsonFile = cStringIO.StringIO(resp.content)
        # decoded json into dictionary-and-list format
        products = json.load(jsonFile)
        print products
        return products
    else:
        raise UrlFetchException('could not fetch in get all products')

