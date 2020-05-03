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

          if urlparse(self.url).scheme=="":
            self.url = "http://" + self.url
          self.domain=urlparse(self.url).netloc
        else:
            self.stop("Error, -url is missing !")

        if self.tool.argHasValue("-deep"):
          val = self.tool.argValue("-deep")
          self.deep = int(val)
        else:
          #print("-deep flag not provided, setting deep to 2")
          self.deep = 2

        self.verbose = self.tool.argExist("-v")

        self.allowedExtensions=["html","php","htm"]

    def run(self):
        print("Starting scan of {} with deep {}".format(self.url,self.deep))
        listToScan=[self.url]
        listScanned=[]

        for i in range(self.deep):
            print("\nDeep {}/{}".format(i+1,self.deep))
            sys.stdout.flush()

            newListToScan=[]
            for url in listToScan:
                if self.verbose: 
                    print("SCANNING {}".format(url))
                else:
                    print(".",end="")
                sys.stdout.flush()
                newListToScan += self.extract(url)
                listScanned.append(self.removeSchemeUrl(url))

            for url in listScanned:
                while ("http://"+url) in newListToScan:
                    newListToScan.remove("http://"+url)
                while ("https://"+url) in newListToScan:
                    newListToScan.remove("https://"+url)

            listToScan=list(dict.fromkeys(newListToScan)) #removing duplicates
            if not self.verbose: print("")
            print("{} new urls found".format(len(listToScan)))

            if len(listToScan)==0: break
            
        print("\nRemaining url to scan : {}\n".format(len(listToScan)))

        if self.verbose: self.printFoundUrls(listScanned)
        self.writeFoundUrls(listScanned)

    def printFoundUrls(self,listUrls):
        print("Url found ({}):".format(len(listUrls)))
        listUrls.sort()
        for url in listUrls:
            print(url)
        print("")

    def writeFoundUrls(self,listUrls):
        fileName=urlparse(self.url).netloc + ".txt"
        f = open(fileName, "w")
        listUrls.sort()
        for url in listUrls:
            f.write(url + "\n")
        f.close()

    def removeSchemeUrl(self,url):
        u=urlparse(url)
        return u.netloc + u.path

    def cleanUrl(self, url):
        u=urlparse(url)
        return u.scheme + "://" + u.netloc + u.path

    def sameDomain(self, url):
        return urlparse(url).netloc == self.domain
    
    def extract(self, url):
        if self.isAFile(url): 
            print("File",url)
            return []
        try:
            req = requests.get(url, self.headers)
            soup = BeautifulSoup(req.content, 'html.parser')
            tab=soup.find_all('a', href=True)

            links=[]
            for u in tab:
                urlFound=u['href']
                if self.sameDomain(urlFound):
                    urlFound=self.cleanUrl(urlFound)
                    links.append(urlFound)
            links=list(dict.fromkeys(links)) #removing duplicates
            return links
        except:
            print("\nERROR\n")
            return []

    def isAFile(self,url):
        url=urlparse(url).path
        url=url.split("/")[-1]
        if "." not in url: return False

        url = url.split(".")[-1]
        if url in self.allowedExtensions: return False

        return True

    def stop(self, msg = ""):
        if msg != "": print(msg)
        exit(0)#stop the program

if __name__ == '__main__':
    prog = program(sys.argv)
    prog.run()