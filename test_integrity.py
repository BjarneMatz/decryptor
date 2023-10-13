from database.database import Database as DB
from Logger.logger import Logger as LOG
import os

db = DB("hashes")
log = LOG("Integrity Test").log
bad_words = []


def load_dictionary(language: str):
    log(f"Loading dictionary for language '{language}'")
    #ISO 639-1 codes (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    script_path = os.getcwd()
    wordlist = []
    if language == "de":
        with open(f"{script_path}/dictionarys/de", "r", encoding="utf-8") as file_data:
            wordlist = file_data.readlines()
    log(f"Loaded {len(wordlist)} words from dictionary", 3)
    return wordlist

def test_word(word: str):
    if db.get_value(word) == None:
        log(f"Word '{word}' not found in database!", 1)
        bad_words.append(word)
        
def main():
    wordlist = load_dictionary("de")
    log("Starting integrity test")
    for word in wordlist:
        test_word(word.strip())
    if bad_words == []:
        log("Integrity test successful!", 3)
    else:
        log(f"Words not found in database: {bad_words}", 1)
        
if __name__ == "__main__":
    main()
    