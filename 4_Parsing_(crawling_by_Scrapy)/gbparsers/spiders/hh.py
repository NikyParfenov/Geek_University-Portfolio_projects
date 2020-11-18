"""
Parser of hh.ru using the next structure:
1. Remote jobs
1.1. Title of vacancy
1.2. Salary
1.3. Vacancy description
1.4. Key skills
1.5. Author of a vacancy (url)
2. Authors of parsed remote vacancies:
2.1. Company name
2.2. Web-site (url)
2.3. Field of company work
2.4. Company description
3. In addition, parse all vacancies of that authors using structure in 1.
"""
import scrapy
from ..loaders import HeadHunterJobsLoader, HeadHunterCompaniesLoader


class HeadHunterSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['spb.hh.ru']
    start_urls = ['https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'vacancies': '//div[@class="vacancy-serp"]//a[contains(@class, "HH-LinkModifier")]/@href',
        'pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "HH-Pager-Controls-Next")]/@href',
        'company': '//div[@class="vacancy-company-name-wrapper"]/a/@href',
        'company_vacancies': '//div[@class="employer-sidebar-content"]/div[@class="employer-sidebar-block"]/a/@href',
    }

    # parsing basic page with remote vacancies
    def parse(self, response, **kwargs):
        # follow to a next page
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)
        # follow to a vacancy page
        for url in response.xpath(self.xpath['vacancies']):
            yield response.follow(url, callback=self.vacancy_parse)

    # parsing vacancies
    def vacancy_parse(self, response, **kwargs):
        loader = HeadHunterJobsLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="vacancy-title"]//h1/text()')
        loader.add_xpath('salary', '//div[@class="vacancy-title"]//p[@class="vacancy-salary"]//text()')
        loader.add_xpath('description', '//div[@class="vacancy-section"]/div[@class="g-user-content"]//text()')
        loader.add_xpath('skills', '//div[@class="bloko-tag-list"]/div//span/text()')
        loader.add_xpath('owner_url', self.xpath['company'])
        yield loader.load_item()

        # follow to a vacancy of a company
        for url in response.xpath(self.xpath['company']):
            yield response.follow(url, callback=self.company_parse)

    # parse a company page
    def company_parse(self, response, **kwargs):
        loader = HeadHunterCompaniesLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="employer-sidebar-header"]//span//text()')
        loader.add_xpath('company_url', '//div[@class="employer-sidebar-content"]/a/@href')
        loader.add_xpath('field_of_work', '//div[@class="employer-sidebar-block"]/p/text()')
        loader.add_xpath('description', '//div[@class="company-description"]/div[@class="g-user-content"]//text()')
        yield loader.load_item()

        # follow to an company's vacancies
        for url in response.xpath(self.xpath['company_vacancies']):
            yield response.follow(url, callback=self.parse)
