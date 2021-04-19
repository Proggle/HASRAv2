[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# **Overview**:

This system allows the user to host up to 5 mice in their home environment and automatically administer the single pellet reaching test to those animals. The system can run unsupervised and continuously for weeks at a time, allowing all 5 mice to perform an unlimited number of single pellet trials at their leisure. 

The design allows a single mouse at a time to enter the reaching tube. Upon entry, the animal’s RFID tag will be read, and if authenticated, a session will start for that animal. A session is defined as everything that happens from the time an animal enters the reaching tube to when they leave the tube. At the start of a session, the animal’s profile will be read and the task difficulty as well as the left and right preference will be automatically adjusted by moving the pellet presentation arm to the appropriate distance both away from the reaching tube and from right to left. Pellets will continue to be presented periodically until the mouse leaves the tube, at which point the session will end. Video and other data is recorded for the duration of each session. At session end, all the data for the session is saved in an organized way. We also have an auxiliary function for counting the successful rate of displaying a pellet using MobileNetV2 based on tensorflow and keras.

For further analyse, you can check the repository posted here:
https://github.com/SilasiLab/HomecageSinglePellet_Manual





# **Dependencies:**
* Ubuntu v16.04 LTS: Kernel version 4.4.19-35 or later
* Or Windows 10 is recommended, since the backend camera driver performs better that the one on linux in our experiment.
* Anaconda 3 environment, for the dependancies without a version number, it means there is no specific requirement on it. 
	* Python==3.6.10
	* pySerial==3.4	
	* numpy==1.18.1
	* OpenCV=4.1.2 (A whl file is provided under requirment folder.)
	* tkinter=8.6.8
	* matplotlib=3.1.3
	* Pillow
	* tqdm
	* tensorflow=1.10.0
	* keras=2.2.4
	* psutil
	* multiprocessing
	* subprocess
	
* Arduino IDE v1.8.5

# **Software Installation for x86 (Jetson/ARM instructions below):**
1. Windows 10 is strongly recommended for a better support of camera driver. Ubuntu 16.04 LTS is alternative.
2. Install Anaconda. (https://www.anaconda.com/distribution/)
3. Install Arduino IDE v1.8.5. (https://www.arduino.cc/en/Main/Software)
	
4. Create and configure a virtual environment for installing the HomeCageSinglePellet code.
	- `conda create -n <yourenvname> python=3.6.10 anaconda`
	- `conda activate <yourenvname>`
	- `conda install -c anaconda numpy==1.18.1`
	- `conda install -c anaconda pyserial==3.4`
	- `conda install -c anaconda tk==8.6.8`
	- `conda install -c conda-forge matplotlib`
	- `conda install tqdm`
	- `conda install Pillow`
	- `conda install tensorflow==1.10.0`
	- `conda install keras==2.2.4`
	- `pip install psutil`
	

5. Make sure you have git install. cd to the folder you want to have HASRA in.
   `git clone https://github.com/SilasiLab/HASRAv2.git`
6. `pip install /path/to/HASRA/dependencies/opencv_python-4.1.2+contrib-cp36-cp36m-win_amd64.whl` or you can just pip install
   opencv with `pip install opencv-python`. Currently we are using opencv v4.4.x
7. Add ID of cage to the name of folder as postfix. (Rename the folder of the downloaded repository as HASRA_[id]).
8. Create folders and profiles of the animals by running the  `genProfiles.py `
	- `conda activate [name of your environment]`
	- `cd /path/to/HASRA/src/client`
	- `python genProfiles.py`
9. If you don't know the RFID tag numbers for your tags you can run the task and scan each tag individually.
   The numbers will be printed to the console. Then you can go to /HASRA_[cage number]/AnimalProfiles/MOUSE1.
   Open up the .txt file in that folder and edit the first line to be the RFID tag number. Do this for each mouse.

# **Software Installation Jetson/ARM:**

1. Put sd card into host machine
2. Make sure the contents of the sd can be deleted… ie back them up on the host machine if you need them or aren’t sure
3. Use disks utility to format sd card
4. https://developer.nvidia.com/jetson-nano-sd-card-image
Download nano sd card image from the nvidia downloads page… link above\
5. $ /usr/bin/unzip -p ~/Downloads/jetson_nano_devkit_sd_card.zip | sudo /bin/dd of=/dev/sd<x> bs=1M status=progress
6. Use your file manager to eject the sd card once the above process is complete
7. Put a jumper on your nano to allow for power from the barrel jack
8. Put in the sd and give your nano power
9. Allocate all the remaining blocks in your sd to your home fs
10. Go through the setup normally… make a user and pw, etc
11. $ sudo apt-get update && apt-get upgrade
12. $ sudo apt install git-all
13. $ git clone https://github.com/silasilab/hasra_jetson.git
14. $ git clone https://github.com/JetsonHacksNano/CSI-Camera.git
15. $ git clone https://github.com/jetsonhacks/jetsonUtilities.git
16. $ sudo -H pip3 install -U jetson-stats
17. Reboot
18. Dont pip install requirements.txt…
	 - $ pip3 install pyserial
	 - $ pip3 install psutil
19.Remove all function calls in main.py that’re dependent on tk
20. $ sudo apt install libcanberra-gtk-module libcanberra-gtk3-module
21. Setup is_running
	- $ cd ~
	- $ vim is_running.sh
	Write: #!/bin/bash
		pgrep -af main.py
22. Put below line in bashrc
	$ alias is_running=’/home/homecage24/is_running.sh’
23. Setup rclone by running and going through the steps:
	$ rclone config
24. Setup cronjobs to run rclone commands to send files to cloud storage
	$ crontab -e


# **Assembly:**

The detailed assembly manual can be found here:
https://github.com/SilasiLab/HomeCageSinglePellet_server/blob/master/Homecage%20assembly%20manual.pdf


# **Usage**:
### **Running the Device**
1. Enter the virtual environment that the system was installed in by typing `conda activate <my_env>` into a terminal.

2. Optional: Use `cd` to navigate to` HASRA_[cage number]/src/client/` and then run `python -B genProfiles.py`. The text prompts will walk you through entering your new animals into the system. Since the folder and the file are already inclued in this repo, this step is optional.

3. Open HASRA_[cage number]/config/config.txt and set the system configuration you want.

4. This step is now optional, as there is a COM port scanner feature in the code now.
   Skip this step for now and come back if the task hangs on startup and the console
   indicates that you should check COM ports.
   
   Find the COM port ids for Arduino and RFID reader, using `mode` command in terminal.
   (In linux: Arduino needs to be USB0 , and RFID reader needs to be USB1. You can see connected USB devices with terminal command:
   ls /dev/tty* and You need to replace the COMs in main.py -> `sys_init()` function manually.) 
  
5. Open a terminal and run following command:
* `cd \your\path\to\HASRA_[cage number]\src\client\`
* `conda activate YourEnvironment` replace YourEnvironment by the name of your environment.
* `python main.py`
   if you want to explicitly pass the COM ports in CLI you can run main.py with the following arguments.
* `python main.py COM-arduino COM-RFID` replace COM-arduino and COM-RFID by the COM ids of Arduino and RFID respectively.


6. Optional: If you have a google file stream mounted on this computer, you can choose to upload all the viedos and log files to google drive. You need firstly find out the local path to this google drive folder, in our case it is: `G:\Shared drives\SilasiLabGdrive`.
Since there could be mutiple cages running on the same computer and they can also be stored in the same google cloud folder. You can add a suffix to the project folder name by changing the root folder name from `HASRA` to `HASRA_[cage number]` 
In the same folder, open another terminal window, activate the virtual environment again (if needed), then run `python googleDriveManager.py \path\to\your\cloud\drive\folder`.
The videos and the log files will be stored in `your cloud drive\homecage_id_sync`.

7. You need to put in the RFID tag numbers manually into the profiles. Take mouse 1 as an instance, you need to replace the first line in `HomeCageSinglePellet_server\AnimalProfiles\MOUSE1\MOUSE1_save.txt`. If you do not know your tag number, don't worry. You can scan it on the RFID reader, it will be printed in the Terminal as `[tag number] not recognized`.

8. To test that everything is running correctly, block the IR beam breaker with something
	and scan one of the system’s test tags. If a session starts properly, it’s working. You will also be able to find out hom many pellets have been succefully displayed out of current displays we have as it is shown in the terminal too. 

9. To shut the system down cleanly; 

	- Ensure no sessions are currently running and that the motors have all moved back to their default positions. 
	- Press the quit button on the GUI.
	- Ctrl+c out of the program running in the terminal.


# **Troubleshooting**:

* Is everything plugged in?
* Make sure you are in the correct virtual environment.
* Make sure the HASRA_[cage number]/config/config.txt file contains the correct configuration. (If the file gets deleted it will be replaced by a default version at system start)
* Make sure there are 1 to 5 profiles in the HASRA_[cage number]/AnimalProfiles/ directory. Ensure these profiles contain all the appropriate files and that the save.txt file for each animal contains the correct information. 
