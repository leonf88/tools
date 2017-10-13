csdlbib.py
==

功能：下载 IEEE CSDL 里面论文的摘要信息（因为 IEEE CSDL 里面的 Bibliographic 没有 Abstract 的内容）。

设计思路：将从 CSDL 里面下载的 bibtex 转化为 xml，提取每篇 article 的 DOI，然后解析网页获得 Abstract 信息，整理生成新的 xml 文件，最后转换为 bibtex 文件。

说明：使用需要安装 [bibutils] [1]。

[1]:http://sourceforge.net/p/bibutils/home/Bibutils/

getabs.py
==
依赖软件：pdfminer

    $ sudo pip install pdfminer

功能：摘取 PDF 中的 abstract 字段

使用：输入可以是文件或者目录。如果是目录，则处理目录下所有以 pdf 后缀结尾的文件。

xlscr.py
==
依赖软件：xlrd, xlwt

    $ sudo pip install xlrd 
    $ sudo pip install xlwt

功能：EXCEL 文件的行列转换
