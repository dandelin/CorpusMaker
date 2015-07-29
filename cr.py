#-*- coding: utf-8 -*-
import requests, regex, time, sqlite3, difflib, cleanhtml, re
from lxml import html
from libextract.api import extract
from urlparse import urlparse, urljoin

class Spider:
	def __init__(self, start_url, base_urls, db_name, timer=0.5, rule=''):
		self.extracted = set()
		self.queue = set([start_url])
		self.base_urls = set(base_urls)
                self.rules = [base_url+rule for base_url in base_urls]
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
                links_with_rule = []
                for rule in self.rules:
                    links_with_rule = links_with_rule + [link for link in links if rule in link]
                links = set(links_with_rule)
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
			to_db = [(url, '\n'.join(grams))]
			self.cur.executemany("INSERT INTO t (url, grams) VALUES (?, ?);", to_db)
			self._connection.commit()
			return grams
		else:
			return None
	def nstep(self, n=1):
		for i in xrange(n):
			print "Step #{}".format(i)
			grams = self.step()
			if grams == None:
				self._connection.close()
				print "Queue is Empty"
				return
			time.sleep(self.timer)
		self._connection.close()
	def extract_multilingual(self, url):
		texts = []
		r = requests.get(url)
		if r.status_code == 200:
                        a = r.content
                        b = cleanhtml.clean_html(a).lower()
                        c = re.split(r'[\n\r.]', b)
                        d = [re.sub(r'[^a-zA-z]+', ' ', cc) for cc in c]
                        e = [dd.strip() for dd in d]
                        f = [ee for ee in e if ee != '']
                        g = [ff for ff in f if ff.count(' ')> 5]
                        texts = g
		return texts
	def extract_links(self, url, base_urls):
		content = requests.get(url).content
		body = html.fromstring(content)
		links = body.xpath("//a/@href")
		full_links = [link for link in links if urlparse(link).netloc in base_urls and urlparse(link).scheme in ['http', 'https']]
		cur_parse = urlparse(url)
		cur_base = cur_parse.scheme + '://' + cur_parse.netloc
		internal_links = [urljoin(cur_base, link) for link in links if urlparse(link).netloc == '' and not link.startswith('#') and urlparse(link).scheme == '']
		return full_links + internal_links

def noise_extractor(url, base_urls):
	content = requests.get(url).content
	body = html.fromstring(content)
	links = body.xpath("//a/@href")
	full_links = [link for link in links if urlparse(link).netloc in base_urls and urlparse(link).scheme in ['http', 'https']]
	cur_parse = urlparse(url)
	cur_base = cur_parse.scheme + '://' + cur_parse.netloc
	internal_links = [urljoin(cur_base, link) for link in links if urlparse(link).netloc == '' and not link.startswith('#') and urlparse(link).scheme == '']
	link_to_explore = full_links + internal_links
	
	sample_contents = [requests.get(url).content for url in link_to_explore[:4]] + [content]
	textnodes = [t for content in sample_contents for t in list(extract(content, count=5))]
	noise = set()
	seqs = [[0 for i in xrange(len(textnodes))] for j in xrange(len(textnodes))]
	for i in xrange(len(textnodes)):
		t1 = textnodes[i].text_content()
		for j in xrange(i):
			t2 = textnodes[j].text_content()
			seq = difflib.SequenceMatcher(None, t1, t2)
			if seq.ratio() > 0.9:
				noise.add(t1)
				noise.add(t2)
	return noise




if __name__ == '__main__':
	url = 'http://wonjaekim.com/'
	base_urls = [urlparse(url).netloc]
	spider = Spider(url, base_urls, 'cr.db', 0.1)
	spider.nstep(30)
