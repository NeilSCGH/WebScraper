# Weber (Web scraper)

This program will scrap an url. The verbose flag will print all url found during the scan.

	Usage: python weber.py -url URL [-deep x] [-v] [-o fileName]

	Options:

		-url URL        The url to scan

		-deep x         Depth of scan, number of iteration (Optional, by default set to 2)

		-v              Enable verbose during scan (Optional)

		-o fileName     Output all urls found to this file (Optional, by default {domain}.txt)
		
		-c cookie       Use the specified cookie
