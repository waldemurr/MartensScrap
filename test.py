import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
import math

#https://www.drmartens.com/us/en/p/25678201


# driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Chrome(r'C:\Users\Admin\.wdm\drivers\chromedriver\win32\83.0.4103.39\chromedriver.exe')
driver.get('https://www.drmartens.com/us/en/unisex/new-arrivals/c/04150000')
html = driver.execute_script('return document.documentElement.outerHTML')
soup = BeautifulSoup(html, 'html5lib')
header = soup.find('div', class_='hero__text').find('h1').text
print(header)
