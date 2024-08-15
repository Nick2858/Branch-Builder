import pandas as pd
import sys
import networkx as nx
import numpy as np
import csv

def get_generation(segments, generation = 1):
    """
    (list, int) --> None

    This is a recursive function which takes a list of parent branches and finds all the child branches that connect
    to it and assigns them with their respective generation number based on the generation number of their parents. This
    function runs until there are no more connecting child branches.
    """
    print(f"Finding generation {generation}")

    print("Getting start and end points")

    #Get all start and end coordinates of all branches in the segment list
    start_data = list(vessel_data.loc[segments, "NodeData1"].unique())
    end_data = list(vessel_data.loc[segments, "NodeData2"].unique())

    data = list(start_data)
    data.extend(list(end_data))


    print("Finding new generation")

    connection_list = []

    #Find all branches connected to the start and end coords which aren't assigned a generation number
    connections = vessel_data.loc[(vessel_data.loc[:, "NodeData1"].isin(data)) & (vessel_data.loc[:,"BranchID"].isin(segments) == False) | (vessel_data.loc[:, "NodeData2"].isin(data)) & (vessel_data.loc[:,"BranchID"].isin(segments) == False) ,:]
    connection_list = list(connections.loc[:,"BranchID"])

    print("Adding generation value")

    #if there are connections, run otherwise there are no connects and the recursive function will stop running
    if connection_list:
        #Assign the orientation of the first branch based on which coords its child branches connect to
        if generation  == 1 and (start_data in list(connections.loc[:,"NodeData1"]) or start_data in list(connections.loc[:,"NodeData2"])):
            vessel_data.loc[genZeroBranch, "Start1"] = True

        #Assign generation number to child branches and assign orientation of branch using Start1 column value
        vessel_data.loc[connection_list, "Generation"] = generation
        vessel_data.loc[connection_list, "Start1"] = vessel_data.loc[connection_list,"NodeData2"].isin(data)

        #Append new connections to the segment list
        segments.extend(connection_list)

        #Run the function to find the next generation of branches
        get_generation(segments, generation + 1)


#--------------------IMPORTANT----------------------
#
#set path of CSV Branch Data File
#
#---------------------------------------------------

path = "AirwaySegmentData.csv"

#--------------------IMPORTANT----------------------
#
#Enter the CSV Column Number of your Starting Branch
#
#---------------------------------------------------

genZeroBranch = 57

#--------------------IMPORTANT----------------------
#
#Enter the name for the output CSV File
#
#---------------------------------------------------

outputName = "NetData.csv"



#Column number - 1 because the CSV index starts at 1 but pandas dataframe index starts at 0
genZeroBranch -= 1 

#Read CSV File
vessel_data = pd.read_csv(path, header=None)

#Rename Headers
vessel_data.rename(columns={0:"Radius", 1: "X1", 2:"Y1", 3:"Z1", 4:"X2", 5:"Y2", 6:"Z2"}, inplace=True)
vessel_data.loc[:,"Start1"] = False

#Create temporary columns which store coordinates as string to make searching dataframe for equal coords easier
vessel_data.loc[:, "NodeData1"] = vessel_data.iloc[:,1].astype(str) + vessel_data.iloc[:,2].astype(str) + vessel_data.iloc[:,3].astype(str)
vessel_data.loc[:, "NodeData2"] = vessel_data.iloc[:,4].astype(str) + vessel_data.iloc[:,5].astype(str) + vessel_data.iloc[:,6].astype(str)

#Initialize column for storing generation number
vessel_data.loc[:,"Generation"] = "NaN"
vessel_data.loc[:, "Generation"].astype(float)

#Initialize lobe number (the MATLAB Code doesn't give us information on lobe number but it is required for the
#Branch Builder tool)
vessel_data.loc[:, "Lobe"] = 0

#Initialize the BranchID column and make it the index
vessel_data.loc[:,"BranchID"] = vessel_data.index
vessel_data.set_index("BranchID")

#Set the generation number of the starting branch to 0
vessel_data.loc[genZeroBranch, "Generation"] = 0

#Start calculating the generation number using the recursive gen_generation function
get_generation([vessel_data.loc[genZeroBranch, "BranchID"], ], 1)

#Reorder the dataframe
vessel_data = vessel_data[["Generation", "Lobe", "Radius", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "Start1"]]


#Fix the orientation so that XYZ1 coords connect to the parent branch and XYZ2 coords connect to the child branch
print("\n\nFixing Orientation")

XYZ1 = vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), ["X1", "Y1", "Z1"]]
XYZ2 = vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), ["X2", "Y2", "Z2"]]

vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "X1"] = XYZ2["X2"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Y1"] = XYZ2["Y2"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Z1"] = XYZ2["Z2"]

vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "X2"] = XYZ1["X1"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Y2"] = XYZ1["Y1"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Z2"] = XYZ1["Z1"]

#Remove the Start1 column
vessel_data = vessel_data[["Generation", "Lobe", "Radius", "X1", "Y1", "Z1", "X2", "Y2", "Z2"]]

#Remove branches that were not assigned a generation number (they are not conected to main branch network)
vessel_data = vessel_data.loc[vessel_data.loc[:,"Generation"] != "NaN", :]

#Sort dataframe by generation number
vessel_data = vessel_data.sort_values(by="Generation", ascending=True)

print("Exporting to csv file")

#Export dataframe to CSV File
vessel_data.to_csv(outputName)
