# Pixelmon Updater
Updates or downgrades the pixelmonmod jar without having to download the complete mod every time.

# Usage

    patcher.py -p <pixelmon.jar> -s [target server]

or

    patcher.py -p <pixelmon.jar> -V [target version]

# Manual

The -p option is required but you can choose wether to specify a version or check the one running on a selected server

 - Define the pixelmonmod absolute path with `-p or --pixelmon`
 - Define a server to check with `-s or --server`
 - Define a specific version with `-V or --pversion`(es. 5.0.0-beta11,  5.0.0-beta9)

Check the file `pixelmondiff.txt` to see which pixelmon versions are available for update/downgrade.
#Technical details
The patcher will download from my dropbox folder only the files that differ from your current pixelmon version to the one you want to update/downgrade to.
