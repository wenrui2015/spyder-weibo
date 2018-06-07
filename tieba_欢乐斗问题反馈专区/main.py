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




#####shouyoubao#####
def shouyou_single_page(url,f_out):
    page_url_xpath_str='//div[@class="gb-bbs-center"]/div[@class="gb-list-wrap gb-clear"]\
                            /div[@class="gb-cols-7"]/div[@class="gb-list-inner"]\
                            /ul[@class="gb-bbs-list adm-bbs-list"]/li/div[@class="gb-bl-title"]/a/@href'
                            
    huifu_num_xpath_str='//div[@class="gb-bbs-center"]/div[@class="gb-list-wrap gb-clear"]\
                            /div[@class="gb-cols-7"]/div[@class="gb-list-inner"]\
                            /ul[@class="gb-bbs-list adm-bbs-list"]/li/div[@class="gb-fun"]/span[@class="gb-p-talk"]/text()'
    selector=get_url(url=url)
    page_url_list=selector.xpath(page_url_xpath_str)
    huifu_num_list=selector.xpath(huifu_num_xpath_str)
    if len(huifu_num_list)!=len(page_url_list):
        print("len(huifu_num_list)!=len(page_url_list)")
        print(url,len(huifu_num_list),len(page_url_list))
    else:
         N=len(huifu_num_list)
         for i in range(N):
             f_out.write(page_url_list[i]+"\t"+huifu_num_list[i]+"\n")

def shouyou_all_page(f_out):
    url_list=[]
    count=1
    for page_num in range(1,2601,1):
        #不同的板块只需要改这里就行了  bug:http://bbs.g.qq.com/forum-56729-1-1-0.html
        url_list.append("http://bbs.g.qq.com/forum-56729-"+str(page_num)+"-1-0.html")
    #get all single page's subject
    for url in url_list:
        print("获得第%d个页面"%(count))
        count+=1
        try:
            shouyou_single_page(url,f_out)
        except Exception as e:
            print("error occur during get url:",url)
    f_out.close()
def get_reply(topic_id):
    reply_list=[]
    print(topic_id)#http://bbs.g.qq.com/forum/queryPageCommentInfo?forum_id=56640&page_no=1&page_size=10&topic_id=8352783844729280
    html=requests.get('http://bbs.g.qq.com/forum/queryPageCommentInfo?forum_id=56729&page_no=1&page_size=10&topic_id='+topic_id)
    data=html.content.decode("utf8")
    data=json.loads(data)['data']
    data=data["pageContent"]
    if len(data)!=0:
        for ele in data:
            reply_list.append(ele["content_info"]["content"])
        return "pinglun".join(reply_list)
    else:
        return ''
def shouyou_detail(url,num,f_out):
    selector=get_url(url=url)
    head_xpath_str='//div[@class="gb-bbs-center"]/div[@class="gb-bbs-topside js-bbs-topside gb-clear"]\
    /div[@class="gb-bbs-title"]/strong/text()'
    main_topic_xpath_str='string(//div[@class="gb-bbs-content gb-layout gb-clear"]\
    /div[@id="js_main_topic"]/div[@class="gb-floor-r"]/div[@class="gb-floor-inner gb-clear"]\
    /div[@class="gb-p-c"]/div[@class="gb-p-inner"])'
    head_content=''.join(selector.xpath(head_xpath_str)).replace("\t",'').replace("\n",'').strip()
    subject_main_topic=''.join(selector.xpath(main_topic_xpath_str)).replace("\t",'').replace("\n",'').strip()
    find_is=re.findall("http://bbs.g.qq.com/thread-(.*)-1-1-0-0.html",url)#/thread-1937403207795136-1-1-0-0.html
    topic_id=find_is[0]
    all_reply=get_reply(topic_id).replace("\t",'').replace("\n",'').strip()
    f_out.write("\t".join([head_content,subject_main_topic,all_reply,num]))#+"\n"
def shouyou():
    count=1
    f_out=open("origin_data/shouyou_detail.txt","a",encoding="utf8") 
    url_num=[]
    with open("origin_data/shouyou_subject_url.txt")as fi:
        for line in fi:
            url_num.append(line)
    fi.close()
    for line in url_num[19372:]:
        try:
            print("第%d个页面"%(count+19372),line)
            count+=1
            line=line.split("\t")
            url=line[0];num=line[1]
            shouyou_detail("http://bbs.g.qq.com"+url,num,f_out)
        except Exception as e:
            print("error",line)
    f_out.close()
#f_out=open("origin_data/shouyou_subject_url.txt","w",encoding="utf8")
#shouyou_all_page(f_out)        

def main():
    #shouyou()
    #f_out=open("origin_data/shouyou_zonghe_subject_url.txt","w",encoding="utf8")
    #shouyou_all_page(f_out)  
    #f_out=open("origin_data/subject_data.txt","w",encoding="utf8")
    #get_all_page(f_out)
if __name__ == "__main__":
    main()                      
























