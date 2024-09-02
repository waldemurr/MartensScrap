from selenium import webdriver
import math
import numpy as np
import csv

howtoos={'HOW TO CLEAN YOUR DOCS': 'https://www.drmartens.com/us/en/how-to-clean-docs-balsam-wax',
		 'HOW TO CLEAN PATENT LEATHER': '/us/en/how-to-clean-patent-leather-docs',
		 'HOW TO CLEAN SUEDE': '/us/en/how-to-clean-suede-dr-martens',
		 'How to Protect Your Leather': '/us/en/how-to-protect-maintain-dr-martens',
		 'HOW TO CLEAN WITH DUBBIN WAX': 'https://www.drmartens.com/us/en/how-to-clean-docs-dubbin-wax',
		 'HOW TO STYLE': 'https://www.drmartens.com/us/en/how-to-style',}
nd = {}
for k in howtoos.keys():
	nd
