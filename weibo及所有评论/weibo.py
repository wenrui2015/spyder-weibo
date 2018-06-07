# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 12:48:27 2018

@author: ruiwen
"""
import os
import re
from selenium import webdriver
import time
import pickle
import requests
from lxml import etree
from conf import PHANTOM_JS_PATH,COOKIES_SAVE_PATH,account_id,account_password,user_id,url_login 

def is_number(s):
    try:
        float(s)
        return True
    except ValueError as e:
        return False

def get_selector(url,cookie,headers):
    '''
    this function get xpath selector,timeout=3s
    '''
    try:
        response=requests.get(url, cookies=cookie, headers=headers,timeout=3)
        html=response.content 
        selector = etree.HTML(html)
        return selector
    except Exception as e:
        print(url,e)


def get_cookie(account_id, account_password,url_login):
    phantom_js_driver_file = os.path.abspath(PHANTOM_JS_PATH)
    if os.path.exists(phantom_js_driver_file):
        driver = webdriver.PhantomJS(phantom_js_driver_file)
        driver.get(url_login)  
        driver.set_window_size(1920, 1080)
        #这个时间一定要稍微长一点，否则可能获取失败  
        time.sleep(10)
        driver.find_element_by_xpath('//input[@id="loginName"]').send_keys(account_id)
        driver.find_element_by_xpath('//input[@id="loginPassword"]').send_keys(account_password)
            
        print('account id: {}'.format(account_id))
        print('account password: {}'.format(account_password))
        driver.find_element_by_xpath('//a[@id="loginAction"]').click()
        time.sleep(5)  
        try:
            cookie_list = driver.get_cookies()
            cookie_string = ''
            for cookie in cookie_list:
                if 'name' in cookie and 'value' in cookie:
                    cookie_string += cookie['name'] + '=' + cookie['value'] + ';'
            if 'SSOLoginState' in cookie_string:
                print('success get cookies!! \n {}'.format(cookie_string))
                if os.path.exists(COOKIES_SAVE_PATH):
                    with open(COOKIES_SAVE_PATH, 'rb') as f:
                        cookies_dict = pickle.load(f)
                    if cookies_dict[account_id] is not None:
                        cookies_dict[account_id] = cookie_string
                        with open(COOKIES_SAVE_PATH, 'wb') as f:
                            pickle.dump(cookies_dict, f)
                        print('successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
                    else:
                        pass
                else:
                    cookies_dict = dict()
                    cookies_dict[account_id] = cookie_string
                    with open(COOKIES_SAVE_PATH, 'wb') as f:
                        pickle.dump(cookies_dict, f)
                    print('successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
                return cookies_dict
            else:
                print('error, account id {} is not valid, pass this account,you may longer the time.sleep()\n'
                      .format(account_id))
                pass

        except Exception as e:
            print(e)

    else:
        print('can not find PhantomJS driver, please download from http://phantomjs.org/download.html based on your '
              'system.')
def init_cookie(update_cookies=False):
    if update_cookies:
        cookies_dict=get_cookie(account_id, account_password,url_login)
        print('getting cookies finished. starting scrap..')
    else:
        if os.path.exists(COOKIES_SAVE_PATH):
            with open(COOKIES_SAVE_PATH, 'rb') as f:
                cookies_dict = pickle.load(f)
            pass
        else:
            cookies_dict=get_cookie(account_id, account_password,url_login)
            print('cookies file not exist,getting cookies finished. starting scrap..')
    cookies_string = cookies_dict[account_id]
    cookie = {
                "Cookie": cookies_string
             }
    return cookie
def init_headers():
    """
    avoid span
    :return:
    """
    headers = requests.utils.default_headers()
    user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0'
        }
    headers.update(user_agent)
    print('headers: ', headers)
    headers = headers
    return headers
def run_spyder():
    weibo_scraped=0
    weibo_detail_urls=[]
    weibo_content=[]
    num_zan_list=[]
    num_forwarding_list=[]
    num_comment_list=[]
    cookie=init_cookie(update_cookies=False)
    headers=init_headers()
    if is_number(user_id):
        url = 'http://weibo.cn/u/%s?filter=%s&page=1' % (user_id,0)
        print(url)
    else:
        url = 'http://weibo.cn/%s?filter=%s&page=1' % (user_id,0)
        print(url)
    selector=get_selector(url,cookie,headers)
    #get the user name
    print("get the user name......")
    user_name = selector.xpath('//table//div[@class="ut"]/span[1]/text()')[0]
    #get user  info
    pattern = r"\d+\.?\d*"
    str_wb = selector.xpath('//span[@class="tc"]/text()')[0]
    guid = re.findall(pattern, str_wb, re.S | re.M)
    for value in guid:
        num_wb = int(value)
        break
    weibo_num = num_wb
    str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
    guid = re.findall(pattern, str_gz, re.M)
    following = int(guid[0])
    str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
    guid = re.findall(pattern, str_fs, re.M)
    followers = int(guid[0])
    print('current user all weibo num {}, following {}, followers {}'.format(weibo_num, following,
                                                                        followers))
    #get weibo info    
    print("get weibo info......")
    if selector.xpath('//input[@name="mp"]') is None:
            page_num = 1
    else:
            page_num = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
    pattern = r"\d+\.?\d*"
    print('--- all weibo page {}'.format(page_num))
    for page in range(1, page_num):
        url2 = 'http://weibo.cn/%s?filter=%s&page=%s' % (user_id, filter, page)
        selector2=get_selector(url2,cookie,headers)
        info = selector2.xpath("//div[@class='c']")
        print('---- current solving page {}'.format(page))

        if page % 10 == 0:
            print('[ATTEMPTING] rest for 5 minutes to cheat weibo site, avoid being banned.')
            #time.sleep(60*5)
            time.sleep(20)
        if len(info) > 3:
            for i in range(0, len(info) - 2):
                detail = info[i].xpath("@id")[0]
                weibo_detail_urls.append('http://weibo.cn/comment/{}?uid={}&rl=0'.
                                                         format(detail.split('_')[-1], user_id))

                weibo_scraped += 1
                str_t = info[i].xpath("div/span[@class='ctt']")
                weibos = str_t[0].xpath('string(.)')
                weibo_content.append(weibos)
                print(weibos)
                str_zan = info[i].xpath("div/a/text()")[-4]
                guid = re.findall(pattern, str_zan, re.M)
                num_zan = int(guid[0])
                num_zan_list.append(num_zan)

                forwarding = info[i].xpath("div/a/text()")[-3]
                guid = re.findall(pattern, forwarding, re.M)
                num_forwarding = int(guid[0])
                num_forwarding_list.append(num_forwarding)

                comment = info[i].xpath("div/a/text()")[-2]
                guid = re.findall(pattern, comment, re.M)
                num_comment = int(guid[0])
                num_comment_list.append(num_comment)
            print('共' + str(weibo_scraped) + '条微博')
    #get weibo comments
    print("get weibo comments......")
    weibo_comments_save_dir = './weibo_detail/'
    weibo_comments_save_path='./weibo_detail/{}.txt'.format(user_id)
    if not os.path.exists(weibo_comments_save_dir):
        os.makedirs(os.path.dirname(weibo_comments_save_dir))
    with open(weibo_comments_save_path, 'w+',encoding="utf8") as f:
        for i, url in enumerate(weibo_detail_urls):
            print('solving weibo detail from {}'.format(url))
            selector_detail=get_selector(url,cookie,headers)
            all_comment_pages = selector_detail.xpath('//*[@id="pagelist"]/form/div/input[1]/@value')
            print("all_comment_pages",all_comment_pages)
            if len(all_comment_pages)==0:
                print("len(all_comment_pages)==0")
                all_comment_pages=1#一页评论
            else:
                all_comment_pages=all_comment_pages[0]
            print('\n这是 {} 的微博：'.format(user_name))
            print('微博内容： {}'.format(weibo_content[i]))
            print('接下来是下面的评论：\n\n')

            # write weibo content
            f.writelines('E\n')
            f.writelines(weibo_content[i] + '\n')
            f.writelines('E\n')
            f.writelines('F\n')
            
            for page in range(1,int(all_comment_pages)+1,1):
                if page % 10 == 0:
                    print('rest for 10 second to cheat weibo site, avoid being banned.')
                    #time.sleep(60*5)
                    time.sleep(10)
                detail_comment_url = url + '&page=' + str(page)
                print("detail_comment_url",detail_comment_url)
                try:
                    # from every detail comment url we will got all comment
                    selector_comment=get_selector(detail_comment_url,cookie,headers=None)
                    comment_div_element = selector_comment.xpath('//div[starts-with(@id, "C_")]')
                    for child in comment_div_element:
                        single_comment_user_name = child.xpath('a[1]/text()')[0]
                        if child.xpath('span[1][count(*)=0]'):
                            single_comment_content = child.xpath('span[1][count(*)=0]/text()')[0]
                        else:
                            span_element = child.xpath('span[1]')[0]
                            at_user_name = span_element.xpath('a/text()')[0]
                            at_user_name = '$' + at_user_name.split('@')[-1] + '$'
                            single_comment_content = span_element.xpath('text()')
                            single_comment_content.insert(1, at_user_name)
                            single_comment_content = ' '.join(single_comment_content)
                                
                        full_single_comment = '<' + single_comment_user_name + '>' + ': ' + single_comment_content
                        print(full_single_comment)
                        f.writelines(full_single_comment + '\n')
                except etree.XMLSyntaxError as e:
                    print('-*20')
                    print('user id {} all done!'.format(user_id))
                    print('all weibo content and comments saved into {}'.format(weibo_comments_save_path))
            f.writelines('F\n')
    

def main():
    run_spyder()

if __name__ == "__main__":
    main()      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
