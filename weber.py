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
        #Help
        if self.tool.argExist("-h") or self.tool.argExist("-help"): 
            self.help()

        if self.tool.argHasValue("-url"): 
            self.url = self.tool.argValue("-url")
        else: self.stop("Error, -url is missing !")

        if urlparse(self.url).scheme == "": self.url = "http://" + self.url

        self.domain=urlparse(self.url).netloc
        self.deep = int(self.tool.tryToGetValue("-deep",2))
        self.outputFileName = self.tool.tryToGetValue("-o","")
        self.cookie = self.tool.tryToGetValue("-c","")
        self.verbose = self.tool.argExist("-v")
        self.allowedExtensions=["html", "php", "htm"]

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
                    print("SCANNING {}".format(urlparse(url).path))
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
        
        nbToScan=len(listToScan)
        if nbToScan!=0: print("\n{} Urls not scanned!".format(nbToScan),end='')

        listToSave=listScanned[:]
        for i in range(len(listToScan)):
            listToSave.append(self.removeSchemeUrl(listToScan[i]))

        if self.verbose: self.printFoundUrls(listToSave)
        self.writeFoundUrls(listToSave)

    def printFoundUrls(self,listUrls):
        print("\nUrls found ({}):".format(len(listUrls)))
        listUrls.sort()
        for url in listUrls:
            print(url)
        print("")

    def writeFoundUrls(self,listUrls):
        if self.outputFileName=="":
            fileName=urlparse(self.url).netloc + ".txt"
        else:
            fileName=self.outputFileName

        f = open(fileName, "w")
        listUrls.sort()
        for url in listUrls:
            f.write(url + "\n")
        f.close()
        print("All urls found are in the file {} !\n".format(fileName))

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
            req = requests.get(url, self.headers, cookies={'PHPSESSID': self.cookie})
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

    def help(self):
        print("")
        print("Usage: python weber.py -url URL [-deep x] [-v] [-o fileName] [-c cookie]")
        print("")
        print("Options:")
        print("    -url URL        The url to scan")
        print("    -deep x         Depth of scan, number of iteration (Optional, by default set to 2)")
        print("    -v              Enable verbose during scan (Optional)")
        print("    -o fileName     Output all urls found to this file (Optional, by default {domain}.txt)")
        print("    -c cookie       Use the specified cookie (Optional)")
        print("")
        print("")
        exit(0)

if __name__ == '__main__':
    prog = program(sys.argv)
    prog.run()