# -*- coding: utf-8 -*-
import csv
import math
import os
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
            print('Warning! Expected article date is ' +
                  self.expected_article_date + ' but actual is ' +
                  mod_date + '. Spider may be out of date. ' +
                  'Check for DOM structure changes')

        p_tags = response.css('p')
        pubs = []
        for p_tag in p_tags:
            pub = self.Pub(p_tag)
            if pub.valid:
                pubs.append(pub)

        if len(pubs) > 1999:
            print('Warning! Too many rows for Google Maps import')

        self.process_pubs(pubs)
        return

    def process_pubs(self, pubs):
        field_names = [
            'Name',
            'Link',
            'Branch Status',
            'Address',
            'Phone'
        ]

        file_name = 'pubs-' + str(math.ceil(time.time())) + '.csv'
        with open(
            file_name,
            'w',
            newline=''
        ) as csvfile:
            pub_writer = csv.DictWriter(csvfile, field_names)
            pub_writer.writeheader()
            for pub in pubs:
                pub_writer.writerow({
                    'Name': pub.name,
                    'Link': pub.link,
                    'Branch Status': pub.branch_hq,
                    'Address': pub.address,
                    'Phone': pub.phone
                })

        if os.path.getsize(file_name) >= 40000000:
            print(
                'Warning! File size may be too large for Google Maps import')

        return

    class Pub:
        phone_pattern = r'\([0-9]{3}\)\s*[0-9]{3}[-.][0-9A-Z]{4}'

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

            all_text = ''.join(p_tag.css('::text').getall()) \
                         .replace('\n', ' ') \
                         .replace('&nbsp', ' ').strip()

            if ':' in all_text:
                all_text = all_text.split(':')[1].strip()

            self.branch_hq = 'Emerging' if '**' in all_text else \
                             'Branch HQ' if '*' in all_text else \
                             'NA'

            phone = re.search(self.phone_pattern, all_text)
            if phone:
                self.phone = phone.group(0)
            else:
                self.valid = False
                return

            addr_start = all_text.find(self.name) + len(self.name)
            addr_end = all_text.find(self.phone)
            self.address = all_text[addr_start:addr_end].replace('*', '') \
                                                        .strip()
