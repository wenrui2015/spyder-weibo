# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 09:43:48 2018

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
def get_metainfo_ofpage(url,huifu_num=2,iswenda=True):
    '''
    this function get the meta info of a subuject detail page including 
    all the page num of this subject
    
    return: all the url_list of this subject
    huifu_num:the reply number of this subject,if 0,ignore this subject
    iswenda:flag of weather it is wenda board or superior board since they have diffirent page struct
    '''
    url_list=[]
    if huifu_num<=0:
        return "empty comments!!!"
    else:
        selector=get_url(url)
        try:
            if iswenda:
                other_page=selector.xpath('//div[@class="wd-question"]/div[@class="wd-page tc"]/div[@class="atl-pages"]/form/a/text()')
                current_page=selector.xpath('//div[@class="wd-question"]/div[@class="wd-page tc"]/div[@class="atl-pages"]/form/strong/text()')
            else:
                other_page=selector.xpath('//div[@id="post_head"]/div[@class="mb15 cf"]/div[@class="atl-pages"]/form/a/text()')
                current_page=selector.xpath('//div[@id="post_head"]/div[@class="mb15 cf"]/div[@class="atl-pages"]/form/strong/text()')
            page=other_page+current_page
            page=[int(ele) for ele in page if ele.isdigit()]
            page=max(page)
            flag=1
        except Exception as e:
            flag=0
    if flag==0:
         return [url]
    else:
         for i in range(page):
             if iswenda:
                 find_is=re.findall("(.*)-1.shtml",url)[0]
             else:
                 find_is=re.findall("(.*).shtml",url)[0]
             N=len(find_is)-1
             find_is=find_is[0:N]
             if iswenda:
                 generate_url=find_is+str(i+1)+"-1.shtml"
             else:
                 generate_url=find_is+str(i+1)+".shtml"
             url_list.append(generate_url)
         return url_list
#kk=get_metainfo_ofpage(url="http://bbs.tianya.cn/post-907-64209-1-1.shtml",huifu_num=2,iswenda=True)     

def get_wenda_detail(url):
    '''
    this function is the main function which concate one "wenda" object detail page 
    into a str line with special designed separator. follow  function "parse_pagetext"
    will parse this line into:
        question \t  awns
    the detail struct design please refer "页面结构解析说明.pdf"
    
    return:a line contain all the infomation of a subject separated by designed separator
    '''
    selector=get_url(url)
    #get the subject head and all commment block,note that the comment may contain other comment
    title_head=selector.xpath('//div[@class="wd-question"]/div[@class="q-title"]/h1/span/text()')[0]
    all_awns=selector.xpath('//div[@class="wd-answer"]/div[@class="answer-wrapper"]/div[@class="answer-item atl-item"]')
    block_list=[]
    if len(all_awns)==0:
        print("this page have no comments!!!")
        return None
    for awns in all_awns:
        u_comment_list=[]
        name_list=[]
        content_user=awns.xpath('./div[@class="user"]/a/text()')[0]
        real_content=" ".join(awns.xpath('./div[@class="content"]/text()'))
        content=content_user+"@@ucontent@@"+real_content
        reply_id=awns.xpath('./@replyid')[0]
        tmp_list=url.split('-')
        item_id=tmp_list[1];article_id=tmp_list[2]
       
        reply_url=('http://bbs.tianya.cn/api?method=bbs.api.getCommentList&params.item='+
                  item_id+"&params.articleId="+article_id+"&params.replyId="+reply_id+
                  '&params.pageNum=1')
        re_request_num=0
        while(re_request_num<2):
          html=requests.get(reply_url)
          #成功，则直接返回
          if html.status_code==200:
            break
          else:
            re_request_num+=1
        if html.status_code!=200 and re_request_num>=2:
          print("reply_url网页请求失败:",reply_url)
          continue
        data=html.content.decode("utf8")
        data=json.loads(data)['data']
        for ele in data:
          comment=ele["content"].split("</a>：")
          if len(comment)>1:
            alt_user=comment[0].split('">')[1]
            comment_content=comment[1]
            comment=alt_user+"@@alt_ucomment@@"+comment_content
          else:
            comment=comment[0]
          name=ele['author_name']
          u_comment=name+"@@u_comment@@"+comment
          
          u_comment_list.append(u_comment)
          name_list.append(name)
        block_comment="@@comment@@".join(u_comment_list)
        block=content+"@@concom@@"+block_comment
        block_list.append(block)
    all_block="@@block@@".join(block_list)
    #print(title_head+"@@headblock@@"+all_block)
    return (title_head+"@@headblock@@"+all_block)
    #f_out.write(title_head+"@@headblock@@"+all_block+"\n")    

#fucntion test
#get_wenda_detail(url='http://bbs.tianya.cn/post-907-63967-1-1.shtml#217489')
    


def parse_block(block_line,title,f_out):
  '''
  this function is the main function that parse all comments  of a subject
  which parse a comment content(note the comment may contain comments) to:
  qestion "\t" awnser
  
  block_line:all the comments' line 
  title:the title of the subject
  f_out:the final file of generated question & awnser pair
  '''
  line=block_line.split('@@concom@@')
  content=line[0]
  pinglun_line=line[1]
  content=content.split("@@ucontent@@")
  author_pinglun_dict=dict()
  content_user=content[0]
  real_content=content[1].replace('\t','')
  f_out.write(title+"\t"+real_content+"\n")
  author_pinglun_dict[content_user]=real_content
  if pinglun_line=="":
    return None
  pinglun_list=pinglun_line.split("@@comment@@")
  for each_pinglun in pinglun_list:
    each_pinglun_list=each_pinglun.split("@@u_comment@@")
    pinglun_author=each_pinglun_list[0]
    alt_pingluncontent=each_pinglun_list[1]
    alt_pingluncontent_list=alt_pingluncontent.split("@@alt_ucomment@@")
    if len(alt_pingluncontent_list)>1:
      alt_author=alt_pingluncontent_list[0]
      pingluncontent=alt_pingluncontent_list[1]
      #author_altuser_dict[pinglun_author]=alt_author
    else:
      alt_author=""
      pingluncontent=alt_pingluncontent_list[0]
    pingluncontent=pingluncontent.replace("\t",'')
    author_pinglun_dict[pinglun_author]=pingluncontent
    #如果不是alt别人的评论，则一定是alt作者的
    if alt_author=="":
      f_out.write(real_content+"\t"+pingluncontent+"\n")
    else:
      if alt_author in author_pinglun_dict:
        f_out.write(author_pinglun_dict[alt_author]+"\t"+pingluncontent+"\n")
  
#analysis question and anwser page,generator line text 
def parse_pagetext(line,f_out):
  '''
  this function parse the page line generated by function "get_wenda_detail"
  
  line:the page line generated by function "get_wenda_detail"
  '''
  #split the subject title and all deep-one(the comment to origin subject,
  #when deep-two refer the comments to comment)
  line=line.split("@@headblock@@")
  title=line[0];block=line[1]
  #split all the comment
  block_list=block.split("@@block@@")
  for block_line in block_list:
    parse_block(block_line,title,f_out)
    

#该网址必须有效      
def get_singleurl_detail(url,f_out):
    '''
    this function is the main function which concate one "jingping" object detail page 
    into a str line with special designed separator
    the detail struct design please refer "页面结构解析说明.pdf"
    
    return:a line contain all the infomation of a subject separated by designed separator
    '''
    selector=get_url(url)
    review_block=selector.xpath('//div[@class="atl-item"]/div[@class="atl-content"]/div[@class="atl-con-bd clearfix"]')
    print(review_block)
    for each_review in review_block:
        print_string=''
        #若果有多行的话可能会有br标签，可能是个列表，需要处理
        bb_content=" ".join(each_review.xpath('div[@class="bbs-content"]'))
        print_string+="start###"
        #f_out.write("##########################zhengbanneirong#######################\n")
        #f_out.write(bb_content.xpath('string(.)').replace("\t",'').strip())
        print_string+=bb_content.xpath('string(.)').replace("\t",'').strip()
        #f_out.write("\n\n")
        item_reply_view=each_review.xpath('div[@class="item-reply-view"]/div[@class="ir-list"]/ul/li')
        #f_out.write("____pinglun_____\n")
        print_string+="pinglun"
        if len(item_reply_view)<1:
                #f_out.write("%%%%%%%%%%%%%%%%%%%%%%%%%%yigetieziwanle%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
                print_string+="over###\n"
                print("内容————",print_string)
                f_out.write(print_string)
                continue
        review=[]
        for each_view in item_reply_view:
            #each_view_userid=each_view.xpath('@_userid')[0]
            #each_view_username=each_view.xpath('@_username')[0]
            #若果有多行的话可能会有br标签，可能是个列表，需要处理
            each_view_content=" ".join(each_view.xpath('./span[@class="ir-content"]/text()'))
            #f_out.write("_______________________name="+each_view_username+"\n")
            #f_out.write("_______________________id="+each_view_userid+"\n")
            #f_out.write("_______________________veiw content="+each_view_content+"\n")
            review.append(each_view_content)
        review="comment".join(review)
        print_string+=review
        print_string+="over###\n"
        print("内容————",print_string)
        f_out.write(print_string)        


def get_all_detail(url="http://bbs.tianya.cn/post-907-59777-2.shtml",f_out=None,huifu_num=1):
    '''
    this function get the output of a "wenda" page
    '''
    url_list=get_metainfo_ofpage(url,huifu_num)
    if url_list=="empty comments!!!":
        print("该页没有评论:",url)
        return None
    else:
        #for each url
        for url in url_list:
            print("_______",url)
            #get the page line of this url
            page_line=get_wenda_detail(url=url)
            #有head但是没有确匹配不到评论内容的情况下，会出现这种诡异情况
            if not page_line:
              continue
            print("******page_title",page_line[0:60])
            #parse the page line
            parse_pagetext(page_line,f_out)


def run_spider(detail_f):
    f_out=open("E:/spyer_pro/crawl_data/tianya.txt",'w',encoding="utf8")
    url_list=[]
    huifu_num_list=[]
    #read the url list
    with open(detail_f)as fi:
        for line in fi:
            line=line.split("\t")
            url=line[1];huifu_num=int(line[0])
            url_list.append(url)   
            huifu_num_list.append(huifu_num)
    N=len(huifu_num_list)
    #parse each url ,if error occur,ignore this url and print the error infomation、start next url crawl
    for i in range(N):
      try:
        print("这是第%d个详情页"%i,"http://bbs.tianya.cn"+url_list[i]+str(huifu_num_list[i]))
        get_all_detail(url="http://bbs.tianya.cn"+url_list[i],f_out=f_out,huifu_num=huifu_num_list[i])
      except Exception as e:
        print(e,"详情页:","http://bbs.tianya.cn"+url_list[i])
#特殊的页面bug:#http://bbs.tianya.cn/post-907-24984-3-1.shtml#204824#  
def main():
    detail_f="E:/spyer_pro/crawl_data/detail_url.txt"
    run_spider(detail_f)

if __name__ == "__main__":
    main()



















