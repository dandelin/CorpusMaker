#-*- coding: utf-8 -*-
import requests, regex, time, sqlite3
from lxml import html
from urlparse import urlparse

class Spider:
	def __init__(self, start_url, base_urls, db_name, timer=0.5):
		self.extracted = set()
		self.queue = set([start_url])
		self.base_urls = set(base_urls)
		self._connection = sqlite3.connect(db_name)
		self.cur = self._connection.cursor()
		sql = "CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, url TEXT, grams TEXT);"
		self.cur.execute(sql)
		self.timer = timer
	def not_yet_extracted(self, urls):
		return [url for url in urls if not url in self.extracted]
	def extract(self, url):
		self.extracted.add(url)
		links = self.extract_links(url, self.base_urls)
		self.queue = self.queue.union(set(self.not_yet_extracted(links)))
		return self.extract_multilingual(url)
	def polling(self):
		url = self.queue.pop()
		return url
	def step(self):
		if len(self.queue) > 0:
			url = self.polling()
			grams = self.extract(url)
			print "Stepping {}".format(url)
			to_db = [(url, " ".join(grams))]
			self.cur.executemany("INSERT INTO t (url, grams) VALUES (?, ?);", to_db)
			self._connection.commit()
			return grams
		else:
			return []
	def nstep(self, n=1):
		for i in xrange(n):
			print "Step #{}".format(i)
			grams = self.step()
			if grams == []:
				self._connection.close()
				print "Crawling Finished"
				break
			time.sleep(self.timer)
		self._connection.close()
	def extract_multilingual(self, url):
		content = requests.get(url).content
		body = html.fromstring(content)
		texts = body.xpath("//*/text()")
		texts = [text for text in texts if regex.search(ur'\p{Hangul}+', text) or regex.fullmatch(r'[\w\s]+', text)]
		texts = [regex.findall(ur'\p{Hangul}+\.?|\p{Latin}+\.?', text) for text in texts]
		texts = [unicode(t) for text in texts for t in text]
		return texts
	def extract_links(self, url, base_urls):
		content = requests.get(url).content
		body = html.fromstring(content)
		links = body.xpath("//a/@href")
		full_links = [link for link in links if urlparse(link).netloc in base_urls]
		cur_parse = urlparse(url)
		cur_base = cur_parse.scheme + '://' + cur_parse.netloc
		internal_links = [cur_base + link for link in links if urlparse(link).netloc == '']
		return full_links + internal_links

if __name__ == '__main__':
	url = 'http://www.jaeminjo.com/'
	base_urls = [urlparse(url).netloc]
	spider = Spider(url, base_urls, 'jaeminjo.db', 0.1)
	spider.nstep(100000)