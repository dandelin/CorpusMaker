import cr, utils
from urlparse import urlparse

url = 'http://www.beeradvocate.com'
base_urls = [urlparse(url).netloc]
spider = cr.Spider(url, base_urls, 'beer.db', 0.1)
spider.nstep(10)
utils.combine('beer.db')
