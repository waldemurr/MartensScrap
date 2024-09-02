from bs4 import BeautifulSoup
import math
import os
import requests
# from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib
import traceback


# 5-11
def get_html(url):
    r = requests.get(url)
    return r.text


url = r'https://avto-nomer.ru/ru/gallery.php?&ctype=1&usr=11376&start='
for i in range(2, 102):
    soup = BeautifulSoup(get_html(url + str(i)), 'html5lib')
    print(soup.find('div'))
    list_img = soup.find('div', class_='container content').find_all('img', class_='img-responsive center-block')
    print(list_img)
    # urllib.request.urlretrieve(user_photo_url, 'Martens/inst_photos/' + id + '.jpg')
    # print(list_img)
