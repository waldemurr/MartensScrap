from bs4 import BeautifulSoup
import math
import os
import requests
import csv
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib
import traceback

#5-11
def get_html(url):
	r = requests.get(url)
	return r.text


def get_category_dic(html):
	soup = BeautifulSoup(html, 'html5lib')
	list_record = soup.find('div', class_='navigation__overflow clearfix').find_all('a')[5:]
	dic = dict([(record.text, record['href']) for record in list_record])
	# <li class="yCmsComponent nav__link--secondary">
	if not os.path.exists(r'Martens'):
		os.makedirs(r'Martens')
	for p in dic:
		if martens_url not in dic[p]:
			dic[p] = martens_url + dic[p]
	print(dic)
	return dic


def load_sizes(driver, csv_writer, err_counter=1):
	try:
		time.sleep(1)
		html = driver.execute_script('return document.documentElement.outerHTML')
		soup = BeautifulSoup(html, 'html5lib')
		# sizes block
		# adding a id (avaiable/not avaiable for each size value
		sizes = soup.find('div', class_='size-content size-with-tab')
		sizes_male = sizes_female = sizes_juniors = []
		if sizes is not None:
			if sizes.find('div', id='tabSize_MALE') is not None and len(
					sizes.find('div', id='tabSize_MALE').find_all('a')) > 0:
				sizes_male = [size['data-label'].split(';')[-1].split('\xa0')[-1] + ' ' + size['data-sku-purchasable'][0]
							  for size in sizes.find('div', id='tabSize_MALE').find_all('a') if size.has_attr('data-label')]
			if sizes.find('div', id='tabSize_FEMALE') is not None and len(
					sizes.find('div', id='tabSize_FEMALE').find_all('a')) > 0:
				sizes_female = [size['data-label'].split(';')[-1].split('\xa0')[-1] + ' ' + size['data-sku-purchasable'][0]
								for size in sizes.find('div', id='tabSize_FEMALE').find_all('a') if
								size.has_attr('data-label')]
			if sizes.find('div', id='tabSize_JUNIORS') is not None and len(
					sizes.find('div', id='tabSize_JUNIORS').find_all('a')) > 0:
				sizes_juniors = [
					size['data-label'].split(';')[-1].split('\xa0')[-1] + ' ' + size['data-sku-purchasable'][0]
					for size in sizes.find('div', id='tabSize_JUNIORS').find_all('a') if
					size.has_attr('data-label')]
		id = soup.find('div', id='js-variant-label').find('label').text

		# id, sizes_male, sizes_female, sizes_juniors
		new_row = [id, ','.join(map(str, sizes_male)), ','.join(map(str, sizes_female)),
				   ','.join(map(str, sizes_juniors))]
		csv_writer.writerow(new_row)
	except Exception as e:
		print(e)
		if err_counter < 3:
			driver.refresh()
			time.sleep(6 * err_counter)
			load_sizes(driver=driver, csv_writer=csv_writer, err_counter=err_counter + 1)
		else:
			print(driver.current_url)
			traceback.print_exc()


def load_boots(url, driver, csv_writer=None):
	driver.get(url)
	time.sleep(2)
	html = driver.execute_script('return document.documentElement.outerHTML')
	soup = BeautifulSoup(html, 'html5lib')
	if soup.find('span', id='filter-count') is not None:
		items_count = int(soup.find('span', id='filter-count').text)
		pages_count = math.ceil(items_count / 48)

		for i in range(pages_count - 1):
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight-800);")
			driver.find_element_by_css_selector('.btn.btn-primary.pagination__wrap__button.js-pagination').click()
			time.sleep(2)
		html = driver.execute_script('return document.documentElement.outerHTML')
		soup = BeautifulSoup(html, 'html5lib')
		list_goods = [martens_url + product['href'] for product in
					  soup.find('div', id='product-list').find_all('a', class_="product__list__item__name")]
		print(len(list_goods))
		for i in list_goods:
			driver.get(i)
			time.sleep(2)
			load_sizes(driver=driver, csv_writer=csv_writer)


def main():
	# r'C:\Users\Admin\AppData\Roaming\Mozilla\Firefox\Profiles\m72by53l.default'
	driver = webdriver.Chrome(r'C:\Users\Admin\.wdm\drivers\chromedriver\win32\83.0.4103.39\chromedriver.exe')
	# (ChromeDriverManager().install())
	driver.get('https://www.drmartens.com/us/en')
	html_dic = get_category_dic(get_html(martens_url + '/us/en'))
	with open(r'Martens\sizes.csv', 'a', newline='') as csvfile:
		goods_writer = csv.writer(csvfile, delimiter=';',
								  quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for cat in html_dic:
			load_boots(url=html_dic[cat], driver=driver, csv_writer=goods_writer)


if __name__ == '__main__':
	global martens_url
	martens_url = 'https://www.drmartens.com'
	main()
