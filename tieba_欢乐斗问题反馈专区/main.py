# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 14:18:24 2018
@author: ruiwen
"""
import json
import requests
from lxml import etree
import re 

####huanledoudizhu贴吧主题爬取######### 
def get_url(url):
    '''
    this function get xpath selector,timeout=3s
    '''
    try:
        response=requests.get(url, cookies=None, headers=None,timeout=3)
        html=response.content 
        selector = etree.HTML(html)
        return selector
    except Exception as e:
        print("response.status_code not correct")
        print(url,e)
        
def get_all_page(f_out):
    url_list=[]
    count=1
    root_url="https://tieba.baidu.com/f?kw=%E6%AC%A2%E4%B9%90%E6%96%97%E5%9C%B0%E4%B8%BB&ie=utf-8&pn="
    for page_num in range(0,26950,50):
        url_list.append(str(page_num))
    #get all single page's subject
    for url in url_list:
        print("第%d个详情页面"%(count))
        url=root_url+url
        count+=1
        try:
            parse_single_page(url,f_out)
        except Exception as e:
            print("error occur during get url:",url)
    f_out.close()
    
#input[starts-with(@name,'name1')] 
def parse_single_page(url,f_out):   
    page_list=[]    
    selector=get_url(url=url)
    page_subject_xpath_str='//ul[@id="thread_list"]/li[@class=" j_thread_list clearfix"]/\
                        div[@class="t_con cleafix"]/div[@class="col2_right j_threadlist_li_right "]\
                        /div[@class="threadlist_lz clearfix"]/div[starts-with(@class,"threadlist_title pull_left j_th_tit ")]\
                        /a'
                        
    page_detail_xpath_str='//ul[@id="thread_list"]/li[@class=" j_thread_list clearfix"]/\
                        div[@class="t_con cleafix"]/div[@class="col2_right j_threadlist_li_right "]\
                        /div[@class="threadlist_detail clearfix"]/div[@class="threadlist_text pull_left"]\
                        /div[@class="threadlist_abs threadlist_abs_onlyline "]/text()'
    huifu_num_xpath_str='//ul[@id="thread_list"]/li[@class=" j_thread_list clearfix"]/\
                        div[@class="t_con cleafix"]/div[@class="col2_left j_threadlist_li_left"]\
                        /span/text()'
    huifu_num_list=selector.xpath(huifu_num_xpath_str)
    page_detail=selector.xpath(page_detail_xpath_str)
    page_content_list=selector.xpath(page_subject_xpath_str)
    for ele in page_content_list:
        subject_str=''.join(ele.xpath('text()'))
        page_list.append(subject_str)
    #print(len(huifu_num_list),len(page_list),len(page_detail))
    if len(huifu_num_list)!=len(page_content_list):
        print("len(huifu_num_list)!=len(page_content_list)")
        print(url)
        print(huifu_num_list)
        for each in page_content_list:
            print(each)
            
    else:
        N=len(huifu_num_list)
        for i in range(N):
            page_con=page_list[i].replace("\t",'').replace("\n",'').replace("\r",'').strip()
            page_de=page_detail[i].replace("\t",'').replace("\n",'').replace("\r",'').strip()
            f_out.write(page_con+"\t"+page_de+"\t"+huifu_num_list[i]+"\n")




def main():
    f_out=open("./subject_data.txt","w",encoding="utf8")
    get_all_page(f_out)
if __name__ == "__main__":
    main()    
