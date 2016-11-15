# Pixelmon Updater
Updates or downgrades the pixelmonmod jar without having to download the complete mod every time.

#Usage

    patcher.py -p <pixelmon.jar> -s [target server]

or

    patcher.py -p <pixelmon.jar> -V [target version]

#Manual

    -p or --pixelmon defines the path to the pixelmon jar
    -s or --server defines the server that you want to check and get up to date
    -V or --pversion defines a certain version(es. 5.0.0-beta11,  5.0.0-beta9)

Check the file `pixelmondiff.txt` to see which pixelmon versions are available for update/downgrade.
#Technical details
The patcher will download from my dropbox folder only the files that differ from your current pixelmon version to the one you want to update/downgrade to.

The code signature reamins untouched so there isn't any security risk associated with patching the mod with this untrested code.

