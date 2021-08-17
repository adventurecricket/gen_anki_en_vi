#!/bin/env python3

""" wiki_VietNamese dictionary api """

from http import cookiejar

import requests
from bs4 import BeautifulSoup as soup


vi_types ={'Từ viết tắt','Tính từ','Yếu tố','Phó từ','Mạo từ','Trợ động từ','Phụ tố chu vi','Yếu tố quanh','Từ ghép','Liên từ kết hợp'
,'Danh từ tập họp','Liên từ','Từ rút gọn','Hệ từ','Đồng động từ','Mạo từ hạn định','Từ chỉ định','Tính từ chỉ định','Đại từ chỉ định'
,'Từ hạn định','Từ ghép sau','Động từ không ngôi','Tính từ bất định','Mạo từ bất định','Trung tố','Thán từ','Từ nghi vấn','Nội động từ'
,'Chữ cái','Từ ghép trung','Danh từ','Số từ','Trợ từ','Động tính từ','Mạo từ bộ phận','Đại từ nhân xưng','Địa danh','Tính từ sở hữu'
,'Yếu tố sau','Tính từ riêng','Danh từ riêng','Tiền tố','Giới từ','Từ ghép trước','Đại từ','Đại từ phản thân','Động từ phản thân'
,'Đại từ quan hệ','Liên từ phụ thuộc','Hậu tố','Ngoại động từ','Động từ'}


class WordNotFound(Exception):
    """ word not found in dictionary (404 status code) """
    pass


class BlockAll(cookiejar.CookiePolicy):
    """ policy to block cookies """
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Vi_Word(object):
    """ retrive word info from oxford dictionary website """
    entry_selector = '#entryContent > .entry'
    header_selector = '.top-container'

    title_selector = header_selector + ' .headword'
    
    soup_data = None
    
    @classmethod
    def get_url(cls, word):
        """ get url of word definition """
        baseurl = 'https://vi.wiktionary.org/wiki/{0}#Tiếng_anh'.format(word)
        return baseurl

    @classmethod
    def delete(cls, selector):
        """ remove tag with specified selector in cls.soup_data """
        try:
            for tag in cls.soup_data.select(selector):
                tag.decompose()
        except IndexError:
            pass

    @classmethod
    def get(cls, word):
        """ get html soup of word """
        req = requests.Session()
        req.cookies.set_policy(BlockAll())

        page_html = req.get(cls.get_url(word), timeout=5, headers={'User-agent': 'mother animal'})
        if page_html.status_code == 404:
            raise WordNotFound
        else:
            cls.soup_data = soup(page_html.content, 'html.parser')

        if cls.soup_data is not None:
            # remove some unnecessary tags to prevent false positive results
            cls.delete('[title="Oxford Collocations Dictionary"]')
            cls.delete('[title="British/American"]')  # edge case: 'phone'
            cls.delete('[title="Express Yourself"]')
            cls.delete('[title="Collocations"]')
            cls.delete('[title="Word Origin"]')
    
    @classmethod
    def definition_full(cls):
        """ return word definition + corresponding examples

        A word can have a one or many definitions
        Each definitions can have one, many or no examples

        """
        if cls.soup_data is None:
            return None

        info = []
        article = cls.soup_data.find(id = "Ti.E1.BA.BFng_Anh")

        namespaces = article.find_all_next('h3')
        try:
            for namespace in namespaces:
                definitions = []
            
                type = namespace.select('span.mw-headline')[0].text
                if type in vi_types:
                    ol = namespace.find_next("ol")
                    if ol != None:
                        lis = ol.find_all("li")

                        for li in lis:
                            definition = {}
                            li_texts = li.text.split("\n")
                            definition['description'] = li_texts[0]
                            definition['examples'] = li_texts[1:(len(li_texts))]

                            definitions.append(definition)
                    else:
                        dl = namespace.find_next("dl")
                        dds = dl.find_all("dd")
                        for dd in dds:
                            definition = {}
                            dd_texts = dd.text.split("\n")
                            definition['description'] = dd_texts[0]
                            definition['examples'] = dd_texts[1:(len(dd_texts))]

                            definitions.append(definition)

                    info.append({'namespace': type, 'definitions': definitions})
                elif type in 'Tham khảo':
                    break
        except IndexError:
            pass
        
        return info

        