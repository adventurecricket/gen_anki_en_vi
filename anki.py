import genanki
import oxford_and_vn as oxf_vn

class anki:

  @classmethod
  def get_en_meaning(self, info):
    str_info = ''
    word_form = info.get('wordform')
    word_form = word_form[0].upper() + word_form[1:]
    formal = info.get('formal')
    str_info = '<font color="#ff0000">'
    str_info += f'[{word_form}]<br>'
    str_info += '</font>'
    if formal != None:
      str_info += '<font color="#ffaa00">'
      str_info += f'{formal}<br>'
      str_info += '</font>'
    
    for meaning in info.get('meaning'):
      name_space = meaning.get('namespace')
      if name_space != '__GLOBAL__' and name_space != None:
        name_space = name_space[0].upper() + name_space[1:]
        str_info += '<font color="#25cb00">'
        str_info += f'<b>({name_space})</b><br>'
        str_info += '</font>'
      
      for sense in meaning.get("definitions"):
        description = sense.get('description')
        property = sense.get('property')
        if property != None:
          str_info += f'-&nbsp;<font color="#aaaa7f"><span style="font-style: italic; font-weight: inherit;">{property}</span></font> {description}<br>'
        else:
          str_info += f'-&nbsp; {description}<br>'
        synonym = sense.get("synonym")
        if synonym:
          str_info += f'<b>Synonym </b>'
          str_info += f'<font color="#ff5500"><span style="font-style: italic; font-weight: inherit;">{synonym}</span></font><br>'
        examples = sense.get("examples")
        if examples != None:
          str_info += '<font color="#0000ff">'
          for example in sense.get("examples"):
            str_info += f'<span style="font-style: italic; font-weight: inherit;">{example}</span><br>'
          str_info += '</font>'
          
    return str_info

  @classmethod
  def get_vi_meaning(self, info):
    str_info = ''
    
    name_space = info.get('namespace')
    if name_space != None:
      name_space = name_space[0].upper() + name_space[1:]
      str_info += '<font color="#25cb00">'
      str_info += f'<b>({name_space})</b><br>'
      str_info += '</font>'
    
    for sense in info.get("definitions"):
      description = sense.get('description')
      if description != None:
        str_info += f'-&nbsp; {description}<br>'
      examples = sense.get("examples")
      if examples != None:
        str_info += '<font color="#0000ff">'
        for example in sense.get("examples"):
          str_info += f'<span style="font-style: italic; font-weight: inherit;">{example}</span><br>'
        str_info += '</font>'
          
    return str_info

  @classmethod
  def get_field_info(self, en_infoes, vi_infoes):
    cloze = ''
    word_form = ''
    ipa = ''
    word_name = en_infoes[0].get('name')
    en_mean = ''
    vi_mean = ''
    extra = ''

    lEn_Word_name  = len(word_name)
    if lEn_Word_name > 2:
      cloze = word_name[0] + '.....' + word_name[lEn_Word_name - 1]
    else:
      cloze = word_name[0] + '.....'

    for pronunc in en_infoes[0].get('pronunciations'):
      if pronunc.get('prefix') == 'nAmE':
        ipa = pronunc.get('ipa')

    for info in en_infoes:
      if word_form != '':
        word_form += ', '
      word_form += info.get('wordform')
      extra_info = info.get('extractinfo')
      if extra_info != None:
        if extra != '':
          extra += '<br>'
        extra += f'-&nbsp;{extra_info}'
      
      en_mean += self.get_en_meaning(info)

    for info in vi_infoes:
      vi_mean += self.get_vi_meaning(info)

    fields = [
      word_name,
      cloze,
      word_form, 
      ipa,
      '',
      en_mean,
      vi_mean,
      extra,
      ''
    ]

    return fields

  @classmethod
  def gen_anki_note(self, note_type, en_infoes, vi_infoes):

    my_model = genanki.Model(
    6666666666,
    note_type,
    fields=[
      {'name': 'Word'},
      {'name': 'Cloze'},
      {'name': 'Word Type'},
      {'name': 'Phonetic symbol'},
      {'name': 'Audio'},
      {'name': 'English Meaning'},
      {'name': 'Vietnamese Meaning'},
      {'name': 'Extra information'},
      {'name': 'Picture'}
    ],
    templates=[
      {
        'name': 'Card 1',
        'qfmt': '{{Word}}',
        'afmt': '{{FrontSide}}<hr id="Word">{{Word}}',
      },
    ])
    
    my_note = genanki.Note(
      model = my_model,
      fields= self.get_field_info(en_infoes, vi_infoes)
    )
    
    return my_note

  @classmethod
  def get_en_info(self, word):
    all_info = []
    oxf_vn.En_Word.get(word)

    info = oxf_vn.En_Word.shorten_info()
    all_info.append(info)

    other_results = oxf_vn.En_Word.other_results()
    if other_results != None:
      other_words = other_results[0]["All matches"]
      for other_word in other_words:
          if other_word["name"] == word:
              oxf_vn.En_Word.get(other_word["id"])
              if oxf_vn.En_Word.name() == word:
                  info = oxf_vn.En_Word.shorten_info()
                  all_info.append(info)
    
    return all_info

  @classmethod
  def get_vi_info(self, word):
      all_info = []
      try:
        oxf_vn.Vi_Word.get(word)
        all_info = oxf_vn.Vi_Word.definition_full()
      except:
        pass

      return all_info
  
  @classmethod
  def gen_anki_apkg_file(self, deck_name, note_type, words):
    error_words = []

    my_deck = genanki.Deck(
      2059400110,
      deck_name)

    for word in words:
      try:
        temp_word = word.replace('\n','').strip().lower()
        print(f'-------------------{temp_word}-------------------')
        en_info = self.get_en_info(temp_word)
        vi_info = self.get_vi_info(temp_word)
        my_note = self.gen_anki_note(note_type, en_info, vi_info)
        my_deck.add_note(my_note)
      except:
        error_words.append(word)
    
    genanki.Package(my_deck).write_to_file(f'{deck_name}.apkg')

    return error_words