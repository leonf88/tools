#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Update the IEEE CSDL bibtex with article Abstract

from urllib2 import urlopen
from pyquery import PyQuery
from threading import Thread, Event
from Queue import Queue
from os import path
import xml.etree.ElementTree as et
import sys, re, urlparse, os, urllib

class ModifyBibItem(Thread):
    _url_re=re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    _url_timeout=100

    def __init__(self,lq,e):
        super(ModifyBibItem, self).__init__()
        self.linkQ=lq
        self.event=e
        self.curmods=None
        self.curpq=None

    def _downpdf(self,q):
        dl=q('#abs-articleinfo .abs-pdf a')
        file_url=dl.attr('href')
        if file_url is not None:
            pdfpath = path.join(os.getcwd(), path.basename(self.curmods.get('ID'))+".pdf")
            urllib.urlretrieve(file_url, pdfpath)
            dname=self._getTagAttr('titleInfo/title')+"-"+self._getTagAttr("part/detail[@type='issue']/number")
            print "[DOWNLOAD] "+dname+' => '+pdfpath
            dfile.write("[DOWNLOAD] %s => %s\n" %(dname.encode('utf8'), pdfpath))
            return pdfpath
        return None

    # retrieve the url to get the content
    def _setpage(self, url):
        if self._url_re.match(url) is None:
            raise UserWarning("Invalid url: "+url)
        cur_url=urlparse.urlparse(url).geturl()
        context=urlopen(url=cur_url, timeout=self._url_timeout).read()
        self.curpq=PyQuery(context)
        self.conte=context

    # get the attribute of certain tag
    def _getTagAttr(self,xpath,attr=None):
        if attr is None or attr == '':
            s=self.curmods.find(getQNameStr(xpath)).text
        else:
            s=self.curmods.find(getQNameStr(xpath)).get(attr)
        if s is None:
            s=''
        return s

    # input is one of the xml DOM node 'mods'
    def _addAbstAttr(self, one_bib):
        d=one_bib.find(getQNameStr("identifier[@type='doi']"))
        if d is not None:
            print "Get information from", d.text
            cnt=5
            while cnt != 0:
                self._setpage(d.text)
                if len(self.curpq('#main-content')) != 0:
                    break
                else:
                    cnt-=1
            if cnt == 0:
                raise UserWarning('no context')
            # get abstract information
            abs_el=one_bib.makeelement(getQNameStr('abstract'),{})
            abs_el.text=self.curpq('#abs-abscontent .abs-articlesummary').text()
            if abs_el.text is not None and abs_el.text != '':
                one_bib.append(abs_el)
            # down pdf
            pdfpath=self._downpdf(self.curpq)
            if pdfpath is not None:
                file_el=one_bib.makeelement(getQNameStr('file'),{})
                pdfpath=':'+pdfpath[1:]+':pdf'
                file_el.text=pdfpath
                one_bib.append(file_el)

    def run(self):
        while self.event.is_set() and self.linkQ.empty() is False:
            try:
                self.curmods=self.linkQ.get()
                self._addAbstAttr(self.curmods)
            except Exception as e:
                print "[FAILED]", self.curmods.get('ID'), " for", e
                break

# get the tag string based on certain namespace
def getQNameStr(s):
    res=''
    for subs in s.split('/'):
        res+=str(et.QName(nms,subs))+'/'
    return res[:-1]

# get new xml file which add the abstract information, work with multiple threads
def getnewxml(filename):
    xmlet=et.parse(filename)
    er=xmlet.getroot()
    q=Queue()
    e=Event()
    e.set()
    for m in er:
        q.put(m)

    max_thread_num=10

    if q.qsize() < max_thread_num:
        max_thread_num=q.qsize()

    ts=[]
    for t in range(max_thread_num):
        ts.append(ModifyBibItem(q,e))

    for t in ts:
        t.start()

    for t in ts:
        t.join()

    fn=filename+'2'
    xmlet.write(fn)

    return fn

def xml2bib(f):
    fn=path.basename(f)
    f_dir=path.dirname(f)
    new_fn=getfname(fn)+".bib"
    f_path=path.join(f_dir,new_fn)
    cnt=1
    orig_f_path=f_path
    while path.exists(f_path):
        f_path=orig_f_path+"."+str(cnt)
        cnt+=1
    os.system('xml2bib %s > %s' % (f, f_path))
    print "Save in", f_path
    return f_path

def bib2xml(f):
    fn=path.basename(f)
    f_dir=path.dirname(f)
    new_fn=getfname(fn)+".xml"
    f_path=path.join(f_dir,new_fn)
    os.system('bib2xml %s > %s' % (f, f_path))
    return f_path

# remove the suffix of filename
def getfname(f):
    try:
        n=f.rindex('.')
        return f[:n]
    except:
        return f

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: %s [bibtex file]' % sys.argv[0]
        sys.exit(-1)

    nms='http://www.loc.gov/mods/v3'
    dfile=open('down.ls','a')
    filename=sys.argv[1]
    et.register_namespace('',nms)
    f=path.join(os.getcwd(),filename)
    fxml=bib2xml(f)
    fxml2=getnewxml(fxml)
    xml2bib(fxml2)
    os.remove(fxml)
    os.remove(fxml2)
    dfile.close()

