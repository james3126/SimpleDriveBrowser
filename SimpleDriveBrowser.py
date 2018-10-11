# All Drive Browser - James Kerley - 2018
# Imports
import os
import ctypes
import re
import string

# Function to install packages via pip from within the program
def install(package):
    pip.main(['install', package])

# First, check we have easygui installed, otherwise install it via our install() function
while True:
    try:
        import easygui as i
    except ModuleNotFoundError:
        print("Easy GUI not found! Installing ...")
        install('easygui')
    else:
        print("Easy GUI loaded")
        break

# Function to get all available drives
#
# This would only grab the local mounted drives -
# def find_drives():
#    return re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)
#
# Our new one here will get all the drives that are mounted, inluding net-drives
# By making use of the GetLogicalDrives() function
def find_drives():
    drives = []
    formatted_drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()

    # Find drive letters by finding matches to the uppercase alphabet
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    # This new method simply gets the letter, so we need to format it correctly
    for drive in drives:
        formatted_drives.append("{}:\\".format(drive))
        
    return formatted_drives


# Function to get the readable name of the found drive letters
def getDriveName(drive_letter):
    # Simple setting of the C to always be 'Local Disk'
    if drive_letter == 'C:\\':
        drive_name = 'Local Disk'

    # If not the C drive, then use the windows kernel to get the VolumeName
    # Via GetVolumeInformation() (Also gets plenty of other information that
    # Could be used.
    else:
        kernel32 = ctypes.windll.kernel32
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = None
        max_component_length = None
        file_system_flags = None

        rc = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive_letter),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            serial_number,
            max_component_length,
            file_system_flags,
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )

        drive_name = volumeNameBuffer.value

    return drive_name


# Function to get all the folders, in the current locations, absolute paths
# By simply looking at their name, and making use of os.path.abspath()
def get_folders(location):
    folders = []
    drive = location

    # We need to do a check to make sure we have permissions to access the file
    # In question, otherwise we will get an error, and the program will crash
    try:
        os.chdir(location)
    except PermissionError as p_e:
        print("ERROR: {}".format(p_e))
    else:
        get_current_locations = os.listdir(drive)
        for location in get_current_locations:
            if os.path.isdir(location) == True:
                folders.append(str(os.path.abspath(location))+'\\')
        return folders

    # If the permission check fails, then we need to setup a simple error to let
    # The user know. Then they can go BACK to the previous working dir.
    return ['FAILED: ACCESS IS DENIED','PLEASE GO BACK!','Click anywhere to go back.']

# Function to generate the file browser GUI by appending all the found folders
# In the current location into an EasyGUI choices box.
def browser_screen(location, drive_name):
    choices = []
    msg = "Current Dir Folders\nCurrent dir: "+location
    title = "Drive Browser - "+drive_name
    if len(location) > 3:
        choices.append('BACK')
    else:
        choices.append('CHANGE DRIVE')
    print(location)
    choices += get_folders(location)
    choice = i.choicebox(msg, title, choices)
    print("test")
    print(choice)
    return choice

# As this browser allows for multiple drives to be browsed, we need to be able
# To change drive. (For both the inital selection, and for when we have reached
# The root dir of the current selected drive). This may be a little messy as we
# Maniplulate the string from the option choice thats returned by EasyGUI, however
# It works perfectly and gets the job done.
def choose_drive():
    drives = []
    all_drive_letters = find_drives()
    for drive_letter in all_drive_letters:
        drives.append(drive_letter+" -> "+getDriveName(drive_letter))
    msg = "Select a drive"
    title = "Drive selector"
    selected_drive = i.choicebox(msg, title, drives)
    if selected_drive != None:
        selected_drive_name = 'drive: '+selected_drive.rsplit('-> ', 1)[1]
    else:
        print("EXITING..")
        exit(0)
    selected_drive_letter = selected_drive.rsplit("\\", 1)[0]+'\\'
    drive_details = [selected_drive_letter, selected_drive_name]
    print(drive_details)
    return drive_details

# Set some basic required vars by calling our choose_drive() function and then
# Extracting the returned data from it.
drive_details = choose_drive()
current_location = drive_details[0]
drive_name = drive_details[1]
locations = []
backTypes = ['BACK','FAILED: ACCESS IS DENIED','PLEASE GO BACK!','Click anywhere to go back.']

# Finally, start a forever loop that will generate the new file choosing screen
# Each time the user interacts with the GUI. This also keeps track of the current
# Directory, and the trail of directories that are above, giving us an absolute
# Path that allows the user to make use of a 'BACK' button.
while True:
    print("test")
    locations.append(current_location)
    print(locations)

    if current_location == None:
        print("EXITING...")
        exit(0)

    # A simple check to see if the BACK button (or any other message that would
    # Mean you have to go back) has been pressed, and to then change the current
    # File paths and history list.
    for backType in backTypes:
        if current_location == backType:
            print("removing" + locations[-1])
            del locations[-1]
            current_location = locations[-1]
            print("Location is now"+current_location)
            current_location = current_location.rsplit("\\", 2)[0]+'\\'
            print("Location is now"+current_location)
            locations.append(current_location)
            print(locations)

    # A simple check to see if the CHANGE DRIVE button has been pressed, and
    # Then to instead call our functions that will allow the user to change drive.
    if current_location == 'CHANGE DRIVE':
        locations = []
        drive_details = choose_drive()
        current_location = drive_details[0]
        drive_name = drive_details[1]
        
    # Finally, after everything has been completed for this 'round' of choices,
    # The browser_screen() function is called to generate us a new EasyGUI screen
    # And then display this to the user.
    current_location = browser_screen(current_location, drive_name)
    
        
