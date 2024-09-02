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


# https://www.drmartens.com/us/en/p/25736100


def get_category_dic(html):
	soup = BeautifulSoup(html, 'html5lib')
	# EDITED
	list_record = soup.find('div', class_='navigation__overflow clearfix').find_all('a')
	dic = dict([(record.text, record['href']) for record in list_record])
	# <li class="yCmsComponent nav__link--secondary">
	if not os.path.exists(r'Martens'):
		os.makedirs(r'Martens')
	for p in dic:
		if martens_url not in dic[p]:
			dic[p] = martens_url + dic[p]
	return dic


def get_html(url):
	r = requests.get(url)
	return r.text


def get_photo_urls(soup):
	cur_photo = soup.find('div', class_='item js-zoom-img slick-slide slick-current slick-active').find('img')[
		'data-zoom-image']
	photos = [photo.find('img')['data-zoom-image'] for photo in
			  soup.find_all('div', class_='item js-zoom-img slick-slide')]
	photos.insert(0, cur_photo)
	return photos


def get_sublinks(driver):
	driver.get('https://www.drmartens.com/us/en/')
	html = driver.execute_script('return document.documentElement.outerHTML')
	soup = BeautifulSoup(html, 'html5lib')


def load_comments(soup, pages, product_id):
	if soup.find('div', class_='pagination') is None:
		return 0
	ref_pattern = soup.find('div', class_='pagination')['embedded_content_url'].split('(')[-1].split(')')[0]
	page_ref_p1, page_ref_p2 = ref_pattern.split('&page=1')
	counter = 0
	with open(r'Martens\comments.csv', 'a', newline='') as csvfile:
		comments_writer = csv.writer(csvfile, delimiter='|',
									 quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for p in range(pages):
			url = page_ref_p1 + '&page=' + str(p + 1) + page_ref_p2
			html = get_html(url=url)
			soup = BeautifulSoup(html, 'html5lib')
			comments = soup.find_all('article')
			if len(comments) == 0:
				break
			for comment in comments:
				counter += 1
				comment_id = comment['id']
				username = comment.find('h4', class_='attribution-name').text
				if comment.find('h5', class_='attribution-details').find('span', class_='location') is not None:
					location = comment.find('h5', class_='attribution-details').find('span',
																					 class_='location').text.strip()
				else:
					location = ''
				if comment.find('h5', class_='attribution-details').find('span', class_='segment') is not None:
					segment = comment.find('h5', class_='attribution-details').find('span',
																					class_='segment').text.strip()
				else:
					segment = ''
				overall_rating = comment.find('div', class_='overall_score_stars')['title']
				if hasattr(comment.find('dd', class_='pros'), 'text'):
					pros = comment.find('dd', class_='pros').text
				else:
					# e.g. Reviewer left no comment
					pros = ''
				if hasattr(comment.find('dd', class_='cons'), 'text'):
					cons = comment.find('dd', class_='cons').text
				else:
					# e.g. Reviewer left no comment
					cons = ''
				confirmed = comment.find('span', class_='date date_delivery').text.strip()
				published = comment.find('span', class_='date date_publish').text.strip()
				if comment.find('div', class_='review-photo') is not None:
					has_photo = 't'
					url = comment.find('div', class_='review-photo').find('img')['src']
				else:
					has_photo = 'f'
					url = ''
				if comment.find('span', class_='previous_voters') is not None:
					# Example: 1 of 1 people found this review helpful
					# Saved: 1 of 1
					helpful = comment.find('span', class_='previous_voters').text.split(' people')[0].strip()
				else:
					helpful = ''
				try:
					comments_writer.writerow(
						[comment_id, product_id, username, location, segment, overall_rating, pros, cons, confirmed,
						 published, has_photo, helpful])
					if len(url) > 1:
						urllib.request.urlretrieve(url, 'Martens/comments/' + product_id + '_' + comment_id + '.jpg')
				except Exception:
					counter -= 1
	return counter


def load_item(cat_name, driver, csv_writer, err_counter=1):
	try:
		time.sleep(1)
		html = driver.execute_script('return document.documentElement.outerHTML')
		soup = BeautifulSoup(html, 'html5lib')
		prod_name = soup.find('h1', class_='product-main-info__name').text.strip()
		price = soup.find('span', class_='current-price').text.strip()
		if soup.find('span', class_='clr original-price bfx-price') is not None:
			special_price = soup.find('span', class_='clr original-price bfx-price').text.strip()
		else:
			special_price = ''
		path_links = [k['href'] for k in soup.find('ol', class_='breadcrumb').find_all('a')]
		binded_refs = [r['href'] for r in soup.find('ul', class_='variant-list').find_all('a')]
		# sizes block
		# adding a id (avaiable/not avaiable for each size value
		sizes = soup.find('div', class_='size-content size-with-tab')
		sizes_male = sizes_female = sizes_juniors = []
		if sizes is not None:
			if sizes.find('div', id='tabSize_MALE') is not None and len(
					sizes.find('div', id='tabSize_MALE').find_all('a')) > 0:
				sizes_male = [size['data-label'].split(';')[-1].split('\xa0')[-1] + ' ' + size['data-sku-purchasable'][0]
							  for size in sizes.find('div', id='tabSize_MALE').find_all('a') if
							  size.has_attr('data-label')]
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
		# product description block
		alltext = soup.find('div', id='item-prodDetail')
		if alltext is not None:
			description = '\r\n'.join(str(alltext).split('\n')[1:-1])
		else:
			description = ''
		color = soup.find('div', id='js-variant-label').find('span').text
		id = soup.find('div', id='js-variant-label').find('label').text

		# downloading photos
		list_photos = get_photo_urls(soup)
		for i in range(len(list_photos)):
			urllib.request.urlretrieve(list_photos[i], 'Martens/prod_photos/' + id + '_' + str(i) + '.jpg')
		# loading comments
		counter = 0
		ncomments = actual_ncomments = '0'
		style = quality = value_for_money = overall_rating = ''
		while True:
			html = driver.execute_script('return document.documentElement.outerHTML')
			soup = BeautifulSoup(html, 'html5lib')
			if soup.find('a', class_='js-tab-call reviews-tab') is None:
				counter = 10
				break
			if len(soup.find('a', class_='js-tab-call reviews-tab').text.split('(')[-1]) > 1 or counter > 3:
				break
			counter += 1
			time.sleep(1)
		if counter <= 3:
			nrevs = int(soup.find('a', class_='js-tab-call reviews-tab').text.split('(')[-1][:-1])
			if nrevs > 0:
				driver.execute_script("window.scrollTo(0, 500);")
				driver.find_element_by_css_selector('.js-tab-call.reviews-tab').click()
				time.sleep(1)
				html = driver.execute_script('return document.documentElement.outerHTML')
				soup = BeautifulSoup(html, 'html5lib')
				if soup.find('table', class_='scores') is not None:
					revs = soup.find('table', class_='scores').find_all('span')
					style, quality, value_for_money, overall_ratings = [str(r.text) for r in revs[:4]]
					ncomments = str(nrevs)
					nrevs = load_comments(soup=soup, pages=math.ceil(nrevs / 10), product_id=id)
					actual_ncomments = str(nrevs)
				driver.execute_script("window.scrollTo(0, 0)")

		# id, category, prod_name, price, special_price, color, sizes_male, sizes_female, sizes_juniors, description,
		# binded_refs, path_links, ncomments, actual_ncomments, style, quality, val4money, overall_rating
		new_row = [id, cat_name, prod_name, price, special_price, color, ','.join(map(str, sizes_male)),
				   ','.join(map(str, sizes_female)), ','.join(map(str, sizes_juniors)),
				   description, ','.join(map(str, binded_refs)), ','.join(map(str, path_links)),
				   ncomments, actual_ncomments, str(style).replace(".", ","), str(quality).replace(".", ","),
				   str(value_for_money).replace(".", ","), str(overall_rating).replace(".", ",")]
		csv_writer.writerow(new_row)
	except Exception as e:
		print(e)
		if err_counter < 3:
			driver.refresh()
			time.sleep(6 * err_counter)
			load_item(cat_name=cat_name, driver=driver, csv_writer=csv_writer, err_counter=err_counter + 1)
		else:
			traceback.print_exc()
			exit()


def load_boots(cat_name, url, driver, csv_writer=None):
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
		# list_ids = ['img-' + goods_link.split('/')[-1] for goods_link in list_goods]
		# .find('main', class_='dm-main clr clearfix main__inner-wrapper')
		print(len(list_goods))
		for i in list_goods:
			driver.get(i)
			time.sleep(2)
			load_item(cat_name=cat_name, driver=driver, csv_writer=csv_writer)


def skip_ad(driver):
	print('me go sleep')
	time.sleep(5)
	print('ama awake')
	html = driver.execute_script('return document.documentElement.outerHTML')
	soup = BeautifulSoup(html, 'html5lib')
	test = soup.find('div', id='popup-subcription-backgrounds-container-0d5cfac3-223a-4e52-91f7-24372d156775')
	if test is not None:
		driver.find_element_by_id('popup-overlay-0d5cfac3-223a-4e52-91f7-24372d156775').click()
		return True
	return False


def main():
	# r'C:\Users\Admin\AppData\Roaming\Mozilla\Firefox\Profiles\m72by53l.default'
	driver = webdriver.Chrome(r'C:\Users\Admin\.wdm\drivers\chromedriver\win32\83.0.4103.39\chromedriver.exe')
	# (ChromeDriverManager().install())
	driver.get('https://www.drmartens.com/us/en')
	html_dic = get_category_dic(get_html(martens_url + '/us/en'))
	with open(r'Martens\goods.csv', 'a', newline='') as csvfile:
		goods_writer = csv.writer(csvfile, delimiter=';',
								  quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for cat in html_dic:
			load_boots(cat_name=cat, url=html_dic[cat], driver=driver, csv_writer=goods_writer)


if __name__ == '__main__':
	global martens_url
	martens_url = 'https://www.drmartens.com'
	main()
	binded_refs_names = {'NEW': '/us/en/unisex/new-arrivals/c/04150000',
						 'NEW ARRIVALS': '/us/en/kids/new-arrivals/c/03150000',
						 'WOMEN': '/us/en/womens/c/01000000',
						 'MEN': '/us/en/mens/c/02000000',
						 'KIDS': '/us/en/kids/c/03000000',
						 'VIEW ALL': '/us/en/unisex/new-arrivals/c/04150000',
						 'FEATURED': '/us/en/originals-boots-and-shoes/boots/c/06010000',
						 'PLATFORMS': '/us/en/mens/platforms/c/02050000',
						 'SANDALS': '/us/en/kids/kids-sandals/c/03b30000',
						 'CASUAL': '/us/en/mens/mens-casual-boots-and-shoes/c/02a70000',
						 'COLOR POP ORIGINALS': 'https://www.drmartens.com/us/en/originals-boots-and-shoes/c/06000000',
						 'STYLE AND CARE': 'https://www.drmartens.com/us/en/the-gallery',
						 'INSTAGRAM GALLERY': 'https://www.drmartens.com/us/en/the-gallery',
						 'HOW TO CLEAN YOUR DOCS': 'https://www.drmartens.com/us/en/how-to-clean-docs-balsam-wax',
						 'HOW TO CLEAN PATENT LEATHER': '/us/en/how-to-clean-patent-leather-docs',
						 'HOW TO CLEAN SUEDE': '/us/en/how-to-clean-suede-dr-martens',
						 'How to Protect Your Leather': '/us/en/how-to-protect-maintain-dr-martens',
						 'HOW TO CLEAN WITH DUBBIN WAX': 'https://www.drmartens.com/us/en/how-to-clean-docs-dubbin-wax',
						 'HOW TO STYLE': 'https://www.drmartens.com/us/en/how-to-style',
						 'Shop All': '/us/en/c/06000000',
						 'BOOTS, SHOES & SANDALS': '/us/en/kids/c/03000000',
						 'BOOTS': '/us/en/kids/boots/c/03010000',
						 'SHOES': '/us/en/kids/shoes/c/03020000',
						 'CHELSEA BOOTS': '/us/en/mens/boots/chelsea-boots/c/02010500',
						 'ANKLE BOOTS': '/us/en/mens/boots/ankle-boots/c/02010600',
						 'HEELS': '/us/en/womens/heels/c/01040000',
						 'MARY JANES': '/us/en/womens/shoes/mary-jane-shoes/c/01021200',
						 'BEST SELLERS': '/us/en/kids/best-sellers/c/03110000',
						 'MADE IN ENGLAND': '/us/en/unisex/made-in-england/c/04310000',
						 'VEGAN': '/us/en/mens/vegan/c/02060000',
						 'Sale': '/us/en/sale/mens/c/08380000',
						 'ACCESSORIES': '/us/en/accessories/c/07000000',
						 'BAGS & BACKPACKS': '/us/en/accessories/bags/womens/c/07576900',
						 'LACES': '/us/en/accessories/shoecare--laces-and-insoles/shoe-laces/c/07597600',
						 'SHOE CARE & INSOLES': '/us/en/accessories/shoecare--laces-and-insoles/shoe-care---cleaner/c/07597500',
						 'SOCKS': '/us/en/accessories/socks/c/07600000',
						 'ALL ACCESSORIES': '/us/en/accessories/mens/c/07610000',
						 'UTILITY BOOTS': '/us/en/mens/boots/utility-boots/c/02010003',
						 'BAGS & WALLETS': '/us/en/accessories/bags/mens/c/07576800',
						 'SHOP BY SIZE': '/us/en/kids/c/03000000',
						 'BIG KIDS': '/us/en/kids/youth/c/03250000',
						 'LITTLE KIDS': '/us/en/kids/junior/c/03240000',
						 'TODDLERS': '/us/en/kids/toddler-shoes-and-boots/c/03230000',
						 'INFANT/NEWBORN': '/us/en/kids/baby-and-infant-boots-and-shoes/c/03220000',
						 'ALL KIDS': '/us/en/kids/c/03000000',
						 'GIRLS BOOTS & SHOES': '/us/en/kids/girls/c/03200000',
						 'BOYS BOOTS & SHOES': '/us/en/kids/boys/c/03210000',
						 'SALE': '/us/en/sale/c/08000000',
						 'ORIGINALS': '/us/en/originals-boots-and-shoes/c/06000000',
						 'ORIGINAL BOOTS': '/us/en/originals-boots-and-shoes/boots/c/06010000',
						 '1460 LACE-UP BOOTS': '/us/en/originals-boots-and-shoes/boots/1460-lace-up-boots/c/06015600',
						 '1490 MID CALF BOOTS': '/us/en/originals-boots-and-shoes/boots/1490-boots/c/06015700',
						 '2976 CHELSEA BOOTS': '/us/en/originals-boots-and-shoes/boots/2976-chelsea-boots/c/06015900',
						 '101 LOW LACE-UP BOOTS': '/us/en/originals-boots-and-shoes/boots/101-ankle-boots/c/06015800',
						 '1914 TALL BOOTS': '/us/en/originals-boots-and-shoes/boots/1914-tall-lace-up-boots/c/06016000',
						 'CHURCH MONKEY BOOTS': '/us/en/originals-boots-and-shoes/boots/church-boots/c/06016100',
						 'ORIGINAL SHOES': '/us/en/originals-boots-and-shoes/shoes/c/06020000',
						 '1461 OXFORD SHOES': '/us/en/originals-boots-and-shoes/shoes/1461-oxford-shoes/c/06026200',
						 '3989 BROGUE SHOES': '/us/en/originals-boots-and-shoes/shoes/3989-brogue-shoes/c/06026300',
						 '8065 MARY JANE SHOES': '/us/en/originals-boots-and-shoes/shoes/8065-mary-jane-shoes/c/06026400',
						 '8053 CASUAL SHOES': '/us/en/originals-boots-and-shoes/shoes/8053-shoes/c/06026700',
						 'ADRIAN TASSEL LOAFER': '/us/en/originals-boots-and-shoes/shoes/adrian-tassel-loafers/c/06026500',
						 'POLLEY T-BAR MARY JANE': '/us/en/originals-boots-and-shoes/shoes/polley-t-bar-mary-jane-shoes/c/06026600',
						 "WOMEN'S ORIGINALS": '/us/en/womens/originals/c/01070000',
						 "MEN'S ORIGINALS": '/us/en/mens/originals/c/02070000',
						 'ALL ORIGINALS': '/us/en/originals-boots-and-shoes/c/06000000',
						 'LEARN MORE': 'https://www.drmartens.com/us/en/originals-boots-and-shoes',
						 'WORK BOOTS': '/us/en/work/work-boots/c/05840000',
						 'WORK BOOTS & SHOES': '/us/en/work/c/05000000',#we are here
						 'WORK SHOES': '/us/en/work/work-shoes/c/05850000',
						 'LIGHT WORK BOOTS': '/us/en/work/light-work/c/05400000',
						 'HEAVY DUTY WORK BOOTS': '/us/en/work/heavy-work/c/05410000',
						 'SERVICE INDUSTRY': '/us/en/work/service-work-boots-and-shoes/c/05860000',
						 'EXTRA-WIDE': '/us/en/work/extra-wide-work-boots/c/05490000',
						 'SAFETY & STEEL TOE': '/us/en/work/steel-toe/c/05430000',
						 "WOMEN'S WORK BOOTS": '/us/en/work/womens/c/05390000',
						 'ALL WORK BOOTS & SHOES': '/us/en/work/c/05000000', 'TECHNOLOGIES': '/us/en/work/c/05000000',
						 'ANTI-STATIC': '/us/en/work/anti-static-work-boots/c/05470000',
						 'ELECTRICAL HAZARD': '/us/en/work/electrical-hazard-work-boots/c/05480000',
						 'HEAT RESISTANT': '/us/en/work/heat-resistant-work-boots/c/05500000',
						 'METATARSAL GUARD': '/us/en/work/metatarsal-guard-work-boots/c/05510000',
						 'PUNCTURE RESISTANT': '/us/en/work/puncture-resitant-work-boots/c/05530000',
						 'SLIP-RESISTANT': '/us/en/work/slip-resistant/c/05450000',
						 'STEEL TOE': '/us/en/work/steel-toe/c/05430000',
						 'WATERPROOF': '/us/en/work/waterproof-boots/c/05330000', 'EXPLORE': '/us/en/tough-as-you',
						 'TOUGH AS YOU': 'https://www.drmartens.com/us/en/tough-as-you',
						 'FIND OUT MORE': 'https://www.drmartens.com/us/en/tough-as-you',
						 '#TOUGHASYOU': 'https://www.drmartens.com/us/en/tough-as-you/your-stories',
						 'ABOUT TOUGH AS YOU': 'https://www.drmartens.com/us/en/tough-as-you/about',
						 'STORIES': 'https://www.drmartens.com/us/en/tough-as-you',
						 'TOUGH AS YOU STORIES': 'https://www.drmartens.com/us/en/tough-as-you/our-stories',
						 'AVIE ACOSTA': 'https://www.drmartens.com/us/en/tough-as-you/stories/avie-acosta',
						 'BOB VYLAN': 'https://www.drmartens.com/us/en/tough-as-you/stories/bob-vylan',
						 'LOTTE VAN EIJK': 'https://www.drmartens.com/us/en/tough-as-you/stories/lotte-van-eijk',
						 'NAKED GIANTS': 'https://www.drmartens.com/us/en/tough-as-you/stories/naked-giants',
						 'DR. MARTENS PRESENTS': 'https://www.drmartens.com/us/en/dm-presents',
						 'How to Style': 'https://www.drmartens.com/us/en/how-to-style',
						 'DM Presents': '/us/en/dm-presents', 'DIY DOCS': '/us/en/diy-docs',
						 'BLOG': 'https://blog.drmartens.com/', 'MUSIC': 'https://blog.drmartens.com/category/music/',
						 'STYLE': 'https://blog.drmartens.com/category/style/',
						 'ART': 'https://blog.drmartens.com/category/art/',
						 'COLLABORATIONS': 'https://blog.drmartens.com/category/dr-martens-collaborates/',
						 'THE BRAND': 'https://blog.drmartens.com/category/the-brand/'}

# html = get_html('https://www.drmartens.com/us/en/p/11822006')
# soup = BeautifulSoup(html, 'html5lib')
