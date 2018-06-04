# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 11:04:39 2018

@author: ruiwen
"""
import sys
from http_util import get_url
import re


def get_tianya(page_num,f_out):
    '''
    this function get all page's subject and generator a url file contain all the url
    
    page_num:the number of subject pages you want to get
    f_out:the url file
    url:first page of question and awnser board on tianya BBS
    '''
    selector=get_url(url="http://bbs.tianya.cn/list.jsp?item=907&sub=2")
    #get the next page's id
    next_id=selector.xpath('//*[@id="main"]/div[@class="short-pages-2 clearfix"]/div[@class="links"]/a')
    next_id=str(next_id[-1].xpath("@href")[0])
    find_is=re.findall("(.*)nextid=(.*)",next_id)
    next_page_id=find_is[0][1];
    next_page_url=[]
    block=selector.xpath('//*[@id="main"]/div[@class="mt5"]/table/tbody')
    huifushu_list=[]
    #the first page
    for blo in block[1:]:
        tmp=blo.xpath('tr/td[1]/a/@href')
        huifushu=blo.xpath('./tr/td[4]/text()')
        huifushu_list+=huifushu
        next_page_url=next_page_url+tmp
    
    #next all page
    for i in range(page_num):
        try:
            current_url="http://bbs.tianya.cn/list.jsp?item=907&sub=2"+"&nextid="+next_page_id
            selector=get_url(current_url)
            next_id=selector.xpath('//*[@id="main"]/div[@class="short-pages-2 clearfix"]/div[@class="links"]/a')
            next_id=str(next_id[-1].xpath("@href")[0])
            find_is=re.findall("(.*)nextid=(.*)",next_id)
            next_page_id=find_is[0][1]
            block=selector.xpath('//*[@id="main"]/div[@class="mt5"]/table/tbody')
            for blo in block[1:]:
                tmp=blo.xpath('tr/td[1]/a/@href')
                huifushu=blo.xpath('./tr/td[4]/text()')
                huifushu_list+=huifushu
                next_page_url=next_page_url+tmp
        except Exception as e:
            print("get pages url error!!!,the error url is:",current_url,e)

    valid_url=0       
    print("len_list:",len(next_page_url))
    print("huifushu_list:",len(huifushu_list)) 
    if len(huifushu_list)!=len(next_page_url):
        print("len(huifushu_list)!=len(next_page_url)")
    else:
        for i in range(len(next_page_url)):
            if huifushu_list[i]==str(0):
                continue
            f_out.write(huifushu_list[i]+"\t"+next_page_url[i]+"\n")
            valid_url+=1
    print("valid page url is:",valid_url)
    f_out.close()
    #return [int(ele) for ele in huifushu_list],next_page_url
    
    

def main():
    f_out="./detail_url.txt"
    page_num=int(sys.argv[1])
    get_tianya(page_num,f_out)

if __name__ == "__main__":
    main()















    
    
    
    