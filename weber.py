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
        list=self.getHyperLinks(self.url)

        for url in list:
            if self.sameDomain(url):
                cleanedUrl= self.cleanUrl(url)
                print(cleanedUrl)

    def cleanUrl(self, url):
        u=urlparse(url)
        return u.scheme + "://" + u.netloc + u.path

    def sameDomain(self, url):
        return urlparse(url).netloc == self.domain
    
    def getHyperLinks(self, url):
        req = requests.get(url, self.headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        tab=soup.find_all('a', href=True)

        list=[]
        for u in tab:
            try: list.append(u['href'])
            except IndexError: 1
        
        return list

    def stop(self, msg = ""):
        if msg != "": print(msg)
        exit(0)#stop the program

if __name__ == '__main__':
    prog = program(sys.argv)
    prog.run()