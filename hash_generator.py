import hashlib as hl
from database.database import Database as DB
import os
import multiprocessing as mp



def load_dictionary(language: str):
    #ISO 639-1 codes (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    script_path = os.getcwd()
    wordlist = []
    if language == "de":
        with open(f"{script_path}/dictionarys/de", "r") as file_data:
            wordlist = file_data.readlines()
    return wordlist


def generate_hashes(db, text: str):
    encoded_text = text.encode("UTF-8")
    algorithms = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    hashes = {}

    for algorithm in algorithms:
        hash_object = hl.new(algorithm, encoded_text)
        hex_dig = hash_object.hexdigest()
        hashes[algorithm] = hex_dig
    db.set_value(text, hashes)


def split_work_for_multiprocessing(wordlist: list, processes: int):
    chunk_size = len(wordlist) // processes # // = floor division, rounds down to nearest whole number
    chunks = []
    for i in range(processes): #range(4) = 0,1,2,3
        if i == processes - 1: 
            chunk = wordlist[i * chunk_size:] #last chunk gets the rest of the words
        else:
            chunk = wordlist[i * chunk_size:(i + 1) * chunk_size] #every other chunk gets chunk_size words
        chunks.append(chunk)
        print(f"Chunk {i} has {len(chunk)} words")
        
    return chunks

def multiprocess_worker(wordlist: list):
    db = DB(f"hashes_{mp.current_process().name}")
    hashcount = 0
    for word in wordlist:
        generate_hashes(db, word.strip())
        hashcount += 1
        if hashcount % 1000 == 0:
            print(f"[{mp.current_process().name}] Generated {hashcount}/{len(wordlist)} hashes")
        
    print("Finished work")
    
def multiprocess_handler(chunks: list):
    
    processes = []
    for chunk in chunks:
        process = mp.Process(target=multiprocess_worker, args=(chunk,), name=f"process_{chunks.index(chunk)}")
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    print("Finished all work")
    



if __name__ == "__main__":
    chunks = split_work_for_multiprocessing(load_dictionary("de"), mp.cpu_count())
    multiprocess_handler(chunks)


