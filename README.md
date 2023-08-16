# PegasusMetadataConverter
A python script to convert EmulationStation gamelist.xml files to Pegasus frontend's metadata.pegasus.txt files. I made this because I didn't want to copy and paste my gamelist.xml files into Pegasus' online converter tool at Pegasus' website.

Danger! This has been tested by me for bugs but I do not guarantee it will be completely bug free. Please use this software on a backup of your gamelist.xml files. This software has only been tested on Debian Linux.

Usage
1. copy the prettyFormattedAndroidEmulatorsWithName.xml to your home directory
2. run `python3 convertToPegasus.py /path/to/input_gamelist.xml /path/to/output_metadata.pegause.txt`

At first run on a particular directory it will create a launch.cfg file with a wizard to select launch parameters to import into the metadata.pegasus.txt. If you wish to run this wizard again remove the created launch.cfg file from your gamelist.xml folder.

You can compile this script with `python3 -m py_compile convertToPegasus.py`. `chmod +x` the resulting .pyc file and copy it to `~/.local/bin` to run from anywhere.
