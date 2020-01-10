# -*- coding: utf-8 -*-
import scrapy


class AirbnbSpider(scrapy.Spider):
    name = 'airbnb'
    allowed_domains = ['www.airbnb.mx']
    start_urls = ['http://www.airbnb.mx/']

    def parse(self, response):
        pass
