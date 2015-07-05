#-*- coding: utf-8 -*-
import requests, regex, time, sqlite3
from lxml import html
from libextract.api import extract
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
			print "Stepping ", url
			grams = self.extract(url)
			to_db = [(url, ' '.join(grams))]
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
		texts = []
		r = requests.get(url)
		if r.status_code == 200:
			textnodes = list(extract(r.content))
			texts = [textnode.text_content() for textnode in textnodes]
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
		internal_links = [cur_base + link for link in links if urlparse(link).netloc == '' and link.startswith('/')]
		return full_links + internal_links

def lcs(a, b):
	lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
	# row 0 and column 0 are initialized to 0 already
	for i, x in enumerate(a):
		for j, y in enumerate(b):
			if x == y:
				lengths[i+1][j+1] = lengths[i][j] + 1
			else:
				lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
	# read the substring out from the matrix
	result = ""
	x, y = len(a), len(b)
	while x != 0 and y != 0:
		if lengths[x][y] == lengths[x-1][y]:
			x -= 1
		elif lengths[x][y] == lengths[x][y-1]:
			y -= 1
		else:
			assert a[x-1] == b[y-1]
			result = a[x-1] + result
			x -= 1
			y -= 1
	return result

def erase_noise(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	cur.execute("SELECT * FROM t;")
	rows = cur.fetchall()
	grams = [row[2] for row in rows]
	sqaure_lcs = [[lcs(grams[i], grams[j]) for j in xrange(i)] for i in xrange(len(grams))]
	return sqaure_lcs

if __name__ == '__main__':
	url = 'http://wonjaekim.com/'
	base_urls = [urlparse(url).netloc]
	spider = Spider(url, base_urls, 'cr.db', 0.1)
	spider.nstep(30)