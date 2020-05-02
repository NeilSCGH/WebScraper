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
          val = self.tool.argValue("-url")
          self.url = val
          self.domain=urlparse(self.url).netloc
        else:
            self.stop("Error, -url is missing !")

    def run(self):
        listToScan=self.extract(self.url)
        listScanned=[self.url]
        
        deep=1
        for i in range(deep):
            newListToScan=[]
            for url in listToScan:
                print("SCANNING",url)
                newListToScan += self.extract(url)
                listScanned.append(url)
            listToScan=list(dict.fromkeys(newListToScan)) #removing duplicates

        print("To scan")
        print(listToScan)
        print("\nScanned")
        print(listScanned)

    def cleanUrl(self, url):
        u=urlparse(url)
        return u.scheme + "://" + u.netloc + u.path

    def sameDomain(self, url):
        return urlparse(url).netloc == self.domain
    
    def extract(self, url):
        req = requests.get(url, self.headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        tab=soup.find_all('a', href=True)

        links=[]
        for u in tab:
            urlFound=u['href']
            if self.sameDomain(urlFound):
                urlFound=self.cleanUrl(urlFound)
                try: links.append(urlFound)
                except IndexError: 1
        links=list(dict.fromkeys(links)) #removing duplicates
        return links

    def stop(self, msg = ""):
        if msg != "": print(msg)
        exit(0)#stop the program

if __name__ == '__main__':
    prog = program(sys.argv)
    prog.run()