import os
from anki import anki

def get_list_word(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines

def write_error_word(error_words):
    with open('error_words.txt', 'w') as f:
        f.writelines(error_words)

def main(file_path, deck_name, note_type):
    words = get_list_word(file_path)
    error_words = anki.gen_anki_apkg_file(deck_name, note_type ,words)
    if len(error_words) > 0:
        write_error_word(error_words) 
        print('Some words have eror during execution, pls check the error_words.txt file for datails')
    else:
        print('Successly')

if __name__ == '__main__':
    while True:
        file_path = input('Please enter the path of your words file: ')
        file_path = file_path.strip()
        if file_path.strip() == "":
            print("File path cannot be empty.")
            continue
        elif not os.path.isfile(file_path):
            print("This file is unavailable.")
            continue
        else:
            break
    print('-------------------------------')
        
    while True:
        deck_name = input('Pls enter your the deck name that do you want: ')
        deck_name = deck_name.strip()
        if deck_name.strip() == "":
            print("Deck name cannot be empty")
            continue
        else:
            break
    print('-------------------------------')
        
    while True:
        note_type = input('Pls enter your the note type that do you want: ')
        note_type = note_type.strip()
        if note_type.strip() == "":
            print("Note type cannot be empty")
            continue
        else:
            break
    print('-------------------------------')

    main(file_path, deck_name, note_type)