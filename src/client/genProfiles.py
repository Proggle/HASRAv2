"""
    Author: Julian Pitney, Junzheng Wu, Gavin Heidenreich
    Email: JulianPitney@gmail.com, jwu220@uottawa.ca, gheidenr@uottawa.ca
    Organization: University of Ottawa (Silasi Lab)
"""

import os

def gen_profile(mouseName, cageNumber):

    if(os.path.isdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep + str(mouseName))):
        print(mouseName + " already has a profile! Skipping profile creation...")
        return 0
    else:
        print("Creating profile for " + str(mouseName) + "...")

    # RFID = input("Enter animal RFID: ")
    # cageNumber = input("Enter cage number: ")
    RFID = 0

    # profileDirectory = input("Enter profile save directory: ")
    profileDirectory = os.path.abspath(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName))
    mouseName = mouseName
    mouseNumber = mouseName[len(mouseName) - 1]
    difficulty = "0"
    paw = "LEFT"
    sessionNumber = "1"

    os.mkdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName))
    os.mkdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName) +os.sep+"Analyses")
    os.mkdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName)+os.sep+"Logs")
    os.mkdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+str(mouseName) +os.sep+"Videos")
    os.mkdir(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+str(mouseName) +os.sep+"Temp")

    saveFile = open(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName) + os.sep + str(mouseName) + "_save.txt", "w+")
    saveFile.write(str(RFID) + "\n")
    saveFile.write(str(mouseName) + "\n")
    saveFile.write(str(mouseNumber) + "\n")
    saveFile.write(str(cageNumber) + "\n")
    saveFile.write(str(difficulty) + "\n")
    saveFile.write(str(difficulty) + "\n")
    saveFile.write(str(difficulty) + "\n")
    saveFile.write(str(paw) + "\n")
    saveFile.write(str(sessionNumber) + "\n")
    saveFile.write(str(profileDirectory) + "\n")
    logFile = open(".."+os.sep+".."+os.sep+"AnimalProfiles"+os.sep+ str(mouseName)+os.sep+"Logs"+os.sep+ str(mouseName) + "_session_history.csv", "w+")
    print("Profile created for " + str(mouseName) + "!")


def main():
    animal_profiles_dir = '..' + os.sep + '..' + os.sep + 'AnimalProfiles'
    if not os.path.exists(animal_profiles_dir):
        os.makedirs(animal_profiles_dir)

    cageNumber = input('Enter cage number: ')
    print('Please remember to add Mouse RFID tag numbers, right now theyre all set to 0')
    print('This can be done by opening up MOUSE_save.txt for each MOUSE and editing the first line')

    for i in range(1,6):
        gen_profile("MOUSE" + str(i), cageNumber)

    gen_profile('TEST_TAG', cageNumber)


if __name__ == '__main__':
    DEBUG = False

    if DEBUG:
        pass
    else:
        main()


