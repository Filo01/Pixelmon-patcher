#!/usr/local/bin/python
#  -*- coding: utf-8 -*-
import shutil
import zipfile
import os
import json
import argparse
import sys
import tempfile
import urllib2
import traceback
import json
from mcstatus import GetJson


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        print("Created " + path)
    except OSError as exception:
        pass


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        zip_root = root.replace(path, "")
        for file in files:
            ziph.write(os.path.join(root, file), arcname=zip_root+"/"+file)


def get_server_version(server):
    s = server.split(":")
    host = s[0]
    port = s[1] if len(s)==2 else 25565
    try:
        update = GetJson(host, port=port)
    except Exception:
        print("Error: can't connect to " + server)
        return None
    try:
        for mod in update['modinfo']['modList']:
            if mod['modid'] == 'pixelmon':
                return mod['version']
        print("Error: the specified server is not a Pixelmon server")
    except KeyError:
        print("Error: the specified server is not a Forge server")

    return None


def generate_patch_name(old_v, new_v):
    old_v=old_v.replace(".", "_")
    new_v=new_v.replace(".", "_")
    return old_v +"_to_"+new_v


def get_version(mcmod):
    loaded = json.loads(mcmod)
    return str(loaded[0]["version"])


def get_current_version(pixelmon_jar):
    mcmod = pixelmon_jar.read('mcmod.info')
    return get_version(mcmod)


def get_diffzip_path(patch_name, tmp):
    print("Retrieving patch list")
    patches = urllib2.urlopen("https://raw.githubusercontent.com/Blank01/pixelmon_update/master/pixelmondiff.txt").read()
    for line in patches.split('\n'):
        if line.strip() == "":
            break
        patch = line.split(" ")
        if len(patch) == 2 and patch[0] == patch_name:
            response = urllib2.urlopen(line.split(' ')[1])
            print("Downloading patch " + patch_name)
            zipcontent = response.read()
            diffzip_path = os.path.join(tmp, patch_name+".zip")
            with open(diffzip_path, 'w') as f:
                f.write(zipcontent)
            return diffzip_path
    #if we can't find the right patch raise the exception which will be caught and the program will exit
    raise Exception

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Patches the current pixelmon mod  installed with the one required by the server specified via --server, or by directly writing the selected version via --version",)
    parser.add_argument('-V', '--pversion', required = False)
    parser.add_argument('-s', '--server', required = False)
    parser.add_argument('-p', '--pixelmon', help='path to the pixelmon jar to patch', required= True)

    args = parser.parse_args()

    pixelmon = args.pixelmon
    server = args.server
    new_version = args.pversion

    if not server and not new_version:
        print("Specify either --server(-s) or --pixelmon-version(-V)")
        sys.exit()
    old = zipfile.ZipFile(pixelmon, 'r')
    old_version = get_current_version(old)

    if server:
        new_version = get_server_version(server)
    if new_version is None:
        print("Quitting...")
        sys.exit(-1)
    if(old_version==new_version):
        print("Pixelmon already up to date")
        sys.exit()

    print("Trying to upgrade from " + old_version + " to " + new_version)
    patch_name = generate_patch_name(old_version, new_version)


    tmp = tempfile.mkdtemp()
    try:
        diff_path = os.path.join(tmp, "diff")
        try:
            diffzip_path = get_diffzip_path(patch_name, tmp)
        except:
            print("Error: can't find patch for " + old_version + " to " + new_version)
            sys.exit(-1)

        diff = zipfile.ZipFile(diffzip_path, 'r')
        old_path = os.path.join(tmp, "old_pixelmon")

        print("Extracting current Pixelmon jar...")
        old.extractall(path=old_path)
        print("Done")
        print("Extracting patch " + patch_name + "...")
        diff.extractall(path=diff_path)
        print("Done")

        print("Deleting obsolete files...")
        with open(os.path.join(diff_path, "remove.txt")) as f:
            for line in f:
                line=line.strip()[1:]
                line=line.replace('/', os.path.sep)
                del_file = os.path.join(old_path, line)
                os.remove(del_file)
                print("Removed: " + os.path.join(old_path, line))
        print("Updating new files...")
        for root, subFolders, files in os.walk(diff_path):
                for f in files:
                    new_root = root.replace("diff", "old_pixelmon")
                    make_sure_path_exists(new_root)
                    print("Updating: " + os.path.join(new_root, f).replace(old_path, ""))
                    shutil.move(os.path.join(root, f), os.path.join(new_root, f))
        print("Updating the Pixelmon jar in its folder...")
        pixelmon_path = os.path.dirname(os.path.abspath(pixelmon))
        zipf = zipfile.ZipFile(os.path.join(pixelmon_path, 'pixelmon-patched-'+ new_version + '.jar'), 'w', zipfile.ZIP_DEFLATED)
        zipdir(old_path, zipf)
        zipf.close()
        os.remove(pixelmon)
        print("Successfully updated from " + old_version + " to " + new_version)
    except Exception as inst:
        traceback.print_exc()
        print("Error: Could not update to " + new_version)
    finally:
        shutil.rmtree(tmp)


