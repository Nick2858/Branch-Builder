# BRANCH BUILDER

This repository contains the code for a Blender script that creates hollow branching network objects for use as geometries in CFD. It works by reading a CSV file of the branch data. Each branch is represented by a row in the CSV file. The model approximates branches as straight, hollow, cylinders with hollow spheres at each bifurcation point and the ends of terminal branches. The code was made to work with Blender 4.2, other versions may not be compatible.

## Demo Airway Model
<div align="center" margin-top = "">
  <img src="Images/buildGenAnimation.gif" alt="drawing" width="500"/>
  <p>Rendering of 17 Generation Digital Reference Model of the Human Bronchial Tree from Schmidt et al 2004</p>
</div>

Using airway data from Schmidt et al 2004 (accessible here: https://simtk.org/projects/lungsim) we were able to extract data from the `Demo/Treefile.txt` into the CSV file `Demo/TreeData.csv` with the custom `Demo\TXTtoCSV.py` script. From there, the CSV file data could be imported into the `blenderInterface.py` file running in Blender's **scripting** section to build the airway branching network.

## Setup

### Step 1
The first step in setting up this program to build a branch network is downloading the `blenderInterface.py` code. Once it's been downloaded, it can be opened in Blender.


### Step 2
The next step is to toggle on the System Console in Blender. This will allow you to monitor the program's progress, which will print information about what steps it's on while running. Blender does not respond when scripts are running, this is the only way to monitor that the program is working.


<img src="Images/SetupConsole.png" alt="drawing" width="800"/>

### Step 3
Before running the Python script, some settings must be adjusted. These settings can be found in the script and are displayed below. The `max_gen` variable holds an integer value of the maximum generation number the program will extract from the CSV file and build. The `path` variable holds a string value for the path to the CSV file containing the network data. The `stl_path` variable holds the string value for the path where you wish for the STL files to be exported.

<img src="Images/ChangeSettings.png" alt="drawing" width="400"/>

After configuring these settings, the program can be run in Blender here:




