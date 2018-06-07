本项目旨在从各大论坛、贴吧、微博平台爬取高质量闲聊对话语料论<br>
===

本项目旨在从网络上获取高质量的问答对，用以训练开放域聊天机器人，目前已经获取到数据包括:<br>
1、可可英语情景对话，质量极高的短对话<br>
2、微博及所有评论<br>
3、天涯问答板块及所有回复评论<br>
4、百度贴吧欢乐斗地主游戏问题反馈专区所有帖子<br>

主要特点
---
1、爬虫没有使用任何框架如scrpay,可灵活扩展<br>
2、支持页面内容解析，从帖子、回复、评论嵌套的页面以较高效的方式解析出问答对:主要体现在天涯页面爬取中<br>
3、对于由于网络原因而爬取失败的直接跳过，不影响后续爬取<br>
4、部分动态加载的数据通过抓包分析获取请求json,高效抓取数据<br>
5、对于微博数据，采用ip池和账号池、随机延时等策略尽量避免反爬机制<br>
6、对于微博数据，使用phantomJs+selenium获取登录cookie,避免手动抓取cookie<br>

详细使用说明见readme.pdf
如需以上各种数据，请联系：1174950106@qq.com
                           
  
