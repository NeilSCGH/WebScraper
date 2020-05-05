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

        self.data=urlparse(self.url)
        self.mainDomain=self.getMainDomain(self.url)

        self.deep = int(self.tool.tryToGetValue("-deep",2))
        self.outputFileName = self.tool.tryToGetValue("-o","")
        self.cookie = self.tool.tryToGetValue("-c","")
        self.verbose = self.tool.argExist("-v")
        self.allowedExtensions=["html", "php", "htm"]

        self.otherDomains=[]

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
        listToSave.sort()

        self.otherDomains= self.removeDuplicates(self.otherDomains)
        self.otherDomains.sort()

        if self.verbose: 
            self.printFoundUrls(listToSave)
            self.printOtherDomains()

        name=self.writeUrlsToFile(listToSave)
        print("All urls found are in the file {} !\n".format(name))

    def getMainDomain(self,url):
        data=urlparse(url)
        domain=data.netloc
        tmp=domain.split(".")
        return tmp[-2] + "." + tmp[-1]

    def printOtherDomains(self):
        print("\nOTHER DOMAINS:")
        for url in self.otherDomains:
            if self.getMainDomain(url)==self.mainDomain:
                print(url)

    def printFoundUrls(self,listUrls):
        print("\nUrls found ({}):".format(len(listUrls)))
        listUrls.sort()
        for url in listUrls:
            print(url)
        print("")

    def writeUrlsToFile(self,listUrls):
        if self.outputFileName=="":
            fileName=urlparse(self.url).netloc + ".txt"
        else:
            fileName=self.outputFileName

        f = open(fileName, "w")
        for url in listUrls:
            f.write(url + "\n")

        f.write("\n\n\nOTHER DOMAINS \n\n")

        for url in self.otherDomains:
            f.write(url + "\n")

        f.close()

        return fileName        

    def removeSchemeUrl(self,url):
        u=urlparse(url)
        return u.netloc + u.path

    def cleanUrl(self, url):
        u=urlparse(url)
        return u.scheme + "://" + u.netloc + u.path

    def sameDomain(self, url):
        return urlparse(url).netloc == (self.data).netloc
    
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
                urlFound=self.completeUrl(urlFound)
                urlFound=self.cleanUrl(urlFound)

                if self.sameDomain(urlFound):
                    links.append(urlFound)
                else:
                    (self.otherDomains).append(urlFound)

            links= self.removeDuplicates(links)
            return links
        except:
            print("\nERROR\n")
            return []

    def removeDuplicates(self,tab):
        return list(dict.fromkeys(tab))

    def completeUrl(self,url):
        if urlparse(url).netloc=="":
            url = (self.data).scheme + "://" + (self.data).netloc + url
        return url

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