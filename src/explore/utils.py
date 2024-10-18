import emoji
import re


pre_characters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9",]

def generate_words_with_characters(text):
    return [f'{text} {character}'.strip() for character in pre_characters]
    
def remove_emojis(text: str) -> str:
    cleaned_text = emoji.replace_emoji(text, replace='')
    return cleaned_text

def split_title(text):
    splitters = ['&', ',', '_', '/', '|', '-', '.', '+']

    for splitter in splitters:
        text = text.replace(splitter, ' ')

    return unique_list([string.strip() for string in text.split(' ') if string != ''])


def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist


def remove_duplicate(text):
    return ' '.join(unique_list(text.strip().lower().split()))


def generate_words_from_title(text, query,use_pre_characters:bool=True):
    words = []
    text = remove_emojis(text)
    for word in split_title(text):

        if query not in word.strip().lower():
            sentence = f'{query} {word.strip()}'
        else:
            sentence = word

        sentence = remove_duplicate(sentence)

        if sentence in words or sentence == query:
            continue
        
        if use_pre_characters:
            for character in pre_characters:
                if f'{sentence.strip().lower()} {character}'.strip().lower() in words:
                    continue
                words.append(f'{sentence.strip().lower()} {character}')
        else:
            if sentence.strip().lower() in words:
                words.append(sentence.strip().lower())

        words.append(sentence)

    return words