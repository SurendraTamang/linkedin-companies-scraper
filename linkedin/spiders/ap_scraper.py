# -*- coding: utf-8 -*-
import os
import csv
from pathlib import Path
import scrapy
from scrapy import signals
from scrapy_selenium import SeleniumRequest


class ApScraperSpider(scrapy.Spider):
    name = 'ap_scraper'

    def __init__(self):
        self.unavailable = []
        self.driver = None

        csv_path = os.path.join(Path(__file__).resolve().parents[2], 'links.csv')
        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
            self.name_link = [tuple(row) for row in reader]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ApScraperSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.linkedin.com/login?fromSignIn=true',
            wait_time=3,
            callback=self.parse
        )

    def parse(self, response):
        self.driver = response.meta['driver']

        email_input = self.driver.find_element_by_id('username')
        email_input.send_keys('<your_linkedin_email>')

        password_input = self.driver.find_element_by_id('password')
        password_input.send_keys('<your_linkedin_password>')

        sign_in = self.driver.find_element_by_class_name('btn__primary--large')
        sign_in.click()

        for no, item in enumerate(self.name_link):
            company_name = item[0]
            link = item[1]

            if not link:
                link = company_name.lower().replace(' ', '-')
                link = f"https://www.linkedin.com/company/{link}"

            yield SeleniumRequest(
                url=f'{link}/about',
                wait_time=5,
                callback=self.parse_about,
                meta={
                    'company_name': company_name,
                    'link': link
                }
            )

    def is_unavailable(self, response):
        result = response.xpath('normalize-space(//h1[@class="artdeco-empty-state__headline artdeco-empty-state__headline--sad-browser artdeco-empty-state__headline--3"]/text())').get()
        if result == "Oops!":
            return True

        return False

    def parse_about(self, response):
        company_name = response.request.meta['company_name']
        link = response.request.meta['link']
        website = ""
        industry = ""
        company_size = ""

        if self.is_unavailable(response):
            self.unavailable.append([company_name, link])
            return

        for item in response.xpath('//dt[contains(@class,"org-page-details__definition-term")]'):
            key = item.xpath('normalize-space(.//text())').get()
            if key == "Website":
                website = item.xpath('.//following-sibling::dd[1]/a/@href').get()
            elif key == "Industry":
                industry = item.xpath('normalize-space(.//following-sibling::dd[1]/text())').get()
            elif key == "Company size":
                company_size = item.xpath('normalize-space(.//following-sibling::dd[1]/text())').get()

        absolute_url = f'{link}/people'

        yield SeleniumRequest(
            url=absolute_url,
            wait_time=5,
            callback=self.parse_people,
            meta={
                'company_name': company_name,
                'link': link,
                'website': website,
                'industry': industry,
                'company_size': company_size
            }
        )

    def parse_people(self, response):
        company_name = response.request.meta['company_name']
        link = response.request.meta['link']
        website = response.request.meta['website']
        industry = response.request.meta['industry']
        company_size = response.request.meta['company_size']
        peoples = []

        for people in response.xpath('//div[@class="org-people-profile-card__profile-info"]'):
            name = people.xpath('normalize-space(.//descendant::a[2]/div/text())').get()
            title = people.xpath('normalize-space(.//descendant::div[@class="lt-line-clamp lt-line-clamp--multi-line ember-view"]/text())').get()
            linkedin_url = people.xpath('.//descendant::a[2]/@href').get()
            linkedin_url = f'https://www.linkedin.com{linkedin_url}'

            peoples.append({
                'name': name,
                'title': title,
                'linkedin_url': linkedin_url
            })

        yield {
            'company_name': company_name,
            'link': link,
            'website': website,
            'industry': industry,
            'company_size': company_size,
            'peoples': peoples
        }

    def spider_closed(self, spider):
        with open('unavailable.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.unavailable)

        self.driver.close()
        spider.logger.info('Spider closed: %s', spider.name)
