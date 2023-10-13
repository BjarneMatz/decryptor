import hashlib as hl
from database.database import Database as DB
import os
import multiprocessing as mp
from Logger.logger import Logger as LOG

log = LOG("Hash Generator").log
algorithms = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]


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


def generate_hashes(db, text: str):
    log(f"Generating hashes for '{text}'", 0, "file")
    encoded_text = text.encode("UTF-8")
    hashes = {}

    for algorithm in algorithms:
        hash_object = hl.new(algorithm, encoded_text)
        hex_dig = hash_object.hexdigest()
        hashes[algorithm] = hex_dig
    db.set_value(text, hashes)
    log(f"Generated hashes for '{text}'", 3, "file")


def split_work_for_multiprocessing(wordlist: list, processes: int):
    log(f"Splitting work for {processes} processes")
    chunk_size = len(wordlist) // processes # // = floor division, rounds down to nearest whole number
    chunks = []
    for i in range(processes): #range(4) = 0,1,2,3
        if i == processes - 1: 
            chunk = wordlist[i * chunk_size:] #last chunk gets the rest of the words
        else:
            chunk = wordlist[i * chunk_size:(i + 1) * chunk_size] #every other chunk gets chunk_size words
        chunks.append(chunk)
    log(f"Split work for {processes} processes", 3)
    log(f"Chunks: {chunks}", 4)
    log(f"Chunk size: {chunk_size}", 4) 
    return chunks

def multiprocess_worker(wordlist: list):
    worker_log = LOG(f"Worker {mp.current_process().name}").log
    worker_log(f"Starting work for {mp.current_process().name}")
    db = DB(f"hashes_{mp.current_process().name}")
    hashcount = 0
    for word in wordlist:
        generate_hashes(db, word.strip())
        hashcount += 1
        if hashcount % 250 == 0:
            worker_log(f"Generated {hashcount}/{len(wordlist)} hashes | {hashcount/len(wordlist)*100}%", 3)
    worker_log(f"Finished work", 3)
    
def multiprocess_handler(chunks: list):
    log("Starting work")
    processes = []
    for chunk in chunks:
        process = mp.Process(target=multiprocess_worker, args=(chunk,), name=f"worker_{chunks.index(chunk)}")
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    merge_databases(mp.cpu_count())
    log("Finished work", 3)

def merge_databases(processes: int):
    log("Merging databases")
    for i in range(processes):
        master_db = DB("hashes")
        hash_db = DB(f"hashes_worker_{i}")
        for key in hash_db.get_keys():
            master_db.set_value(key, hash_db.get_value(key))
        hash_db.delete_db_file()
        log(f"Merged database {i+1}/{processes}", 3)
    log("Merged all databases", 3)
        

if __name__ == "__main__":
    chunks = split_work_for_multiprocessing(load_dictionary("de"), mp.cpu_count())
    multiprocess_handler(chunks)
    


