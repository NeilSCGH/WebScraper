import sys
import os
import requests
from bs4 import BeautifulSoup
import wget
from urllib.parse import urlparse
from lib.tools import *

class program():
    def __init__(self,args):
        self.tool = tools(args)
        self.setup(args)#process the arguments

        # Set headers
        self.headers = requests.utils.default_headers()
        self.headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

    def setup(self,args):
        if self.tool.argHasValue("-url"): 
            self.url = self.tool.argValue("-url")
        else: self.stop("Error, -url is missing !")

        if urlparse(self.url).scheme == "": 
            self.url = "http://" + self.url

        self.data=urlparse(self.url)
        
        self.deep = int(self.tool.tryToGetValue("-deep",2))
        self.outputFileName = self.tool.tryToGetValue("-o","")
        self.cookie = self.tool.tryToGetValue("-c","")
        self.allowedExtensions=["html", "php", "htm"]

        self.otherSubDomains=[]

        self.urlsToScan=[self.url]
        self.urlsFound=[self.url]

    def run(self):
        print("Starting scan of {} with deep {}".format(self.url,self.deep))

        for i in range(self.deep):
            print("\nDeep {}/{}".format(i+1, self.deep))

            newUrls = self.scan()#will scan self.urlsToScan

            newUrls = self.removeDuplicates(newUrls)
            newUrls = self.filter(newUrls)

            self.urlsToScan = newUrls[:]
            self.urlsFound += newUrls

            if len(self.urlsToScan)==0: 
                break

        print("\n{} urls found but not scanned".format(len(self.urlsToScan)))

        print("\nUrls found are:")
        self.printList(self.urlsFound)

        self.otherSubDomains=self.removeDuplicates(self.otherSubDomains)
        print("\nOther subdomains are:")
        self.printList(self.otherSubDomains)

    def printList(self,tab):
        tab.sort()
        for elem in tab:
            print(elem)
        
    def removeDuplicates(self,tab):
        return list(dict.fromkeys(tab))

    def filter(self, tab):
        newTab=self.filterDomain(tab)
        newTab=self.filterAlreadyFound(newTab)
        return newTab

    def filterDomain(self, tab):
        ourDomain = self.getDomain(self.url)
        ourMainDomain = self.getMainDomain(self.url)

        sameDomain=[]
        otherSubDomain=[]
        for url in tab:
            if self.getDomain(url) == ourDomain:
                sameDomain.append(url)
            elif self.getMainDomain(url) == ourMainDomain:
                self.otherSubDomains.append(url)
        return sameDomain

    def filterAlreadyFound(self, tab):
        newTab=[]

        for url in tab:
            if url not in self.urlsFound: #attention avec http vs https
                newTab.append(url)
        return newTab
        
    def getMainDomain(self, url): #www.example.com will become example.com
        domain = self.getDomain(url)
        data = domain.split(".")[-2:]
        return data[0] + "." + data[1]
        
    def getDomain(self, url):
        return urlparse(url).netloc

    def scan(self):
        newUrls=[]
        for url in self.urlsToScan:
            print("SCANNING",url)
            newUrls += self.scanUrl(url)
        return newUrls

    def scanUrl(self,url):
        linksFound=[]
        
        hrefs=self.getHrefsUrl(url)

        for u in hrefs:
            link=u['href']
            link=self.completeUrl(link)
            link=self.cleanUrl(link)

            linksFound.append(link)

        return linksFound

    def getHrefsUrl(self,url):
        try:
            req = requests.get(url, self.headers, cookies={'PHPSESSID': self.cookie})
            soup = BeautifulSoup(req.content, 'html.parser')
            return soup.find_all('a', href=True)
        except:
            print("Error with",url)
            return []

    def completeUrl(self,url):
        if urlparse(url).netloc=="":
            url = (self.data).scheme + "://" + (self.data).netloc + url
        return url

    def cleanUrl(self, url):
        data=urlparse(url)
        newUrl = url#data.scheme + "://" + data.netloc + data.path

        if newUrl[-1]=="/": 
            newUrl=newUrl[:-1]

        if "#" in newUrl: 
            newUrl=newUrl.split("#")[0]

        return newUrl

    def stop(self, msg = ""):
        if msg != "": print(msg)
        exit(0)#stop the program

if __name__ == '__main__':
    prog = program(sys.argv)
    prog.run()