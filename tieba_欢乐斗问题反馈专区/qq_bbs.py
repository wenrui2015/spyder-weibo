# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 21:00:26 2018

@author: ruiwen
"""
import json
import requests
from lxml import etree
import re 
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

def qq_wentifankui_single_page(url,f_out):
    page_title_xpath_str='//div[@class="mn"]/div[@id="threadlist"]/div[@class="bm_c"]/form/table\
                        /tbody[starts-with(@id,"normalthread_")]/tr/th/a[1]/@href'
                            
    huifu_num_xpath_str='//div[@class="mn"]/div[@id="threadlist"]/div[@class="bm_c"]/form/table\
                        /tbody[starts-with(@id,"normalthread_")]/tr/td[@class="num"]/em/text()'
    selector=get_url(url=url)
    page_title_list=selector.xpath(page_title_xpath_str)
    huifu_num_list=selector.xpath(huifu_num_xpath_str)
    if len(huifu_num_list)!=len(page_title_list):
        print("len(huifu_num_list)!=len(page_url_list)")
        print(url,len(huifu_num_list),len(page_title_list))
    else:
         N=len(huifu_num_list)
         for i in range(N):
             f_out.write(page_title_list[i]+"\t"+huifu_num_list[i]+"\n")
             
def qq_jianyi_detail(url,f_out,num):
    title_xpath_str='//div[@id="wp"]/div[@id="ct"]/div[@id="postlist"]/table[1]\
                    /tr/td[@class="plc ptm pbn vwthd"]/h1[@class="ts"]/a[2]/text()'
    main_topic_xpath_str='string(//div[@id="wp"]/div[@id="ct"]/div[@id="postlist"]\
                        /div[1]/table/tr/td[@class="plc"]/div[@class="pct"]/div[@class="pcb"])'
    selector=get_url(url=url)
    the_title=selector.xpath(title_xpath_str)
    the_title=''.join(the_title)
    topic_main=selector.xpath(main_topic_xpath_str)
    topic_main=topic_main.replace("\t",'').replace("\n",'').replace("\r",'').strip()
    f_out.write("\t".join([the_title,topic_main,num])+"\n")
    print(the_title)



#qq_jianyi_detail(url=url)
def jianyi_detail():
    url_list=[]
    count=1
    f_out=open("origin_data/qqbbs_jianyi_detail.txt","w",encoding="utf8")
    with open("origin_data/qqbbs_jianyi_url.txt")as fi:
        for line in fi:
            url_list.append(line)
    for ele in url_list:
        url,num=ele.split("\t")
        num=num.strip()
        url="http://qqgame.gamebbs.qq.com/"+url
        print("第%d个详情页面"%(count))
        count+=1
        try:
            qq_jianyi_detail(url,f_out,num)
        except Exception as e:
            print(e)
        #except Exception as e:
            
#问题页和活动咨询页
def wenti_huodong():            
    f_out=open("origin_data/qqbbs_jianyi_url.txt","w",encoding="utf8")            
    url="http://qqgame.gamebbs.qq.com/forum.php?mod=forumdisplay&fid=30710&typeid=33&typeid=33&filter=typeid&page=1"
    count=1
    for i in range(1,22):
        print("第%d个页面"%(count))
        count+=1#http://qqgame.gamebbs.qq.com/forum.php?mod=forumdisplay&fid=30710&typeid=32&filter=typeid&typeid=32&page=2
        url="http://qqgame.gamebbs.qq.com/forum.php?mod=forumdisplay&\
        fid=30710&typeid=34&typeid=34&filter=typeid&page="+str(i)
        qq_wentifankui_single_page(url,f_out)
    f_out.close()



jianyi_detail()


#
















