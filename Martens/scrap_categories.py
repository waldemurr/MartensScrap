import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import math

driver = webdriver.Chrome(r'C:\Users\Admin\.wdm\drivers\chromedriver\win32\83.0.4103.39\chromedriver.exe')
driver.get('https://www.drmartens.com/us/en')
html = driver.execute_script('return document.documentElement.outerHTML')
soup = BeautifulSoup(html, 'html5lib')
list_record = soup.find('div', class_='navigation__overflow clearfix').find_all('a')
dic = dict([(record.text, record['href']) for record in list_record])
mains = soup.find_all(class_='yCmsComponent nav__link js_nav__link main-nav-link')
# main subcat
# m_subcat = soup.find('div', class_='title')
martens_url = 'https://www.drmartens.com'
# with open(r'Martens\cats_goods.csv', 'w', newline='') as csvfile:
# 	cg_writer = csv.writer(csvfile, delimiter=';',
# 							  quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	for p in dic:
# 		if martens_url not in dic[p]:
# 			dic[p] = martens_url + dic[p]
# 		driver.get(dic[p])
# 		time.sleep(4)
# 		html = driver.execute_script('return document.documentElement.outerHTML')
# 		soup = BeautifulSoup(html, 'html5lib')
# 		if soup.find('span', id='filter-count') is not None:
# 			items_count = int(soup.find('span', id='filter-count').text)
# 			pages_count = math.ceil(items_count / 48)
#
# 			for i in range(pages_count - 1):
# 				driver.execute_script("window.scrollTo(0, document.body.scrollHeight-800);")
# 				driver.find_element_by_css_selector('.btn.btn-primary.pagination__wrap__button.js-pagination').click()
# 				time.sleep(2)
# 			html = driver.execute_script('return document.documentElement.outerHTML')
# 			soup = BeautifulSoup(html, 'html5lib')
# 			list_goods = [martens_url + product['href'] for product in
# 						  soup.find('div', id='product-list').find_all('a', class_="product__list__item__name")]
# 			list_goods_names = [product['href'] for product in
# 						  soup.find('div', id='product-list').find_all('a', class_="product__list__item__name")]
# 			for i in range(items_count):
# 				cg_writer.writerow([p, dic[p], list_goods[i], list_goods_names[i]])
with open(r'Martens\categories.csv', 'w', newline='') as csvfile:
	cg_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for p in dic:
		if martens_url not in dic[p]:
			dic[p] = martens_url + dic[p]
		driver.get(dic[p])
		time.sleep(4)
		html = driver.execute_script('return document.documentElement.outerHTML')
		soup = BeautifulSoup(html, 'html5lib')
		slug = driver.current_url.split('/')[-1]
		url = driver.current_url
		title = soup.find('title').text.strip()
		if soup.find('div', class_='hero__text') is not None:
			header = soup.find('div', class_='hero__text').find('h1').text.strip()
		else:
			header = None
		if soup.find(class_='js-hero-read-more') is not None:
			description = soup.find(class_='js-hero-read-more').text
		else:
			description = None
		if soup.find('ol', class_='breadcrumb') is not None:
			binded_refs = [r['href'] for r in soup.find('ol', class_='breadcrumb').find_all('a')]
			binded_names = [r.text for r in soup.find('ol', class_='breadcrumb').find_all('a')]
		else:
			binded_refs = binded_names = ''
		# slug, url, title, description, header, description, binded_refs, binded_names
		print(str(title) + '     ' + str(header))
		new_row = [slug, url, title,description, header, ','.join(binded_refs), ','.join(binded_names)]
		cg_writer.writerow(new_row)
