#!/usr/bin/env python

import xlrd, xlwt, sys

# switch the excel row and column value
def swapCR(fp,outfp=None, sheet=None):
    try:
        data = xlrd.open_workbook(fp)
        if outfp is None:
            outfp=fp+".xls"
        xlo=xlwt.Workbook()

        # st: output sheet
        # tb: input table        
        def __wt(st,tb):
            for nr in range(0,tb.nrows):
                for nc in range(0,tb.ncols):
                    st.write(nc,nr,tb.cell(nr,nc).value)
        if sheet is None:
            for st_name in data.sheet_names():
                st=xlo.add_sheet(st_name)
                tb = data.sheet_by_name(st_name)
                __wt(st,tb)
        else:
            if type(sheet) is int or sheet.isdigit():
                st=xlo.add_sheet("sheet1")
                tb = data.sheet_by_index(int(sheet))
            else:
                st=xlo.add_sheet(sheet)
                tb = data.sheet_by_name(sheet)
            __wt(st,tb)
        
        xlo.save(outfp)
    except Exception, e:
        print str(e)
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: %s <input XLS file> (<sheet index or name>) (<output XLS file>)" % sys.argv[0]
        sys.exit(-1)
    fp = sys.argv[1]
    if len(sys.argv)==2:
        swapCR(fp)
    elif len(sys.argv)==3:
        swapCR(fp,sheet=sys.argv[2])
    else:
        swapCR(fp,sys.argv[3],sys.argv[2])
        