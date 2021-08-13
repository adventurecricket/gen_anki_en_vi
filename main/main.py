from anki import anki
from oxford import Word as en_word
from wiki_vi import Word as vi_word


import pprint

def get_en_info(word):
    all_info = []
    en_word.get(word)

    info = en_word.shorten_info()
    all_info.append(info)

    other_results = en_word.other_results()
    other_words = other_results[0]["All matches"]
    for other_word in other_words:
        if other_word["name"] == word:
            en_word.get(other_word["id"])
            if en_word.name() == word:
                info = en_word.shorten_info()
                all_info.append(info)
    
    return all_info

def get_vi_info(word):
    all_info = []
    vi_word.get(word)
    all_info = vi_word.definition_full()

    return all_info

def get_list_word():
    with open('D:\Python\gen_anki_en_vi\main\words.txt', 'r') as f:
        lines = f.readlines()
    return lines

def write_error_word(error_words):
    with open('D:\Python\gen_anki_en_vi\main\error_words.txt', 'w') as f:
        f.writelines(error_words)

def main():
    words = get_list_word()
    error_words = anki.gen_anki_apkg_file(words)
    if len(error_words) > 0:
        print('Some words have eror during execution, pls check the error_words.txt file for datails')
    else:
        print('Successly')

if __name__ == '__main__':
    main()