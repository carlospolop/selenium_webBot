from bs4 import BeautifulSoup as b
import lxml
import urllib2 as urllib
import time
def grabProxiesHttp():
    site = 'https://free-proxy-list.net/'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.Request(site,headers=hdr) #sending requests with headers
    url = urllib.urlopen(req).read() #opening and reading the source code
    html = b(url,"lxml")                #structuring the source code in proper format
    rows = html.findAll("tr")       #finding all rows in the table if any.
    proxies = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text for ele in cols]
        try:
            ipaddr = cols[0]        #ipAddress which presents in the first element of cols list
            portNum = cols[1]       #portNum which presents in the second element of cols list
            proxy = ipaddr+":"+portNum  #concatinating both ip and port
            portName = cols[6]          #portName variable result will be yes / No
            if portName == "no":
                proxies.append(str(proxy))
                #proxies.append(str(proxy)+":http") #if yes then it appends the proxy with https
            #else:
                #proxies.append(str(proxy)+":https") #if no then it appends the proxy with http
        except:
            pass

    #for j in proxies:
     #   print(j)
    return proxies

#grabProxiesHttp()
