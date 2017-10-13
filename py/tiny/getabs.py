#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO show title and add the abstraction end constraints
import sys
import glob
import re
from os import path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import *

reload(sys)
sys.setdefaultencoding('utf-8')

def getAbs(pdfFile=None):
    print pdfFile
    fp = open(pdfFile, 'rb')
# Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
    doc = PDFDocument(parser)
# Supply the password for initialization.
# (If no password is set, give an empty string.)
    doc.initialize()
# Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
# Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
# Create a PDF device object.
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

# The Abstract is usually in the first page
# Extract the text between "abstract" and "introduction"
    pagenos=[0]
    for (pageno, page) in enumerate(PDFPage.create_pages(doc)):
        if pagenos and (pageno not in pagenos):
            continue
        interpreter.process_page(page)
        layout = device.get_result()
        flag=False
        for x in layout:
            if(isinstance(x,LTTextBox)):
                if(re.search('introduction', x.get_text(), re.IGNORECASE) or
                        re.search('Categories and Subject Descriptors', x.get_text(), re.IGNORECASE)):
                    break
                if(re.search('abstract', x.get_text(), re.IGNORECASE)):
                    flag=True
                if flag:
                    print(x.get_text())
        break

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: %s [file path]' % sys.argv[0]
        sys.exit(-1)
    inp=sys.argv[1]
    if path.isfile(inp):
       getAbs(inp)
    else:
       for f in glob.glob(path.join(inp,"*.pdf")):
           if path.isfile(f):
               getAbs(f)
