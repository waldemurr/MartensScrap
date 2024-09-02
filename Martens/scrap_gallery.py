import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
import requests
import urllib
import math

driver = webdriver.Chrome(r'C:\Users\Admin\.wdm\drivers\chromedriver\win32\83.0.4103.39\chromedriver.exe')
driver.get('https://www.drmartens.com/us/en/the-gallery')
time.sleep(2)
for i in range(100):
	driver.execute_script("window.scrollTo(0, 10000000);")
	time.sleep(1)
driver.execute_script("window.scrollTo(0, 200);")

driver.find_element_by_class_name('olapic-item-info.olapic-item').click()
with open(r'Martens\instagram_gallery.csv', 'w', newline='') as csvfile:
	inst_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(500):
		time.sleep(0.5)
		html = driver.execute_script('return document.documentElement.outerHTML')
		soup = BeautifulSoup(html, 'html5lib')
		id = driver.current_url.split('#')[-1]
		inst_nick = soup.find('span', class_='author-realname blank_link')
		prod_name = soup.find('span', class_='product-list-item-title')
		user_photo_url = soup.find('div', class_='olapic-main-image')['style'].split('(')[-1].split(')')[0]
		urllib.request.urlretrieve(user_photo_url, 'Martens/inst_photos/' + id + '.jpg')
		prod_photo_url = soup.find('span', class_='product-list-item-image')['style'].split('(')[-1].split(')')[0]
		urllib.request.urlretrieve(user_photo_url, 'Martens/inst_prod_photos/' + id + '.jpg')
		inst_writer.writerow([id, inst_nick, prod_name])
		driver.find_element_by_id('viewer-next').click()
