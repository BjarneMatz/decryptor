import hashlib as hl
from database.database import Database as DB
import os
db = DB("hashes")

def load_dictionary(language: str):
    #ISO 639-1 codes (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    script_path = os.getcwd()
    wordlist = []
    if language == "de":
        with open(f"{script_path}/dictionarys/de", "r") as file_data:
            wordlist = file_data.readlines()
    return wordlist


def generate_hashes(text: str):
    encoded_text = text.encode("UTF-8")
    algorithms = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    hashes = {}

    for algorithm in algorithms:
        hash_object = hl.new(algorithm, encoded_text)
        hex_dig = hash_object.hexdigest()
        hashes[algorithm] = hex_dig
    db.set_value(text, hashes)
    

if __name__ == "__main__":
    wordlist = load_dictionary("de")
    hashcount = 0
    for word in wordlist:
        generate_hashes(word.strip())
        hashcount += 1
        if hashcount % 1000 == 0:
            print(f"Working on hash {hashcount}/{len(wordlist)} | {int((hashcount/len(wordlist))*100)}%")




