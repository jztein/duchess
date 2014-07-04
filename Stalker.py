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

BASELINE_PRICE = 0.01

class UrlFetchException(IOError):
    pass

class TestException(IOError):
    pass

class ShopifyException(ValueError):
    pass

def putProductData(jsonValue, pid):

    goat = json.dumps(jsonValue)

    b = urlfetch.fetch(url="%s/products/%s.json" % (SHOP_URL, pid),
                       method=urlfetch.PUT,
                       payload=goat,
                       headers=JSON_HEADERS)
    print "##### put product data"
    print b.status_code
    print "##### end: put product data"

def getProductData(pid):

    b = urlfetch.fetch(url="%s/products/%s.json" % (SHOP_URL, pid),
                       method=urlfetch.GET,
                       headers=HEADERS)
    print "##### GET product data"
    print b.status_code
    print "##### end: GET product data"

    return b.status_code, b.content


def deleteProduct(pid):
    b = urlfetch.fetch(url="%s/products/%s.json" % (SHOP_URL, pid),
                       method=urlfetch.DELETE,
                       headers=HEADERS)
    print "#^#^# deleting product"
    print b.status_code
    print "#^#^# END deleting product"


def testAddProduct():
    goat = json.dumps({"product": {"title": "Burton Custom Freestlye 151","body_html": "<strong>Good snowboard!</strong>","vendor": "Burton","product_type": "Snowboard","tags": "Barnes & Noble, John's Fav, \"Big Air\""}})

    b = urlfetch.fetch(url="%s/products.json" % SHOP_URL,
                       method=urlfetch.POST,
                       payload =goat,
                       headers=JSON_HEADERS)
    print "##### test add product"
    print b.status_code
    print b.content
    print "##### end test add product"

    products = getAllProducts()
    for product in products:
        if product['title'] == 'Burton Custom Freestlye 151':
            return

    raise TestException('did not add product correctly')
        

def getAllProducts():
    url = '%s/products.json' % SHOP_URL
    resp = urlfetch.fetch(url, headers=HEADERS)
    if resp.status_code == 200:
        jsonFile = cStringIO.StringIO(resp.content)
        # decoded json into dictionary-and-list format
        decoded = json.load(jsonFile)
        print "##### get all products"
        print "Num products:", len(decoded['products'])
        print "##### END get all products"
        return decoded['products']
    else:
        raise UrlFetchException('could not fetch in get all products')

# change price of product named $title to $newPrice
def changePrice(products, title, newPrice=-1, discount=0.10, min_price=0.01):
    gotProduct = False
    for product in products:
        if product['title'] == title:
            if newPrice == -1:
                newPrice = (1.0 - discount) * float(product['variants'][0]['price'])
            product['variants'][0]['price'] = newPrice
            newProduct = product
            gotProduct = True
            break

    if gotProduct:
        print ">> putting new price"
        pid = newProduct['id']

        if float(newPrice) < min_price:
            deleteProduct(pid)
            print "!!! Deleted product:", newProduct['title']
            return

        newJson = {}
        newJson['product'] = newProduct
        putProductData(newJson, pid)
    else:
        raise ShopifyException('could not change price of product %s' % title)
    
    # comment out if TEST-ing
    return

    # TEST: check stuff
    products = getAllProducts()
    for product in products:
        if product['title'] == title:
            if str(product['variants'][0]['price']) != "%.2f" % newPrice:
                print "ERROR"
                print "Wrong price:", product['variants'][0]['price']
                print "Expected price: %.2f" % newPrice
                raise TestException('price not altered correctly')
            else:
                print "New price:", product['variants'][0]['price']
