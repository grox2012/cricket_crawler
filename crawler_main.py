import time,urllib,urllib2,cookielib,re,random
from StringIO import StringIO
import gzip

# Read from crawler.config file(username, password, and phone numbers)
config_file = open("crawler.config","r")
config_list = config_file.read().splitlines()
config_file.close()

# Get login page with the token
site = "https://www.cricketwireless.com/myaccount/ImplLoginAction.do"
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
req = urllib2.Request(site, headers=hdr)
cookie = cookielib.MozillaCookieJar("cookie.txt")
handlers = [
    urllib2.HTTPSHandler(debuglevel=1),
    urllib2.HTTPCookieProcessor(cookie)
]
opener = urllib2.build_opener(*handlers)
try:
    page = opener.open(req)
except urllib2.HTTPError, e:
    print e.fp.read()
print "URL: " + page.geturl()
token_matcher = re.compile(r'\d+')
match = token_matcher.search(page.geturl())
token = ""
if match:
    token = match.group()
    print "Extracted token: " + token
else:
    print "Match token failed! Exit."
    exit()

time.sleep(1)

# Login the account
site = "https://www.cricketwireless.com/myaccount/loginPage.do"
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Host': 'www.cricketwireless.com',
       'Connection': 'keep-alive',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.8',
       'Content-Type': 'application/x-www-form-urlencoded',
       'Cache-Control': 'max-age=0',
       'Origin': 'https://www.cricketwireless.com',
       'Referer': 'https://www.cricketwireless.com/myaccount/ImplLoginAction.do?ecareAction=login&_CSRFToken=' + token,
       'Upgrade-Insecure-Requests': 1}
postdata=urllib.urlencode({
    '_stateParam':'eCareLocale.currentLocale=en_US__English',
    '_forwardName':'login',
    '_resetBreadCrumbs':'false',
    '_expandStatus':'',
    'redirectURL':'',
    'userName':config_list[0],
    'password':config_list[1],
    'ecareAction':'login',
    '_CSRFToken':token
})
req = urllib2.Request(url=site, headers=hdr, data=postdata)
try:
    page = opener.open(req, timeout=10)
except urllib2.HTTPError, e:
    print e.fp.read()
except Exception, ex:
    print ex
cookie.save(ignore_discard=True, ignore_expires=True)
print "URL: " + page.geturl()
print "page.Info():"
print page.info()
if page.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(page.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
fout = open("original.html", "w")
fout.write(data)
fout.close()

# Send ajax request to get data usage
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Host': 'www.cricketwireless.com',
       'Connection': 'keep-alive',
       'Accept': '*/*',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.8',
       'Content-Type': 'application/x-www-form-urlencoded',
       'Cache-Control': 'max-age=0',
       'Origin': 'https://www.cricketwireless.com',
       'Referer': 'https://www.cricketwireless.com/myaccount/secure/navigateMenu.do',
       'X-Requested-With': 'XMLHttpRequest'}
output = open("result.txt", "w")
for i in range(0, len(config_list) - 2):    
    site = "https://www.cricketwireless.com/myaccount/secure/loadSingleSubscriber.do?num=" + str(random.random())
    postdata=urllib.urlencode({
        'ctn': config_list[i+2]
    })
    req = urllib2.Request(url=site, headers=hdr, data=postdata)
    try:
        page = opener.open(req, timeout=10)
    except urllib2.HTTPError, e:
        print e.fp.read()
    except Exception, ex:
        print ex
    if page.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(page.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    fout = open("data" + str(i) + ".html", "w")
    fout.write(data)
    fout.close()
    data_matcher = re.compile(r"\d+\.?\d*\w+ of 2.5GB Used")
    match = data_matcher.search(data)
    if match:
        print config_list[i+2]
        print match.group()
        output.write(config_list[i+2] + " " + match.group() + "\n")
    else:
        print "Match failed for " + config_list[i+2]
output.close()
