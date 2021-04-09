import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ChelseaItem
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
pattern = r'(\xa0)?'

class ChelseaSpider(scrapy.Spider):
	name = 'chelsea'
	start_urls = ['https://www.chelseagroton.com/Home/Why-Chelsea-Groton/News-You-Can-Use']
	page = 2
	def parse(self, response):
		articles = response.xpath('//div[@class="date_title"]')
		for article in articles:
			date = article.xpath('.//span/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[contains(text(),"Next")]').get()
		if next_page:
			yield FormRequest.from_response(response, formdata={
				"__EVENTTARGET": 'dnn$ctr692$DNNArticle_List$MyArticleList$MyPageNav$ctlPagingControl',"__EVENTARGUMENT":f'Page_{self.page}'}, callback=self.parse)
			self.page += 1

	def parse_post(self, response, date):
		title = response.xpath('(//h1)[2]/text()').get()
		content = response.xpath('//div[@id="dnn_ctr633_ModuleContent"]//text()[not (ancestor::script or ancestor::style or ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ChelseaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
