import scrapy
import json
from ..items import ScrapymarkstatsItem
from scrapy.loader import ItemLoader


# from scrapyfbref.items import ScrapyfbrefItem #for shell running

class MSPSpider(scrapy.Spider):
    name = 'laligams'
    #allowed_domains = ['fbref.com']
    start_urls = ["https://markstats.club/laliga-players-22-23/"]

    headers={
                "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",

    "Referer": "https://markstats.club/laliga-players-22-23/",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    }
    leagues=["es La Liga","eng Premier League","it Serie A ","de Bundesliga","fr Ligue 1"]
    urltableid=['1062','1060','1064','1068','1066']
    count=0
    def parse(self,response):
      for tableid in self.urltableid:
        url = 'https://markstats.club/wp-admin/admin-ajax.php?action=wp_ajax_ninja_tables_public_action&table_id='+tableid+'&target_action=get-all-data&default_sorting=old_first&ninja_table_public_nonce=a94896a9ec'
        yield scrapy.Request(url,callback=self.parse_api,headers=self.headers,cb_kwargs=dict(i=self.count))
        self.count=self.count+1
    def parse_api(self, response,i):
        resjson=json.loads(response.body)
        item=ScrapymarkstatsItem()
        self.count=self.count+1
        for rows in resjson:
            values = rows['value']
            item["player"] = values["player"]
            item["team"] = ' ' + values["team"]
            item["league"] = self.leagues[i]
            item["xthreat"] = values["xthreat"]
            item["noncrossxt"] = values["noncrossxt"]
            item["fieldsgainedpass"] = values["progressionpass"]
            item["fieldsgainedcarry"] = values["progressioncarry"]
            item["penboxcarries"] = values["penboxcarries"]
            item["progressionreceived"] = values["progressionreceived"]

        yield item

