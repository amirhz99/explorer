import emoji
import re

def remove_emojis(text: str) -> str:
    cleaned_text = emoji.replace_emoji(text, replace='')
    return cleaned_text

pre_characters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9",]


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


def generate_words_from_title(text, query):
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

        for character in pre_characters:
            if f'{sentence.strip().lower()} {character}'.strip().lower() in words:
                continue

            words.append(f'{sentence.strip().lower()} {character}')

        words.append(sentence)

    return words