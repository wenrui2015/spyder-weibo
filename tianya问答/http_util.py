# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 11:01:36 2018

@author: ruiwen
"""

import requests
from lxml import etree
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