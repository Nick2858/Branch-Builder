import networkx as nx
import pandas
import pandas as pd



#--------------------IMPORTANT----------------------
#
#set txt file path to extract branch network data
#
#---------------------------------------------------

path = '/Treefile.txt'

#Open txt file and save data to info variable
with open(path, 'r') as data:
    info = list(data.read().splitlines())

#initialize branch network graph with networkx module
bNet = nx.Graph()

#extract nodes
for line in range(len(info)):

    #Find all "NodeID" mentions in document
    if "NodeID" in info[line]:

        #Extract NodeID and coords from lines following NodeID metion
        nodeId = int(info[line].split(":")[-1].replace(" ",""))
        coords = info[line + 1].split("Koord: ")[-1].split(" ")

        #convert coords from string to float
        for coord in range(len(coords)):
            coords[coord] = float(coords[coord])

        #create node object in branching network graph with nodeID identifier and coords attribute
        bNet.add_node(nodeId, coords=coords)

#get list of nodes and their coords
nodeCoords = bNet.nodes.data(data="coords")

#extract edges
for line in range(len(info)):

    #Find all "EdgeID" metions in document
    if "EdgeID" in info[line]:

        #Extract edge parameters from consecutive lines after EdgeID mention
        edgeId = int(info[line].split(":")[-1])
        predID = int(info[line + 1].split(",")[0].split(":")[-1])
        succID = int(info[line + 1].split(",")[-1].split(":")[-1])

        Hiera = int(info[line + 4].split(":")[-1])
        Length = float(info[line + 5].split(":")[-1])
        Volume = float(info[line + 6].split(":")[-1])
        Lobe = int(info[line + 7].split(":")[-1])
        Segment = int(info[line + 8].split(":")[-1])

        x1,y1,z1 = nodeCoords[predID]
        x2,y2,z2 = nodeCoords[succID]

        #Create edge object in branch network graph with source and target as predecessive node and successive node.
        bNet.add_edge(predID, succID, id= edgeId, generation=Hiera, length=Length, volume=Volume, lobe=Lobe, segment=Segment, x1= x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2)


#convert branch network graph to pandas dataframe
df = nx.to_pandas_edgelist(bNet, source="predID", target="succID")

#sort dataframe by id and set index to id
df = df.sort_values(by=["id"], ascending=True)
df = df.set_index(["id"])

#change order of dataframe columns
df =df[["predID", "succID", "generation", "length", "volume", "lobe", "segment", "x1", "y1", "z1", "x2", "y2", "z2"]]

#select which generations to export or select which lobes to export
df2 = df.loc[(df.loc[:, "generation"] >= 0) & (df.loc[:, "generation"] <= 20), :]
#df2 = df.loc[(df.loc[:, "lobe"] >= 0) & (df.loc[:, "lobe"] <= 4), :]

#export csv file of branch network/tree data
df2.to_csv("TreeData.csv", index=True)


