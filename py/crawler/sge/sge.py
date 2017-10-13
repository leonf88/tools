#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, os, re, json
import urllib
import urllib2
import urlparse
import logging
import traceback
import time

from pyquery import PyQuery as PQ

reload(sys)
sys.setdefaultencoding("utf8")

class SGEDownload:

	def __init__(self):
		# [{"date": ..., "url": ..., "data": {"title": ..., "Au100g": ..., "Ag(T+D)": ..., ...}}, ...]
		self._data = []

	# def _chk(rec):
	# 	for w in rec["data"]["title"]:
	# 		for t in tags:
	# 			if w == t:
	# 				return True
	# 	raise(IOError("record does not have tag " + t))
	def load_data(self, file_path, chk_func = None):
		"""load data file into memory, the format of date is '\%Y-\%m-\%d' and will be convert to time.struct_time type """
		self._data = []

		in_file = open(file_path, "r")
		for line in in_file:
			rec = json.loads(line.encode("utf8"), encoding="utf8")
			try:
				if chk_func: chk_func(rec)
				self._data.append(rec)
			except IOError, e:
				print "read line: " + line
				print e
				sys.exit(-1)

		in_file.close()
		self._data = self._format_data(self._data)

	def _format_data(self, data):
		if data:
			def _format_date(d):
				if d != time.struct_time:
					d = time.strptime(d, "%Y-%m-%d")
				return d
			data = map(lambda d: {"date": _format_date(d["date"]), "url": d["url"], "data": d["data"]}, data)

		return data

	def dump_data(self, file_path, mode = "w"):
		f_data = open(file_path, mode)
		for lk in self._data:
			t_date = lk["date"]
			lk["date"] = self.format_time(lk["date"])
			f_data.write(json.dumps(lk, encoding='utf-8', ensure_ascii=False))
			f_data.write("\r\n")
			f_data.flush()
			lk["date"] = t_date
		f_data.close()

	# return the self._data["data"]
	def _get_one_page_data(self, page_url):
		"""Page structure is like: .full_count #pzoom table"""
		try:
			p_content = urllib2.urlopen(page_url).read()
			pq = PQ(p_content)
			
			# page title
			# print pq(".imgDetail h2").text()

			# patch for some pages
			trs = pq("#page_con tbody tr")

			if len(trs) == 0:
				p_data = None
			else:
				# get the title
				d_title = map(lambda t: re.sub(r"\s+", "", PQ(t).text()) , PQ(trs[0])("td"))
				if len(d_title)==0:
					# patch for some pages
					d_title = map(lambda t: re.sub(r"\s+", "", PQ(t).text()) , PQ(trs[0])("th"))
				p_data = {"title":d_title}
				d_arr = []
				for tr in trs[1:]:
					d_row = map(lambda t: PQ(re.sub(r"<(script).*?</\1>(?s)","",PQ(t).html())).text(),PQ(tr)("td"))
					p_data[d_row[0]] = d_row
		except Exception, e:
			traceback.print_exc()
			print "error page: %s\n%s" % (page_url,e)
			return None

		return p_data

	# links: [{"date": ..., "url": ...}, ...]
	def _get_one_page_links(self, page_url):
		"""Get the links of the one page, and return the next page link"""
		links = []
		prefix_url = "http://www.sge.com.cn/xqzx/mrxq/"
		# prefix_url = "http://www.sge.sh/publish/sge/xqzx/jyxq/index.htm"
		try:
			p_content = urllib2.urlopen(page_url).read()
			pq = PQ(p_content)

			for li in map(lambda a: PQ(a), pq("#zl_list li")):
				try:
					d = li("span").text().strip()
					d = time.strptime(d, "%Y-%m-%d")
				except:
					print "Convert date error " + d + ". Format is \"%Y-%m-%d\""
					sys.exit(-1)

				l = {"date":d, "url":urlparse.urljoin(prefix_url, li("a").attr("href"))}
				links.append(l)

			next_url = None
			for a in map(lambda a:PQ(a), pq(".z_page a")):
				if a.text() == "下一页":
					next_url = urlparse.urljoin(prefix_url, a.attr("href"))

			if next_url is not None and next_url != page_url:
				return links, next_url
			else:
				return links, None
		except Exception, e:
			print "error page: %s" % page_url
			print e

	def incr_get_data(self, page_url, file_path = None):
		"""update the data incremently"""
		if (self._data is None or len(self._data) == 0) and file_path != None and (os.path.exists(file_path) and os.path.isfile(file_path)):
			self.load_data(file_path)
			date = [d["date"] for d in self._data]
			past_max_date = max(date)
		else:
			self._data = []
			past_max_date = time.strptime("1977-01-01", "%Y-%m-%d")

		print "Update time to " + self.format_time(past_max_date)
		new_links = []

		while True:
			links, next_url = self._get_one_page_links(page_url)
			min_date = min([d["date"] for d in links])
			if past_max_date > min_date:
				for lk in links:
					if lk["date"] > past_max_date:
						new_links.append(lk)
				break
			else:
				new_links.extend(links)
				print "Append %d new pages, current page size is %d, current date %s" % (len(links), len(new_links), self.format_time(links[0]["date"]))

			if next_url is not None and next_url != page_url:
				page_url = next_url
				next_url = None
			else:
				break

		sum = len(new_links)

		for cnt, pg in enumerate(new_links):
			pg["data"] = self._get_one_page_data(pg["url"])
			self._data.append(pg)
			cnt+=1
			rate = float(cnt) / float(sum)
			rate_num = int(rate * 100)
			print '%-20s%3d/%d......%3d%%\r' % (self.format_time(pg['date']), cnt, sum, rate_num),
			sys.stdout.flush()

	def format_time(self, date):
		return "%d-%d-%d" % (date.tm_year, date.tm_mon, date.tm_mday)

	def update(self, file_path):
		self.incr_get_data("http://www.sge.com.cn/xqzx/mrxq", file_path)
		self._data = sorted(self._data, key = lambda r: r["date"])
		self.dump_data(file_path)

	def sort(self, file_path):
		self.load_data(file_path)
		self._data = sorted(self._data, key = lambda r: r["date"])
		self.dump_data(file_path)

class SEGPlot:
	def __init__(self):
		# [{"date": ..., "url": ..., "data": {"title": ..., "Au100g": ..., "Ag(T+D)": ..., ...}}, ...]
		pass

	# [["date", "t1 k1 val", "t2 k1 val", ..., "t1 k2 val", "t2 k2 val", ...]
	def parse_data(self, data, keys, tags = [u"最高价", u"收盘价", u"开盘价", u"最低价"]):
		def _find_idx(tags, arr):
			# [t1, t2] => {t1: 1, t2: 2}
			t_idx = {}
			for t in tags: t_idx[t] = -1
			for i, t in enumerate(arr):
				if t_idx.has_key(t):
					t_idx[t] = i
			logging.debug("tags index: " + str(t_idx))
			return t_idx

		p_rec = []
		for rec in data:
			if rec["data"] is None:
				continue
			irec = []
			irec.append(rec["date"])
			t_idx = _find_idx(tags, rec["data"]["title"])
			for k in keys:
				if rec["data"].has_key(k):
					d = rec["data"][k]
				else:
					d = ["0"] * len(rec["data"]["title"])
				for t in tags:
					irec.append(d[t_idx[t]])

			p_rec.append(irec)

		p_rec = sorted(p_rec, key = lambda r: r[0], reverse=True)

		return p_rec

	def plot(self, data, out_file):
		if data is None or len(data) == 0:
			print "No data to plot"
			return

		zipped = zip(*data)

		import numpy as np
		import pylab as plt
		from matplotlib.ticker import MultipleLocator

		y = zipped[3]

		fig = plt.figure(figsize=(10, 6))
		x = np.arange(0, len(y), 1)

		plt.rc('font', family='serif')
		plt.plot(x, y)
		plt.xlabel(r'Date')
		plt.ylabel(r'Price (RMB)', fontsize=16)
		plt.title(r"Gold Price Trend", fontsize=16, color='b')
		plt.grid(True)

		# customize the x-axis title
		t = []
		span = 60
		for i, date in enumerate(zipped[0]):
			if i % span == 0:
				t.append(date)
		ax = plt.gca()
		ax.xaxis.set_major_locator(MultipleLocator(span))
		locs, labels = plt.xticks()
		plt.xticks(locs, t)
		fig.autofmt_xdate()

		plt.savefig(out_file)

	def plot_time(self, dat, key, start_time, end_time):
		dat = sp.parse_data(dat, [key], [u"最高价", u"收盘价", u"开盘价", u"最低价"])
		start_time = time.strptime(start_time, "%Y-%m-%d")
		end_time = time.strptime(end_time, "%Y-%m-%d")
		dat = filter(lambda d: d[0] > start_time and d[0] < end_time, dat)
		dat = sorted(dat, key = lambda r: r[0], reverse=False)
		to_str = lambda d: "%d-%d-%d" %(d.tm_year, d.tm_mon, d.tm_mday)
		dat = map(lambda d: [to_str(d[0])] + d[1:], dat)
		w_file = open('plot.dat', 'w')
		w_file.write("# date max close open min\n")
		for k in dat:
			w_file.write("%s\n" % " ".join(k))
		w_file.close()
		sp.plot(dat, "plot.png")
		print "Plot plot.png"

if __name__ == "__main__":
	si = SGEDownload()
	si.update("data.out")
	sp = SEGPlot()
	# print dat Au9999 Ag99.99 
	sp.plot_time(si._data, "Au9999", "2010-01-01", "2014-12-30")

