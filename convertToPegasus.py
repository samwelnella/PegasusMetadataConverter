#Convert gamelist.xml to pegasys.metadata
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import os.path

#Defining mapping for gamelist.xml systems to Pegasus shortname systems
shortname_mapping = ({
	'3do': '3do',
	'nintendo 3ds': 'n3ds',
	'super nintendo entertainment system': 'snes',
	'nintendo entertainment system': 'nes',
	'neo geo pocket color': 'ngpc',
	'sega master system': 'mastersystem',
	'wonderswan color': 'wonderswancolor',
	'playstation vita': 'psvita',
	'game boy advance': 'gba',
	'sega mega drive': 'megadrive',
	'atari jaguar cd': 'atarijaguarcd',
	'sega game gear': 'gamegear',
	'sega dreamcast': 'dreamcast',
	'nintendo wii u': 'wiiu',
	'neo geo pocket': 'ngp',
	'game boy color': 'gbc',
	'turbografx 16': 'tg16',
	'playstation 4': 'ps4',
	'playstation 3': 'ps3',
	'playstation 2': 'ps2',
	'intellivision': 'intellivision',
	'sega genesis': 'genesis',
	'nintendo wii': 'wii',
	'commodore 64': 'c64',
	'colecovision': 'colecovision',
	'atari jaguar': 'atarijaguar',
	'zx spectrum': 'zxspectrum',
	'sega saturn': 'saturn',
	'playstation': 'psx',
	'nintendo ds': 'nds',
	'nintendo 64': 'n64',
	'wonderswan': 'wonderswan',
	'atari lynx': 'atarilynx',
	'atari 7800': 'atari7800',
	'atari 5200': 'atari5200',
	'atari 2600': 'atari2600',
	'atari 800': 'atari800',
	'sega 32x': 'sega32x',
	'gamecube': 'gc',
	'game boy': 'gb',
	'atari xe': 'atarixe',
	'atari st': 'atarist',
	'sega cd': 'segacd',
	'amstrad': 'amstrad',
	'neogeo': 'neogeo',
	'arcade': 'arcade',
	'apple2': 'apple2',
	'amiga': 'amiga',
	'vita': 'psvita',
	'snes': 'snes',
	'psp': 'psp',
	'nes': 'nes',
	'msx': 'msx',
	'mac': 'macintosh',
})
	

#Defining mapping for system-level gamelist.xml keys to pegasus.metadata.txt keys
collection_mapping = ({
	'System': 'collection',
	'software': 'x-scrape-software',
	'database': 'x-scrape-database',
})

#Defining mapping for games-level gamelist.xml keys to pegasus.metadata.txt keys
game_mapping = ({
	'name': 'game',
	'path': 'file',
	'developer': 'developer',
	'publisher': 'publisher',
	'genre': 'genre',
	'desc': 'description',
	'players': 'players',
	'releasedate': 'release',
	'rating': 'rating',
    #true or false value
	'favorite': 'favorite',
	#int value
	'playcount': 'playCount',
	#don't know the syntax
	'lastplayed': 'lastPlayed',
	#in seconds a int value
	'gametime': 'playTime',
	'hash': 'x-hash',
	'genreid': 'x-genreid',
 	'thumbnail': 'assets.boxFront',
#	'assets.boxBack': a,
#	'assets.boxSpine': b,
#	'assets.boxFull': c,
#	'assets.cartridge': d,
#	'assets.logo': e,
	'marquee': 'assets.marquee',
#	'assets.bezel': g,
#	'assets.panel': h,
#	'assets.cabinetLeft': i,
#	'assets.cabinetRight': j,
#	'assets.tile': k,
#	'assets.banner': l,
#	'assets.steam': m,
#	'assets.poster': n,
#	'assets.background': o,
#	'assets.music': p,
	'image': 'assets.screenshot',
#	'assets.titlescreen': r,
	'video': 'assets.video', 
    # Add other relevant fields as needed
})

#Test if user defined input and output files and set variables or show an error accordingly
try:	
	inFile = os.path.abspath(sys.argv[1])
except IndexError:
    ("No input file specified! Command syntax is convertToPegasus input_file output_file")
    sys.exit(1)
try:
	outFile = os.path.abspath(sys.argv[2])	
except IndexError:
    print("No output file specified! Command syntax is convertToPegasus input_file output_file")
    sys.exit(1)

#Function to parse a gamelist.xml file and return a list of collections and a list of games with pegasus.metadata.xml key names and pegasus.metadata.xml formatted dates
def parse_emulationstation_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    games = []
    providers = []
    system = ''
    
    for provider in root.findall('provider'):
    	#Define this temp variable within the for loop so Python does not overwrite the same dict entry in the list over and over again
    	providersTemp = {}
    	for element in provider:
    		#Make sure the key has a value
    		if element.text is not None:
    			#Make sure that the gamelist.xml XML tag exists in the predefined providers mapping, otherwise skip the tag
    			if element.tag in collection_mapping:
    				providersTemp[collection_mapping[element.tag]] = element.text
    				if element.tag == 'System':
    					if element.text.lower() in shortname_mapping:
    						system = shortname_mapping[element.text.lower()]
    	#Append the Pegasus' formatted collections section to the list
    	providers.append(providersTemp)
    
    for game in root.findall('game'):
    	#Define this temp variable within the for loop so Python does not overwrite the same dict entry in the list over and over again
    	gamesTemp = {}
    	for element in game:
    		#Make sure the key has a value (not needed anymore)
    		if element.text is not None:
    			#Make sure that the gamelist.xml XML tag exists in the predefined game mapping, otherwise skip the tag
    			if element.tag in game_mapping:
    				#Check if the element is releasedate and convert the date to Pegasus' format
    				if element.tag == 'releasedate' or element.tag == 'lastplayed':
    					gamesTemp[game_mapping[element.tag]] = convert_date_format(element.text)
    				#Otherwise convert the key name to Pegasus' format and strip out any errant newline characters
    				else:
    					gamesTemp[game_mapping[element.tag]] = element.text.strip()
		#Append the Pegasus' formatted keys and data to the list
    	games.append(gamesTemp)

    return games, providers, system

#Function that takes a list of games and providers from parse_emulationstation_xml and outputs a Debian control file format variable that can be written to a metadata.pegasus.xml file
def generate_pegasus_metadata(games, providers, launchConfig):
    metadata = []
    
    for provider in providers:
    	#For every provider entry loop through all keys in the provider entry and append the key in Debian control file format
    	for key in provider:
    		metadata.append(key + ": " + provider[key])
    	#Add a blank line between providers
#    	metadata.append("")
    
    if launchConfig is not None:	
    	metadata.append(launchConfig)
    metadata.append("")

    for game in games:
    	#For every game entry loop through all keys in the game entry and append the key in Debian control file format
    	for key in game:
    		metadata.append(key + ": " + game[key])
    	#Add blank line between games
    	metadata.append("")
    	
    metadata_content = "\n".join(metadata)
    return metadata_content

def convert_date_format(input_date):
    # Parse input date string
    input_format = "%Y%m%dT%H%M%S"
    date_obj = datetime.strptime(input_date, input_format)
    
    # Format the date in the desired output format
    output_format = "%Y-%m-%d"
    output_date = date_obj.strftime(output_format)
    
    return output_date
    
def open_launchcfg_file(system):
    launchConfig = ''
    if system != '':
	    try:
	    	with open(os.path.join(os.path.dirname(inFile),'launch.cfg'), 'x') as file:
	    		print("launch.cfg not detected. Creating file.\n")
#	    		while True:
	    		print("Are you using metadata file with Android? (y/n)\n")
	    		android = input("Enter: ")
#	    			if android != 'y' or android != 'Y' or android != 'n' or android != 'N':
#	    				print('Please enter y or n')
#	    				continue
#	    			break
	    		tree = ET.parse(os.path.join(Path.home(), 'prettyFormattedAndroidEmulatorsWithName.xml'))
	    		root = tree.getroot()
	    		for emulator in root.findall('Emulator'):
	    			if emulator.find('shortname').text != system:
	    				root.remove(emulator)
	    		print("Which android emulator would you like to use?")
	    		count = 0
	    		for emulator in root.findall('Emulator'):
	    			count = count + 1
	    			print(str(count) + ") " + emulator.find('name').text + "\n")
#	    		while True:
	    		emulatorInput = input("Enter: ")
#	    			try:
	    		emulatorInput = int(emulatorInput)
#	    			except:
#	    				print = ('Please enter a number between 1 and ' + count)
#	    				continue
#	    			if emulatorInput < 1:
#	    				print = ('Please enter a number between 1 and ' + count)
#	    				continue
#	    			if emulatorInput > count:
#	    				print = ('Please enter a number between 1 and ' + count)
#	    				continue
#	    			break
	    		emulatorInput = emulatorInput - 1
	    		if android == 'y' or android == 'Y':
	    			launchConfig = "shortname: " + root[emulatorInput][1].text + "\n" + "extensions: " + root[emulatorInput][2].text + "\n" + "launch: " + root[emulatorInput][3].text
	    		else:
	    			launchConfig = "shortname: " + root[emulatorInput][1].text + "\n" + "extensions: " + root[emulatorInput][2].text + "\n" + "launch: "
	    			launchCustom = input("Enter your custom launch configuration:")
	    			launchConfig = launchConfig + launchCustom
	    			
	    		with open(os.path.join(os.path.dirname(inFile), 'launch.cfg'), 'w') as file:
	    			file.writelines(launchConfig)
	#    		print(emulator)
	    except FileExistsError:
	    	print("launch.cfg detected.")
	    	with open(os.path.join(os.path.dirname(inFile), 'launch.cfg'), 'r') as file:
	        	launchConfig = file.read()
	        
	    return(launchConfig)

if __name__ == "__main__":
    m, p, s = parse_emulationstation_xml(inFile)
    launchCfg = open_launchcfg_file(s)
    pegasus_metadata = generate_pegasus_metadata(m, p, launchCfg)
    #pegasus_metadata = generate_pegasus_metadata(parse_emulatorstation_xml(inFile))
    
    with open(outFile, "w") as control_file:
    	control_file.write(pegasus_metadata)
