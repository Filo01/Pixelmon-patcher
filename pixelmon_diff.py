#!/usr/local/bin/python2.7

import bsdiff
import argparse
import os
import zipfile
import sys
import json


def get_version(mcmod):
    loaded = json.loads(mcmod)
    return str(loaded[0]["version"])


def generate_filename(old, new):
    old = old.replace(".", "_")
    new = new.replace(".", "_")
    return old + "_to_" + new + ".zip"


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--old", required=True)
    parser.add_argument("-n", "--new", required=True)
    args = parser.parse_args()
    new = args.new
    old = args.old

    with open(old, "rb") as old_file:
        with open(new, "rb") as new_file:
            print("Diffing...")
            control, diff, extra = bsdiff.Diff(old_file.read(), new_file.read())
            print(type(json.dumps(control)))
            print(type(diff))
            print(type(extra))
            old_archive = zipfile.ZipFile(old)
            new_archive = zipfile.ZipFile(new)
            with old_archive.open("mcmod.info") as mcmod:
                old_version = get_version("".join(mcmod.readlines()))
            with new_archive.open("mcmod.info") as mcmod:
                new_version = get_version("".join(mcmod.readlines()))
            filename = generate_filename(old_version, new_version)
            print("Creating Diff file " + filename)
            zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
            size_control = {'size' : os.path.getsize(new), 'control': control}
            zipf.writestr('control', json.dumps(size_control))
            zipf.writestr('diff', diff)
            zipf.writestr('extra', extra)
            zipf.close()
    sys.exit()
