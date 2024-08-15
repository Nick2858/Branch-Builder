import pandas as pd
import sys
import networkx as nx
import numpy as np
import csv

def get_generation(segments, generation = 1):

    print(f"Finding generation {generation}")

    print("Getting start and end points")

    start_data = list(vessel_data.loc[segments, "NodeData1"].unique())
    end_data = list(vessel_data.loc[segments, "NodeData2"].unique())


    data = list(start_data)
    data.extend(list(end_data))


    print("Finding new generation")
    connection_list = []
    connections = vessel_data.loc[(vessel_data.loc[:, "NodeData1"].isin(data)) & (vessel_data.loc[:,"BranchID"].isin(segments) == False) | (vessel_data.loc[:, "NodeData2"].isin(data)) & (vessel_data.loc[:,"BranchID"].isin(segments) == False) ,:]
    connection_list = list(connections.loc[:,"BranchID"])

    print("Adding generation value")
    if connection_list:
        if generation  == 1 and (start_data in list(connections.loc[:,"NodeData1"]) or start_data in list(connections.loc[:,"NodeData2"])):
            vessel_data.loc[startNodeId,"Start1"] = True

        vessel_data.loc[connection_list, "Generation"] = generation
        vessel_data.loc[connection_list, "Start1"] = vessel_data.loc[connection_list,"NodeData2"].isin(data)

        segments.extend(connection_list)
        get_generation(segments, generation + 1)

#path = "F:\Research at UofT\ImageStacks\\Nicholas\\Network properties.csv"
path = "AirwaySegmentData.csv"
vessel_data = pd.read_csv(path, header=None)

vessel_data.rename(columns={0:"Radius", 1: "X1", 2:"Y1", 3:"Z1", 4:"X2", 5:"Y2", 6:"Z2"}, inplace=True)
vessel_data.loc[:,"Start1"] = False

vessel_data.loc[:, "NodeData1"] = vessel_data.iloc[:,1].astype(str) + vessel_data.iloc[:,2].astype(str) + vessel_data.iloc[:,3].astype(str)

vessel_data.loc[:, "NodeData2"] = vessel_data.iloc[:,4].astype(str) + vessel_data.iloc[:,5].astype(str) + vessel_data.iloc[:,6].astype(str)
vessel_data.loc[:,"Generation"] = "NaN"

vessel_data.loc[:, "Generation"].astype(float)
vessel_data.loc[:, "Lobe"] = 0

vessel_data.loc[:,"BranchID"] = vessel_data.index

vessel_data.set_index("BranchID")



startNodeId = 57 #Column number - 1

vessel_data.loc[startNodeId, "Generation"] = 0

get_generation([vessel_data.loc[startNodeId, "BranchID"],],1)

vessel_data = vessel_data[["Generation", "Lobe", "Radius", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "Start1"]]

print("\n\nFixing Orientation")

XYZ1 = vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), ["X1", "Y1", "Z1"]]
XYZ2 = vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), ["X2", "Y2", "Z2"]]

vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "X1"] = XYZ2["X2"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Y1"] = XYZ2["Y2"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Z1"] = XYZ2["Z2"]

vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "X2"] = XYZ1["X1"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Y2"] = XYZ1["Y1"]
vessel_data.loc[(vessel_data.loc[:,"Start1"] == True), "Z2"] = XYZ1["Z1"]

vessel_data = vessel_data[["Generation", "Lobe", "Radius", "X1", "Y1", "Z1", "X2", "Y2", "Z2"]]

vessel_data = vessel_data.loc[vessel_data.loc[:,"Generation"] != "NaN", :]

vessel_data = vessel_data.sort_values(by="Generation", ascending=True)

print("Exporting to csv file")


vessel_data.to_csv("NetData.csv")
