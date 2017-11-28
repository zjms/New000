

from ..items import NewsItem

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
import json
import  scrapy
import re
from scrapy import Request
import time

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')

key_list=['气候','气象','降水','洪水','高温','积雪','气候变化','大风','冷空气','雷电','连阴雨','降雨','预报','灾害',
          '环境','大气','空气','污染','PM2.5','江西气象局','气象局','风速','气象台','气象灾害','气象条件','天气',
          '雾霾 ','雾','霾','冷','热','监测','泥石流','干旱','台风','霜冻','结冰','冰雹','泥石流','森林','预报','预警',
          '灾害风险','气候变化', '人工降雨','人工增雨','极端天气','AQI','PM10','厄尔尼诺','湿度','风向','拉尼娜',
          '大气自净能力', '小风日数','江西省气象部门','大气探测中心' ,'气象学会','灾害防御','气象科学','气候中心',
          '气象信息']
import jieba
import re
def Hit(text):
    count=0
    text= "".join(re.findall(u'[\u4e00-\u9fff]+',text))
    a=jieba.cut(text)
    text = list(set(a))
    for k in key_list:
        if k in text:
            count+=1
    if count>4:
        return True
    else:
        return False

#江西文明网
class NewsSpider(CrawlSpider):
    name = "jxwmw_spider"

    start_urls = ['http://www.jxwmw.cn/',
                  ]
    allowed_domains = ['jxwmw.cn']
    url_pattern = 'http://(\w+).jxwmw.cn/(\w+)/*/2017/(\d{2})/(\d{2})/(\d{9}).shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        title = sel.xpath('//div[@class="title"]/h1/text()').extract()

        pattern = re.match(self.url_pattern, str(response.url))
        source = 'jxnews.cn'

        date =sel.xpath('//div[@class="title"]/p/text()').extract()
        time = sel.xpath('//div[@class="title"]/p/text()').extract()
        url = response.url

        newsId = pattern.group(5)
        contents = ListCombiner(sel.xpath('//div[@id="text"]/p/text()').extract())
        comments = 0
        if Hit(contents):
            item = NewsItem()
            item['source'] = source
            item['time'] = time
            item['date'] = date
            item['contents'] = contents
            item['title'] = title
            item['url'] = url
            item['newsId'] = newsId
            item['comments'] = comments
            yield item
#网易
class NeteaseNewsSpider(CrawlSpider):
    name = "netease_news_spider"
    start_urls = ['http://news.163.com/']
    # Spider中间件会对Spider发出的request进行检查，只有满足allow_domain才会被允许发出
    allowed_domains = ['news.163.com']
    # http://news.163.com/17/0823/20/CSI5PH3Q000189FH.html
    url_pattern = r'(http://news\.163\.com)/(\d{2})/(\d{4})/\d+/(\w+)\.html'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'news.163.com'
        if sel.xpath('//div[@class="post_time_source"]/text()'):
            time_ = sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[0] + ' ' + sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[1]
        else:
            time_ = 'unknown'
        date = '20' + pattern.group(2) + '/' + pattern.group(3)[0:2] + '/' + pattern.group(3)[2:]
        newsId = pattern.group(4)
        url = response.url
        title = sel.xpath("//h1/text()").extract()[0]
        contents = ListCombiner(sel.xpath('//p/text()').extract()[2:-3])
        # comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{}'.format(newsId)
        comments = 0
        if Hit(contents):
            item = NewsItem()
            item['source'] = source
            item['date'] = date
            item['newsId'] = newsId
            item['url'] = url
            item['title'] = title
            item['contents'] = contents
            item['comments'] = comments
            item['time'] = time
            yield item

    #     yield Request(comment_url, self.parse_comment, meta={'source':source,
    #                                                          'date':date,
    #                                                          'newsId':newsId,
    #                                                          'url':url,
    #                                                          'title':title,
    #                                                          'contents':contents,
    #                                                          'time':time_
    #                                                          })
    # def parse_comment(self, response):
    #     result = json.loads(response.text)
    #     item = NewsItem()
    #     item['source'] = response.meta['source']
    #     item['date'] = response.meta['date']
    #     item['newsId'] = response.meta['newsId']
    #     item['url'] = response.meta['url']
    #     item['title'] = response.meta['title']
    #     item['contents'] = response.meta['contents']
    #     item['comments'] = result['cmtAgainst'] + result['cmtVote'] + result['rcount']
    #     item['time'] = response.meta['time']
    #     return item
#新浪
class SinaNewsSpider(CrawlSpider):
    name = "sina_news_spider"
    allowed_domains = ['news.sina.com.cn']
    start_urls = ['http://news.sina.com.cn']
    # http://finance.sina.com.cn/review/hgds/2017-08-25/doc-ifykkfas7684775.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/(\d{4}-\d{2}-\d{2})/doc-(\w+).shtml'
    # today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    # url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/(\w+)/doc-(.*)\.shtml'.format(today_date)
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern],deny=['20%',' ']), callback='parse_news', follow=True,)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath("//h1[@id='artibodyTitle']/text()"):
            contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
            if Hit(contents):
                title = sel.xpath("//h1[@id='artibodyTitle']/text()").extract()[0]
                pattern = re.match(self.url_pattern, str(response.url))
                source = pattern.group(1)
                date = pattern.group(2).replace('-','/')
                if sel.xpath('//span[@class="time-source"]/text()'):
                    time_ = sel.xpath('//span[@class="time-source"]/text()').extract_first().split()[0]
                else:
                    time_ = 'unknown'
                newsId = pattern.group(3)
                url = response.url
                contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
                comment_elements = sel.xpath("//meta[@name='sudameta']").xpath('@content').extract()[1]
                comment_channel = comment_elements.split(';')[0].split(':')[1]
                comment_id = comment_elements.split(';')[1].split(':')[1]
                comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={}&newsid={}'.format(comment_channel,comment_id)

                yield Request(comment_url, self.parse_comment, meta={'source':source,
                                                                 'date':date,
                                                                 'newsId':newsId,
                                                                 'url':url,
                                                                 'title':title,
                                                                 'contents':contents,
                                                                 'time':time_
                                                                })

    def parse_comment(self, response):
        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        item = NewsItem()
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        return item



#腾讯    修改ing   链接打开时出现403和302问题
# class TencentNewSpider(CrawlSpider):
#     name = 'tencent_news_spider'
#     allowed_domains = ['news.qq.com']
#     start_urls = ['http://news.qq.com']
#     #  http://news.qq.com/a/20170825/026956.htm
#     url_pattern = 'http://news.qq.com/a/2017(\d{4})/(\d{1,9}).htm'
#     # rules = [
#     #     Rule(LxmlLinkExtractor(allow=[url_pattern],deny=('class','original',)), callback='parse_news', follow=True,)]
#     rules = [
#         Rule(LxmlLinkExtractor(allow=[url_pattern],deny='http://news.qq.com/a/2017(\d{4})/(\d{1,9}).htm20%'),callback='parse_news',follow=True)
#
#     ]
#     def parse_news(self, response):
#         sel = Selector(response)
#         source = 'tencent.com'
#         # pattern = re.match(self.url_pattern, str(response.url))
#         # newsId = pattern.group(3)
#         newsId=0
#         url = response.url
#         time = 1001
#         if sel.xpath('//div[@class="qq_article"]/h1/text()'):
#             title = sel.xpath('//div[@class="qq_article"]/h1/text()').extract()[0]
#             contents = ListCombiner(sel.xpath('//div[@id="Cnt-Main-Article-QQ"]/p/text()').extract())
#             date = sel.xpath('//div[@class="a_Info"]/span[@class="a_time"]').extract()
#
#
#         elif sel.xpath('//div[@class="LEFT"]/h1/text()'):
#             title = sel.xpath('//div[@class="LEFT"]/h1/text()')
#             contents = ListCombiner(sel.xpath('//div[@class="content-article"]/p[@class="one-p"]/text()').extract())
#
#         else:
#             title=''
#             contents=''
#
#         if contents:
#             item = NewsItem()
#             item['source'] = source
#             item['time'] = time
#             item['date'] = 1000
#             item['contents'] = contents
#             item['title'] = title
#             item['url'] = url
#             item['newsId'] = newsId
#             item['comments'] = 0
#             yield item
class TencentNewsSpider(CrawlSpider):
    name = 'tencent_news_spider'
    allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com']
    # http://news.qq.com/a/20170825/026956.htm
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        # if sel.xpath('//div[@class="qq_article"]/div[@class="hd"]/h1/text()'):
        #     title = sel.xpath('//div[@class="qq_article"]/div[@class="hd"]/h1/text()').extract()[0]
        if sel.xpath('//div[@class="hd"]/h1/text()'):
            title = sel.xpath('//div[@class="hd"]/h1/text()').extract()[0]
        # elif sel.xpath('//div[@id="ArticleTit"]/text()'):
        #     title = sel.xpath('//div[@id="ArticleTit"]/text()').extract()[0]
        elif sel.xpath('//div[@class="LEFT"]/h1/text()'):
            title = sel.xpath('//div[@class="LEFT"]/h1/text()').extract()
        else:
            title = 'unknown'
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:]
        newsId = pattern.group(3)
        url = response.url

        if sel.xpath('//div[@class="a-src-time"]/a/text()'):
            time_ = ListCombiner(sel.xpath('//div[@class="a-src-time"]/a/text()').extract()[-1])
        elif sel.xpath('//span[@class="a_time"]/text()'):
            time_ = sel.xpath('//span[@class="a_time"]/text()').extract()
        elif sel.xpath('//span[@class="article-time"]/text()'):
            time_ = sel.xpath('//span[@class="article-time"]/text()').extract()
        else:
            time_ = 'unknown'

        if sel.xpath('//p/text()'):
            contents = ListCombiner(sel.xpath('//p/text()').extract())
        elif sel.xpath('//div[@id="infoTxt"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@id="infoTxt"]/p/text()').extract())
        else:
            contents = 'unknown'
        comments=0
        if Hit(contents):
            item = NewsItem()
            item['source'] = source
            item['time'] = time_
            item['date'] = date
            item['contents'] = contents
            item['title'] = title
            item['url'] = url
            item['newsId'] = newsId
            item['comments'] = comments
            yield item

#wirted by myself 搜狐ｏｋ
class SohuNewsSpider(CrawlSpider):
    name = "sohu_news_spider"
    start_urls = ['http://news.sohu.com/',
                  'http://travel.sohu.com/',
                  'http://it.sohu.com/',
                  'http://sports.sohu.com/',
                  'http://yule.sohu.com/',
                  'http://cul.sohu.com/',
                  'http://society.sohu.com/'
                  ]


    allowed_domains = ['sohu.com']
    # http://www.sohu.com/a/203596129_100001551?_f=index_chan08news_5
    # url_pattern = r'http://www.sohu.com/a/(\d{9})\_(\d{6, 9})\?\_f=index\_chan08(\w+)\_(\d{1,4})'
    url_pattern = r'www.sohu.com/a/(\d{6,9})\_(\d{6,9})'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        title = sel.xpath('//div[@class="text-title"]/h1/text()').extract()[0].split()
        # pattern = re.match(self.url_pattern, str(response.url))
        source = 'news.sohu.com'

        date = sel.xpath('//div[@class="article-info"]/span/text()').extract()[0][0:10]
        time = sel.xpath('//div[@class="article-info"]/span/text()').extract()[0][10:-1]
        url = response.url
        newsId = re.findall(r'www.sohu.com/a/(.*?)?_',url, re.S)[0]
        contents = ListCombiner(sel.xpath('//article[@class="article"]/p/text()').extract())
        # comments= sel.xpath('//div[@class="right"]/span'

        comments = 0
        item = NewsItem()
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = comments
        yield item

# 新华网

class XinhuaNewsSpider(CrawlSpider):
    name = "xinhua_news_spider"
    start_urls = ['http://www.xinhuanet.com/']


    allowed_domains = ['xinhuanet.com']
    # http://news.xinhuanet.com/fortune/2017-11/10/c_1121937779.htm
    url_pattern = r'http://news.xinhuanet.com/([a-z]+)/*/2017-(\d{1,2})/(\d{1,2})/c\_(\d{6,10}).htm'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)

        if  sel.xpath('//div[@id="p-detail"]/p/text()').extract():
            title = sel.xpath('//div[@class="h-title"]/text()').extract()
            pattern = re.match(self.url_pattern, str(response.url))
            source = 'xinhuanet.com'
            date = sel.xpath('//div[@class="h-info"]/span/text()').extract()[0][:11]
            time = sel.xpath('//div[@class="h-info"]/span/text()').extract()[0][11:]
            url = response.url
            newsId =pattern.group(4)
            # newsId = re.findall(r'c_(.*?).htm',url, re.S)[0]
            contents = ListCombiner(sel.xpath('//div[@id="p-detail"]/p/text()').extract()).split()
            # comments= sel.xpath('//div[@class="right"]/span'

            comments = 0
            item = NewsItem()
            item['source'] = source
            item['time'] = time
            item['date'] = date
            item['contents'] = contents
            item['title'] = title
            item['url'] = url
            item['newsId'] = newsId
            item['comments'] = comments
            yield item
#凤凰网  successful
class IfengNewsSpider(CrawlSpider):
    name = "ifeng_news_spider"
    allowed_domains = ['news.ifeng.com']
    start_urls = ['http://news.ifeng.com']

    # http: // book.ifeng.com / a / 20171115 / 108116_0.shtml
    #http: // fo.ifeng.com / a / 20171116 / 44763303_0.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.ifeng\.com)/a/(\d{8})/(\d+)\_0\.shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        date = pattern.group(2)[0:4] + '/' + pattern.group(2)[4:6] + '/' + pattern.group(2)[6:]
        if sel.xpath('//p[@class="p_time"]/span/text()'):
            time = sel.xpath('//p[@class="p_time"]/span/text()').extract()
        elif sel.xpath('//div[@class="yc_tit"]/p/span/text()'):
            time = sel.xpath('//div[@class="yc_tit"]/p/span/text()').extract()[0]
        elif sel.xpath('//div[@class="zuo_word fl"]/p/text()'):
            time = sel.xpath('//div[@class="zuo_word fl"]/p/text()').extract()[-1]
        else:
            time = "unknown"

        if sel.xpath('//h1[@id="artical_topic"]/text()'):
            title = sel.xpath('//h1[@id="artical_topic"]/text()').extract()
        elif sel.xpath('//div[@class="yc_tit"]/h1/text()'):
            title = sel.xpath('//div[@class="yc_tit"]/h1/text()').extract()
        elif sel.xpath('//div[@class="zhs_mid_02"]/h1/text()'):
            title = sel.xpath('//div[@class="zhs_mid_02"]/h1/text()').extract()
        else:
            title = "unknown"
        source = pattern.group(1)
        newsId = pattern.group(3)
        url = response.url
        if sel.xpath('//div[@id="main_content"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@id="main_content"]/p/text()').extract())
        elif sel.xpath('//div[@class="yc_con_txt"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="yc_con_txt"]/p/text()').extract())
        elif sel.xpath('//div[@class="yaow"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="yaow"]/p/text()').extract())
        else:
            contents = "unknown"
        comments = 0

        item = NewsItem()
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item

#央视新闻
class CctvNewsSpider(CrawlSpider):
    name = "cctv_news_spider"
    allowed_domains = ['news.cctv.com']
    start_urls = ['http://news.cctv.com']
    #http: // jiankang.cctv.com / 2017 / 11 / 17 / ARTIsSTfqrpnb6Nj2UZydIXo171117.shtml
    #http: // tv.cctv.com / 2017 / 11 / 19 / VIDELf9eHnwFxj0h0p77qwNV171119.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.cctv\.com)/(\d{4})/(\d{2})/(\d{2})/(\w+)\.shtml'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/'+ pattern.group(4)
        newsId = pattern.group(5)
        if sel.xpath('//span[@class="info"]/i/text()'):
            time = sel.xpath('//span[@class="info"]/i/text()').extract()
        elif sel.xpath('//span[@class="time"]/text()'):
            time = sel.xpath('//span[@class="time"]/text()').extract()
        else:
            time = "unknown"
        if sel.xpath('//div[@class="cnt_bd"]/h1/text()'):
            title = sel.xpath('//div[@class="cnt_bd"]/h1/text()').extract()
        elif sel.xpath('//h3[@class="title"]/text()'):
            title = sel.xpath('//h3[@class="title"]/text()').extract()
        else:
            title = "unknown"
        url = response.url
        contents = ListCombiner(sel.xpath('//div[@class="cnt_bd"]/p/text()').extract())
        comments = 0

        item = NewsItem()
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item
#江南都市报
class JndsbNewsSpider(CrawlSpider):
    name = "jndsb_news_spider"
    allowed_domains = ['jndsb.jxnews.com.cn']
    start_urls = ['http://jndsb.jxnews.com.cn']
    #http://jndsb.jxnews.com.cn/system/2017/06/17/016210714.shtml
    url_pattern = r'(http://jndsb\.jxnews\.com\.cn)/system/(\d{4})/(\d{2})/(\d{2})/(\d+)\.shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2) + '/' + pattern.group(3) + '/' + pattern.group(4)
        if sel.xpath('//span[@id="pubtime_baidu"]/text()'):
            time = sel.xpath('//span[@id="pubtime_baidu"]/text()').extract_first().split()
        else:
            time = "unknown"
        title = sel.xpath('//div[@class="BiaoTi"]/text()').extract()
        url = response.url
        newsId = pattern.group(5)
        contents = ListCombiner(sel.xpath('//div[@class="Content"]/p/text()').extract())
        comments = 0

        item = NewsItem()
        item['source'] = source
        item['title'] = title
        item['date'] = date
        item['time'] = time
        item['newsId'] = newsId
        item['url'] = url
        item['contents'] = contents
        item['comments'] = comments
        yield item

#中国新闻网     ok
class NewsSpider(CrawlSpider):
    name = "chinanews_spider"
    start_urls = ['http://www.chinanews.com/']
    allowed_domains = ['chinanews.com']
    url_pattern = 'www.chinanews.com/(\w+)/2017/(\d{2})-(\d{2})/(\d{4,9}).shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0].split()
        # pattern = re.match(self.url_pattern, str(response.url))
        source = 'chinanews.com'
        date =sel.xpath('//div[@class="left-t"]/text()').extract()[0].split(' ')[1]
        time = sel.xpath('//div[@class="left-t"]/text()').extract()[0].split(' ')[2][:5]
        url = response.url
        newsId = url[-13:-6]
        contents = ListCombiner(sel.xpath('//div[@class="left_zw"]/p/text()').extract())


        comments = 0
        item = NewsItem()
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = comments
        yield item
#中国气象网
class NewsSpider(CrawlSpider):
    name = "weather_spider"
    start_urls = ['http://www.weather.com.cn/'
                 ]
    allowed_domains = ['weather.com.cn'
                       ]
    url_pattern = 'http://news.weather.com.cn/2017/(\d{2})/(\d{1,9}).shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath('//div[@class="xyn-cont"]/h2/text()').extract():
            title = sel.xpath('//div[@class="xyn-cont"]/h2/text()').extract()
            # pattern = re.match(self.url_pattern, str(response.url))
            source = 'weather.com'

            date1 =sel.xpath('//div[@class="xyn-cont-time"]').extract()[0]
            date = re.findall('2017-(.*?):(\d{2})','date1',re.S)
            time = date
            url = response.url

            newsId = str(url)[-13:-6]
            contents = ListCombiner(sel.xpath('//div[@class="xyn-text"]/p/text()').extract())
            item = NewsItem()
            item['source'] = source
            item['time'] = time
            item['date'] = date
            item['contents'] = contents
            item['title'] = title
            item['url'] = url
            item['newsId'] = newsId
            item['comments'] = 0
            yield item
#信息日报  ok
class NewsSpider(CrawlSpider):
    name = "jxnews_spider"

    start_urls = ['http://www.jxnews.com.cn/xxrb/',
                  'http://www.jxnews.com.cn/xxrb/jryw/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/jxzd/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/cjxw/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/gdxw/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/xwdc/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/xwcs/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/tyxw/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/paotui/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/ygxf/index.shtml',
                  'http://www.jxnews.com.cn/xxrb/whzk/index.shtml'
                  ]


    allowed_domains = ['www.jxnews.com.cn']
    url_pattern = 'http://www.jxnews.com.cn/xxrb/system/2017/(\d{2})/(\d{2})/(\d{9}).shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        title = sel.xpath('//div[@class="article"]/h2/text()').extract()

        pattern = re.match(self.url_pattern, str(response.url))
        source = 'jxnews.com'

        date = sel.xpath('//p[@class="time"]/text()').extract()[0].split()[0]
        time = sel.xpath('//p[@class="time"]/text()').extract()[0].split()[0]
        url = response.url

        newsId = pattern.group(3)
        contents = ListCombiner(sel.xpath('//div[@class="scrap"]/p/text()').extract())


        comments = 0
        item = NewsItem()
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = comments
        yield item


#大江网
class NewsSpider(CrawlSpider):
    name = "jxcn_news_spider"
    allowed_domains = ['jxcn.cn','jxnews.com.cn']
    start_urls = ['http://www.jxcn.cn/']
    # http: // ml.jxcn.cn / system / 2017 / 11 / 02 / 016526588.shtml
    #http: // jt.jxcn.cn / system / 2013 / 11 / 13 / 012794201.shtml
    url_pattern = 'http://(.*?)/(2017)/(\d{2})/(\d{2})/(\d+).shtml'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'jxcn.cn'
        url = response.url
        newsId = pattern.group(5)
        date = pattern.group(2) + '/' + pattern.group(3) + '/' + pattern.group(4)
        if sel.xpath('//span[@id="pubtime_baidu"]/text()'):
            time = ListCombiner(sel.xpath('//span[@id="pubtime_baidu"]/text()').extract())
        elif sel.xpath('//span[@class="left"]/text()'):
            time = sel.xpath('//span[@class="left"]/text()').extract()[-1]
        else:
            time = "unknown"

        if sel.xpath('//div[@class="biaoti1"]/h1/text()'):
            title = sel.xpath('//div[@class="biaoti1"]/h1/text()').extract()
        elif sel.xpath('//div[@class="title"]/text()'):
            title = sel.xpath('//div[@class="title"]/text()').extract()
        elif sel.xpath('//div[@class="BiaoTi"]/text()'):
            title = sel.xpath('//div[@class="BiaoTi"]/text()').extract()
        elif sel.xpath('//div[@class="cont_adtop"]/h1/text()'):
            title = sel.xpath('//div[@class="cont_adtop"]/h1/text()').extract()
        else:
            title = 'unknown'

        if sel.xpath('//div[@class="Content"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="Content"]/p/text()').extract())
        elif sel.xpath('//div[@class="font1"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="font1"]/p/text()').extract())
        elif sel.xpath('//div[@class="text_w650 p14"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="text_w650 p14"]/p/text()').extract())
        elif sel.xpath('//font[@id="Zoom"]/p/text()'):
            contents = ListCombiner(sel.xpath('//font[@id="Zoom"]/p/text()').extract())
        elif sel.xpath('//font[@id="Zoom"]/div/p/text()'):
            contents = ListCombiner(sel.xpath('//font[@id="Zoom"]/div/p/text()').extract())
        else:
            contents = "unknown"
        item = NewsItem()
        item['source'] = source
        item['time'] = time
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['comments'] = 0
        yield item
#人民网
class NewsSpider(CrawlSpider):
    name = "people_news_spider"

    start_urls = ['http://www.people.com.cn/',
                  'http://news.people.com.cn/',
                  'http://politics.people.com.cn/',
                  'http://world.people.com.cn/',
                  'http://finance.people.com.cn/',
                  'http://opinion.people.com.cn/',
                  'http://scitech.people.com.cn/',
                  'http://health.people.com.cn/',
                  'http://edu.people.com.cn/',
                  'http://legal.people.com.cn/',
                  'http://culture.people.com.cn/'
              ]
    allowed_domains = ['people.com.cn']
    # http://energy.people.com.cn/n1/2017/1114/c71661-29644102.html
    url_pattern = 'http://([a-z]+).people.com.cn/n1/2017/(\d{4})/c(\d{4})-(\d{6,10}).html'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]
    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath('//div[@class="box_con"]/p/text()').extract():
            title = sel.xpath('//div[@class="clearfix w1000_320 text_title"]/h1/text()').extract()
            # pattern = re.match(self.url_pattern, str(response.url))
            source = 'people.com'
            date = sel.xpath('//div[@class="fl"]/text()').extract()
            time = sel.xpath('//div[@class="fl"]/text()').extract()
            url = response.url
            newsId = re.findall(r'-(.*?).html',url, re.S)
            contents = ListCombiner(sel.xpath('//div[@class="box_con"]/p/text()').extract())
            # comments= sel.xpath('//div[@class="right"]/span'
            comments = 0
            if Hit(contents):
                item = NewsItem()
                item['source'] = source
                item['time'] = time
                item['date'] = date
                item['contents'] = contents
                item['title'] = title
                item['url'] = url
                item['newsId'] = newsId
                item['comments'] = comments
                yield item

#江西晨报  有问题  页面
class JxcbwNewsSpider(CrawlSpider):
    name = "jxcbw_news_spider"
    allowed_domains = ['jxcbw.cn']
    url_pattern = r'NewsInfo.aspx?(NewsID=\d{3,8}&NewsType=LE\d{1,7})'
    start_urls = ['http://www.jxcbw.cn/']
    #http://www.jxcbw.cn/mainpages/NewsInfo.aspx?NewsID=69366&NewsType=LE123
    #http://www.jxcbw.cn/mainpages/NewsInfo.aspx?NewsID=70152&NewsType=LE107
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news',follow=True)
         ]
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'www.jxcbw.cn'
        time = sel.xpath('//span[@class="time fl"]/text()').extract()
        date = time[0]
        title = sel.xpath('//h2[@class="title-class2"]/text()').extract()
        newsId = pattern.group(1)
        url = response.url
        contents=''
        content_url = 'http://www.jxcbw.cn/mainpages/'+ url
        yield Request(content_url, self.parse_content, meta={'source': source,
                                                             'date': date,
                                                             'newsId': newsId,
                                                             'url': url,
                                                             'title': title,
                                                             'contents': contents,
                                                             'time': time
                                                             })

    def parse_content(self, response):
        sen = Selector(response)

        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        if sen.xpath('//div[@id="content"]/div/text()'):
            contents = ListCombiner(sen.xpath('//div[@id="content"]/div/text()').extract())
        else:
            contents = "unknown"
        item = NewsItem()
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = contents
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        return item


#新气象  successful
class ZgqxbNewsSpider(CrawlSpider):
    name = "zgqxb_news_spider"
    allowed_domains = ['zgqxb.com.cn']
    start_urls = ['http://www.zgqxb.cn']
    # http: // www.zgqxb.com.cn / pressman / bjdp / 201711 / t20171102_66412.htm
    # http: // www.zgqxb.com.cn / kjzg / kejidt / 201711 / t20171121_66600.htm
    url_pattern = r'(http://www\.zgqxb\.com\.cn)/.*/\d{6}/t(\d+)_(\d+).htm'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] +'/' + date[6:]
        newsId = pattern.group(3)
        #时间
        if sel.xpath('//span[@class ="l01 gray"]/text()'):
            time = sel.xpath('//span[@class ="l01 gray"]/text()').extract()[-1]
        else:
            time = "unknown"
        #标题
        if sel.xpath('//strong/b/text()'):
            title = ListCombiner(sel.xpath('//strong/b/text()').extract())
        else:
            title = "unknown"
        url = response.url
        #内容
        if sel.xpath('//div[@class="TRS_Editor"]/p/text()'):
            contents = ListCombiner(sel.xpath('//div[@class="TRS_Editor"]/p/text()').extract())
        elif sel.xpath('//font[@class="font_txt_zw"]/p/text()'):
            contents = ListCombiner(sel.xpath('//font[@class="font_txt_zw"]/p/text()').extract())
        elif sel.xpath('//font[@class="font_txt_zw"]/text()'):
            contents = ListCombiner(sel.xpath('//font[@class="font_txt_zw"]/text()').extract())
        else:
            contents = 'unknown'
        comments = 0
        if Hit(contents):
            item = NewsItem()
            item['source'] = source
            item['title'] = title
            item['date'] = date
            item['time'] = time
            item['newsId'] = newsId
            item['url'] = url
            item['contents'] = contents
            item['comments'] = comments
            yield item


#新民网   successful
class XinminNewsSpider(CrawlSpider):
    name = "xinmin_news_spider"
    allowed_domains = ['xinmin.cn']
    start_urls = ['http://www.xinmin.cn']
    #http://edu.xinmin.cn/tt/2017/11/15/31334031.html
    #http://newsxmwb.xinmin.cn/world/2017/11/21/31335695.html
    url_pattern = r'(http://.*\.xinmin\.cn)/.*/2017/(\d{2})/(\d{2})/(\d+).html'
    rules = [
            Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
        ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = '2017' + '/' + pattern.group(2) + '/' + pattern.group(3)
        newsId = pattern.group(4)
        contents = ListCombiner(sel.xpath('//div[@class="a_p"]/p/text()').extract())
        if Hit(contents):
            if sel.xpath('//div[@class="info"]/span/text()'):
                time = sel.xpath('//div[@class="info"]/span/text()').extract()[-1]
            elif sel.xpath('//span[@class="page_time"]/text()'):
                time = sel.xpath('//span[@class="page_time"]/text()').extract()
            else:
                time = "unknown"
            if sel.xpath('//h1[@class="article_title"]/text()'):
                title = sel.xpath('//h1[@class="article_title"]/text()').extract()
            elif sel.xpath('//h3[@class="content_title"]/text()'):
                title = sel.xpath('//h3[@class="content_title"]/text()').extract()
            else:
                title = "unknown"
            url = response.url
            contents = ListCombiner(sel.xpath('//div[@class="a_p"]/p/text()').extract())
            comments = 0
            if Hit(contents):

                item = NewsItem()
                item['source'] = source
                item['title'] = title
                item['date'] = date
                item['time'] = time
                item['newsId'] = newsId
                item['url'] = url
                item['contents'] = contents
                item['comments'] = comments
                yield item


