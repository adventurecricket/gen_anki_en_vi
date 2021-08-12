#!/bin/env python3

""" wiki_VietNamese dictionary api """

from http import cookiejar

import requests
from bs4 import BeautifulSoup as soup

import vi_word_type as vi_type

class WordNotFound(Exception):
    """ word not found in dictionary (404 status code) """
    pass


class BlockAll(cookiejar.CookiePolicy):
    """ policy to block cookies """
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Word(object):
    """ retrive word info from oxford dictionary website """
    entry_selector = '#entryContent > .entry'
    header_selector = '.top-container'

    title_selector = header_selector + ' .headword'
    wordform_selector = header_selector + ' .pos'
    property_global_selector = header_selector + ' .grammar'

    br_pronounce_selector = '[geo=br] .phon'
    am_pronounce_selector = '[geo=n_am] .phon'
    br_pronounce_audio_selector = '[geo=br] [data-src-ogg]'
    am_pronounce_audio_selector = '[geo=n_am] [data-src-ogg]'

    definition_body_mul_selector = '.senses_multiple'
    namespaces_selector = '.senses_multiple > .shcut-g'
    examples_selector = '.senses_multiple .sense > .examples .x'
    definitions_selector = '.senses_multiple .sense > .def'

    extra_examples_selector = '.res-g [title="Extra examples"] .x-gs .x'
    phrasal_verbs_selector = '.phrasal_verb_links a'
    idioms_selector = '.idioms > .idm-g'

    other_results_selector = '#rightcolumn #relatedentries'

    soup_data = None

    # Add
    remark_selector = header_selector + ' .labels'
    extra_info_selector = header_selector + ' .un'

    definition_body_sgl_selector = '.sense_single'
    example_selector = '.sense_single .sense > .examples .x'
    definition_selector = '.sense_single .sense > .def'

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
    def name(cls):
        """ get word name """
        if cls.soup_data is None:
            return None
        return cls.soup_data.select(cls.title_selector)[0].text

    @classmethod
    def id(cls):
        """ get id of a word. if a word has definitions in 2 seperate pages
        (multiple wordform) it will return 'word_1' and 'word_2' depend on
        which page it's on """
        if cls.soup_data is None:
            return None
        return cls.soup_data.select(cls.entry_selector)[0].attrs['id']
    
    @classmethod
    def _parse_definition(cls, parent_tag):
        """ return word definition + corresponding examples

        A word can have a single (None) or multiple namespaces
        Each namespace can have one or many definitions
        Each definitions can have one, many or no examples

        Some words can have specific property
        (transitive/intransitive/countable/uncountable/singular/plural...)
        A verb can have phrasal verbs
        """
        if cls.soup_data is None:
            return None

        definition = {}

        try:  # property (countable, transitive, plural,...)
            definition['property'] = parent_tag.select('.grammar')[0].text
        except IndexError:
            pass

        try:  # label: (old-fashioned), (informal), (saying)...
            definition['label'] = parent_tag.select('.labels')[0].text
        except IndexError:
            pass

        try:  # refer to something (of people, of thing,...)
            definition['refer'] = parent_tag.select('.dis-g')[0].text
        except IndexError:
            pass

        definition['references'] = cls.get_references(parent_tag)
        if not definition['references']:
            definition.pop('references', None)

        try:  # sometimes, it just refers to other page without having a definition
            definition['description'] = parent_tag.select('.def')[0].text
        except IndexError:
            pass

        try: # synonym: a description may or may not have synonym
            synonym = parent_tag.select('.xrefs .prefix')[0].text
            if synonym == 'synonym':
                definition['synonym'] = "".join([synonym_tag.text
                                                 for synonym_tag in parent_tag.select('.xrefs .Ref .xr-g .xh')])
        except IndexError:
            pass

        definition['examples'] = [example_tag.text
                                  for example_tag in parent_tag.select('.examples .x')]

        definition['extra_example'] = [
            example_tag.text
            for example_tag in parent_tag.select('[unbox=extra_examples] .examples .unx')
        ]

        return definition

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

        for namespace in namespaces:
            definitions = []
            type = namespace.select('span.mw-headline')[0].text
            if type in vi_type.vi_types:
                ol = namespace.find_next("ol")
                lis = ol.find_all("li")

                for li in lis:
                    definition = {}
                    li_texts = li.text.split("\n")
                    definition['description'] = li_texts[0]
                    definition['examples'] = li_texts[1:(len(li_texts))]

                    definitions.append(definition)

                info.append({'namespace': namespace.select('span.mw-headline')[0].text, 'definitions': definitions})
            elif type in 'Tham khảo':
                break




        return info

        