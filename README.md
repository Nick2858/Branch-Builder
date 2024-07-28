# BRANCH BUILDER

This repository contains the code for a blender script that creates hollow branching network objects for use as geometries in CFD. It works by reading a CSV file of the branch data. Each branch is represented by a row in the CSV file. The model approximates branches as straight, hollow, and cylindrical with hollow spheres at each bifurcation point and the ends of terminal branches. 

<div align="center" margin-top = "">
  <h3> Demo Airway Model</h3>
  <img src="Images/buildGenAnimation.gif" alt="drawing" width="500" margin-top = "100px"/>
  <p>Rendering of 17 Generations Digital Reference Model of the Human Bronchial Tree from Schmidt et al 2004</p>
</div>

Using airway data from Schmidt et al 2004 (accessible here: https://simtk.org/projects/lungsim) we were able to extract data from the `Demo/Treefile.txt` into the CSV file `Demo/TreeData.csv` using the custom `Demo\TXTtoCSV.py` script. From there, the CSV file data could be imported into the `blenderInterface.py` file running in blender's script section to build the airway branching network.


