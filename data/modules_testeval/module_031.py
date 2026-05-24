from typing import List

def replaceWords(dictionary: List[str], sentence: str) -> str:
    root = {}

    def insert(word: str) -> None:
        node = root

        for c in word:
            if c not in node:
                node[c] = {}
            node = node[c]

        node['word'] = word

    def search(word: str) -> str:
        node = root

        for c in word:
            if 'word' in node:
                return node['word']

            if c not in node:
                return word

            node = node[c]

        return word

    for word in dictionary:
        insert(word)

    words = sentence.split(' ')
    return ' '.join([search(word) for word in words])