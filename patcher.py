#!/usr/bin/env python3

import os, hashlib, requests, math, gzip, shutil
from bsdiff4 import file_patch_inplace

current_directory = os.path.dirname(os.path.realpath(__file__))
files_path = ""

buf_size = 65536

def hash(filename):
    md5 = hashlib.md5()
    with open(filename, mode='rb') as f:
        while True:
            data = f.read(buf_size)
            if not data: break
            md5.update(data)

    return md5.hexdigest()

def print_progress(n, total, size=20):
    fill = "█" * math.floor((n / total) * size)
    remaining = " " * (size - len(fill))
    print(f"    |{fill}{remaining}| {n}/{total}", end="\r")

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        if r.status_code != 200: return False
        total_size = int(r.headers["content-length"])
        downloaded = 0
        with open(filename, 'wb') as f:
            print(filename)
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    downloaded = downloaded + len(chunk)
                    print_progress(downloaded, total_size)
                    f.write(chunk)
    return True

if __name__ == "__main__":
    files = requests.get(os.path.join(files_path, "list.json")).json()

    for filename in files:
        local_path = os.path.join(current_directory, filename)
        url = os.path.join(files_path, "files", f"{filename}.gz").replace("\\", "/")

        if os.path.isfile(local_path):
            old_hash = hash(local_path)
            if old_hash != files[filename]:
                print(f"{filename} is old, looking for patch")

            while old_hash != files[filename]:
                patch_url = os.path.join(files_path, "patch", filename, old_hash).replace("\\", "/")
                if download_file(patch_url, f"{filename}.patch"):
                    print(f"\npatching {filename}")
                    file_patch_inplace(filename, f"{filename}.patch")
                    os.remove(f"{filename}.patch")
                else:
                    print("no patch found, downloading entire file")
                    download_file(url, f"{filename}.gz")
                    print("\ndecompressing")
                    with gzip.open(f"{filename}.gz", "rb") as compressed_file:
                        with open(filename, "wb+") as new_file:
                            shutil.copyfileobj(compressed_file, new_file)
                    os.remove(f"{filename}.gz")

                old_hash = hash(local_path)
            continue
        
        print(f"{filename} is missing, downloading")
        download_file(url, f"{filename}.gz")
        print("\ndecompressing")
        with gzip.open(f"{filename}.gz", "rb") as compressed_file:
            with open(filename, "wb+") as new_file:
                shutil.copyfileobj(compressed_file, new_file)
        os.remove(f"{filename}.gz")
