#!/usr/bin/env python3

import bsdiff4, json, os, hashlib, shutil, gzip

dir_new = "new_files"
dir_current = "current_files"
dir_download = "download/files"
dir_patch = "download/patch"

file_list = "download/list.json"

buf_size = 65536

def hash(filename):
    md5 = hashlib.md5()
    with open(filename, mode='rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()

if __name__ == "__main__":
    for filename in os.listdir(dir_new):
        old_path = os.path.join(dir_current, filename)
        new_path = os.path.join(dir_new, filename)
        download_path = os.path.join(dir_download, f"{filename}.gz")
        
        if os.path.isfile(old_path):
            patch_path = os.path.join(dir_patch, filename)
            os.makedirs(patch_path, exist_ok=True)

            old_hash = hash(old_path)
            if old_hash != hash(new_path):
                if os.path.isfile(old_path):
                    print(f"making patch of {filename}")
                    bsdiff4.file_diff(old_path, new_path, os.path.join(patch_path, old_hash))
                    print("finished writing patch")

        shutil.copyfile(new_path, old_path)
        
        with open(new_path, 'rb') as f_in:
            with gzip.open(download_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(new_path)

    files = {}

    for filename in os.listdir(dir_current):
        files[filename] = hash(os.path.join(dir_current, filename))

    json.dump(files, open(file_list, mode="w+"))
