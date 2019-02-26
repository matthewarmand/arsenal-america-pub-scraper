# -*- coding: utf-8 -*-
import csv
import math
import re
import scrapy
import time

class ArsenalAmericaPubsSpider(scrapy.Spider):
    name = 'arsenal_america_pubs'
    allowed_domains = ['www.arsenal.com/usa/news/features/arsenal-bars']
    start_urls = ['https://www.arsenal.com/usa/news/features/arsenal-bars/']
    expected_article_date = '01 Jun 2017'

    def parse(self, response):
        mod_date = response.css('span.article-card-header__date::text').get()
        if mod_date != self.expected_article_date:
            print('Warning! Expected article date is ' + self.expected_article_date + ' but actual is ' + mod_date)
            print('Spider may be out of date')

        p_tags = response.css('p')
        pubs = []
        for p_tag in p_tags:
            pub = self.Pub(p_tag)
            if pub.valid:
                pubs.append(pub)
        self.process_pubs(pubs)
        return

    def process_pubs(self, pubs):
        field_names = ['name', 'branch_hq', 'address', 'phone']
        with open('pubs-' + str(math.ceil(time.time())) + '.csv', 'w', newline='') as csvfile:
            pub_writer = csv.DictWriter(csvfile, field_names)
            pub_writer.writeheader()
            for pub in pubs:
                pub_writer.writerow({'name': pub.name, 'branch_hq': pub.branch_hq, 'address': pub.address, 'phone': pub.phone})
        return

    class Pub:
        # Phone hacks:
        #   A-Z in regex needed because Doyle's Public House has PINT as their last four
        #   * after space in regex needed because a couple had no space between area code and number
        #   replace needed because Library Square has a &nbsp; instead of a space
        #   phone_index hack needed because Lahaina Coolers has an extra newline after phone number

        phone_pattern = re.compile('\([0-9]{3}\)\s*[0-9]{3}[-.][0-9A-Z]{4}')
        def __init__(self, p_tag):
            self.valid = True

            a_tag = p_tag.css('a')
            name = a_tag.css('::text').get()
            if name is not None and name.strip() != '':
                self.name = name
                self.link = a_tag.attrib['href']
            else:
                self.valid = False
                return

            all_text = p_tag.css('::text').getall()
            if len(all_text) < 4:
                self.valid = False
                return
   
            # TODO fix this... seems busted currently
            # TODO it may actually be more flexible to join all_text and use searches
            branch_hq = all_text[1].replace('&nbsp', '').strip()
            self.branch_hq = 'Branch' if branch_hq == '*' else 'Emerging' if branch_hq == '**' else 'No'
            print(branch_hq + ', ' + self.branch_hq)

            phone_index = -1
            phone = all_text[-1].replace('&nbsp', ' ').strip()
            if self.phone_pattern.match(phone):
                self.phone = phone
            else:
                phone_2 = all_text[-2].replace('&nbsp', ' ').strip()
                if self.phone_pattern.match(phone_2):
                    self.phone = phone_2
                    phone_index = -2
                else:
                    print('phone is not phone [' + phone + '] & [' + phone_2 + '] for name ' + name)
                    self.valid = False
                    return

            self.address = (all_text[phone_index - 2] + all_text[phone_index - 1]).replace('\n', ' ').strip()

