import bpy
import math
import csv
import math
import mathutils
import time
import datetime
import os


class BranchFileInfo:
    """
    This object storse information read from a branch file in the directory where it was exported to.
    It is used in the process of grouping branches by generation and lobe.
    """

    def __init__(self, name):
        """
        (BranchFileInfo, str) -> None

        The name variable is the name of the branch file. It is used to extract data about the branch id,
        generation number and lobe number.
        """

        self.name = name.split(".")[0]
        self.id = int(((self.name.split("G"))[0]).replace("B", ""))
        self.gen = int((self.name.split("G")[1]).split("L")[0])
        self.lobe = int(self.name.split("L")[-1])


class Branch:
    """
    This class is used to build the branch objects in blender. Branches are made from cylinders and spheres.
    """

    def __init__(self, rowData):
        """
        (object, [float,float,...]) -> Branch object

        The rowData variable contains the following information in this order:
        [id,predID,succID,generation,length,volume,lobe,segment,x1,y1,z1,x2,y2,z2]

        id is the edge/branch id,
        parentID is the previous/parent node/bifurcation id,
        childID is the successive/child node/bifurcation id,
        generation is the generation number of the branch
        length is the length of the branch
        volume is the volume of the branch
        lobe is the lobe number of the branch
        x1,y1,z1 are the coordinates of the predID node
        x2,y2,z2 are the coordinates of the succID node
        """

        self.id, self.parentID, self.childID, self.generation, self.length, self.volume, self.lobe, self.segment = rowData[
                                                                                                                :8]
        self.xyz1 = rowData[8:11]
        self.xyz2 = rowData[11:14]

        # location is center of the cylinder, thus we calculate the average of the previous and successive node coords
        self.location = [(self.xyz1[0] + self.xyz2[0]) / 2, (self.xyz1[1] + self.xyz2[1]) / 2,
                         (self.xyz1[2] + self.xyz2[2]) / 2]

        # vector calculated from predID - succID nodes and converted to mathutils.Vector object for functionality
        self.vector = mathutils.Vector(
            [(self.xyz2[0] - self.xyz1[0]), (self.xyz2[1] - self.xyz1[1]),
             (self.xyz2[2] - self.xyz1[2])])

        # calculate radius of cylinder from volume and length
        self.radius = math.sqrt(self.volume / (self.length * math.pi))

        # set rotation of cylinder using mathutils vector functionality to convert vec to angle
        up_axis = mathutils.Vector([0.0, 0.0, 1.0])
        angle = self.vector.angle(up_axis, 0)
        axis = up_axis.cross(self.vector)
        self.euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()

        self.hollow_rad = 0.1

    def make_branch(self):
        """
        This method is used to build the cylindrical branch 3D object in blender with the given cylinder parameters.
        This blender mesh object is saved to self.cylinder and is named by it's branch id.
        """

        # create a cylinder object in blender using initialized parameters
        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.radius, depth=self.length, rotation=self.euler)

        # assign cylinder object to Branch object and name it based on it's branch (b) id.
        self.cylinder = bpy.context.active_object
        self.cylinder.name = f"b:{self.id}"
        self.cylinder_name = self.cylinder.name

    def make_sphere(self):
        """
        This method is used to build the ends of each branch which is represented by a spherical object in blender
        using the radius, rotation, and location of its parent branch. It is named by it's node id.

        """
        # create sphere object in blender using initialized parameters
        # each branch is the parent to the sphere/node at it's successive node location
        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1), rotation=self.euler)

        # assign sphere object to Branch object and name it based on it's node (s - for sphere) id.
        self.sphere = bpy.context.active_object
        self.sphere.name = f"s:{self.childID}"
        self.sphere_name = self.sphere.name

    def clean(self):
        """
        This method is used to clean the branches by removing any overlap from other neighboring branches.
        """
        #Set up variables to store neighbors.
        parentConnection = "" #Bifurcation model has only one parent branch
        siblingConnection = "" #Bifurcation model has only one sibling branch
        childConnections = [] #Bifurcation model either 2 or 0 child branches.

        #Find branch connections
        for b in branchList:
            if b.id != self.id:

                #Find branches which connect as children of the branch.
                if b.parentID == self.childID: #The parentID of a branch is the childID of the parent branch.
                    childConnections.append(b)

                #Find the parent connection of the branch.
                if b.childID == self.parentID: #The childID of a branch is the parentID of the child branch.
                    parentConnection = b

                #Find the sibling connection of the branch.
                if b.parentID == self.parentID: #Siblings share parentID
                    siblingConnection = b

        #For the parent connection, both cylinder and sphere of the parent branch must not overlap with the cylinder
        #of the branch
        if parentConnection:
            parentConnection.make_branch()
            parentConnection.make_sphere()
            carver(self.cylinder, parentConnection.sphere)
            carver(self.cylinder, parentConnection.cylinder)

        #For the sibling connection, the cylinders of both branches must not overlap.
        if siblingConnection:
            siblingConnection.make_branch()
            carver(self.cylinder, siblingConnection.cylinder)

        #For child connections, the cylinder and sphere must not overlap with the child branch's cylinder.
        for child in childConnections:
            child.make_branch()
            carver(self.cylinder, child.cylinder, False)
            carver(self.sphere, child.cylinder)

    def hollow(self):
        """
        This method is used to hollow out the branch object into tubes to use in CFD.
        """

        # Build replica cylinder with smaller radius assigned to self.hollow_branch
        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.radius - self.hollow_rad, depth=self.length * 2,
                                            rotation=self.euler)
        self.hollow_branch = bpy.context.active_object

        # carve the hollow_branch object out of the cylinder using the carver function
        carver(self.cylinder, self.hollow_branch, False)

        #Set the dimensions of the hollow_branch to match the dimensions of the cylinder
        self.hollow_branch.dimensions = (2 * self.radius, 2 * self.radius, self.length)

        #Carve the hollow_branch object out of the sphere using the carver function
        carver(self.sphere, self.hollow_branch)

        # Build replica sphere with smaller radius assigned to self.hollow_sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius - self.hollow_rad, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1), rotation=self.euler)
        self.hollow_sphere = bpy.context.active_object

        # carve the hollow_sphere object out of the sphere using the carver function
        carver(self.sphere, self.hollow_sphere)

    def finalize(self):
        """
        This method is used to finalize the branch.
        First it unites the branch with its child sphere.
        Then it renames the branch to include information about the branch id, generation and lob numbers.
        """

        # Unite cylinder with sphere using the join tool
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self.cylinder
        self.cylinder.select_set(True)
        self.sphere.select_set(True)
        bpy.ops.object.join()
        bpy.ops.object.select_all(action='DESELECT')

        # Rename the branch object (saved to self.cylinder) to include branch id, generation and lob info.
        self.cylinder.name = f"B{int(self.id)}G{int(self.generation)}L{int(self.lobe)}"

        self.name = self.cylinder.name

    def export(self):
        """
        This method is used to export the branch object
        """

        #Export the branch object as it's finalized name which stores info about the branch ID, generation number
        #and lobe number
        bpy.ops.wm.stl_export(filepath=f"{stl_path}\\{self.name}.stl")

        #Delete the object once you are done exporting it, to save resources for the next object
        deleter(self.cylinder)

    def build_branch(self):
        """
        This method is used to build the branch object by calling other methods in order to build, clean, hollow,
        finalize and export the branch object.
        """
        id = int(self.id)

        self.make_branch()
        self.make_sphere()
        print(f"CLEANING BRANCH {id}")
        self.clean()
        print(f"HOLLOWING BRANCH {id}")
        self.hollow()
        print(f"FINALIZING BRANCH {id}")
        self.finalize()
        print(f"EXPORTING BRANCH AS {self.name}")
        self.export()


def carver(obj1, obj2, delete=True):
    """
    (Branch object, Branch object, bool) -> None

    This function is used to remove overlap between objects.
    Object 1 (obj1) is modified using the boolean difference solver to remove parts of object 1 that overlap
    with object 2 (obj2).

    Object 2 is set to automatically be deleted as in most cases object 2 is a duplicate of a branch object.
    However, sometimes it is necessary to keep object 2 the function accounted for those cases.
    """
    # Carve out areas of object 1 that intersect with object 2
    # must use exact solver and use_self=True solver option to properly carve objects.
    bpy.context.view_layer.objects.active = obj1
    bool_one = obj1.modifiers.new(type="BOOLEAN", name="bool 1")
    bool_one.object = obj2
    bool_one.operation = "DIFFERENCE"
    bool_one.solver = "EXACT"
    bool_one.use_self = True

    # Convert object 1 to mesh to apply modifiers (this is a little hack to apply modifiers,
    # it's already a mesh in blender)
    bpy.ops.object.select_all(action="DESELECT")
    obj1.select_set(True)
    bpy.ops.object.convert(target='MESH', keep_original=False)

    # delete object 2 unless delete = False is passed.
    if delete:
        deleter(obj2)


def groupGen(bList, genList):
    """
    ([Branch object, Branch object, ...], set(int,int,int,...) -> None

    This function is used to read branch files in the directory they were exported to and group them into
    stl objects for each generation.
    """

    print(f"GROUPING BY GENERATION")

    #Set up directory/folder for GEN object files
    genPath = f"{stl_path}\\GEN"
    if not os.path.exists(genPath):
        os.makedirs(genPath)

    #Build each generation object
    for gen in genList:
        print(f'Building Gen:{gen}')

        #Import and join all the branch files of the specified generation number
        for b in bList:
            if b.gen == gen:
                bpy.ops.wm.stl_import(filepath=f"{stl_path}\\{b.name}.stl")

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.join()
                bpy.ops.object.select_all(action='DESELECT')

        #Export the new generation object into the GEN directory
        bpy.ops.wm.stl_export(filepath=f"{genPath}\\GEN{gen}.stl")

        #Delete all objects
        delete_all()


def groupLobe(bList, lobeList):
    """
    ([Branch object, Branch object, ...], set(int,int,int,...) -> None

    This function is used to read branch files in the directory they were exported to and group them into
    stl objects for each lobe.
    """

    print(f"GROUPING BY LOBE")

    #Set up directory/folder for LOBE object files
    lobePath = f"{stl_path}\\LOBE"
    if not os.path.exists(lobePath):
        os.makedirs(lobePath)

    #Build each lobe object
    for lobe in lobeList:
        print(f'Building Lobe:{lobe}')

        #Import and join all the branch files of the specified lobe number
        for b in bList:
            if b.lobe == lobe:
                bpy.ops.wm.stl_import(filepath=f"{stl_path}\\{b.name}.stl")

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.join()
                bpy.ops.object.select_all(action='DESELECT')

        #Export the new lobe object into the LOBE directory
        bpy.ops.wm.stl_export(filepath=f"{lobePath}\\LOBE{lobe}.stl")

        #Delete all objects
        delete_all()


def delete_all():
    """
    (Branch object) -> None

    This function is used to delete all objects in blender.
    """

    #Sselect all objects, delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')


def deleter(obj):
    """
    (Branch object) -> None

    This function is used to delete the object that is passed to it in blender.
    """

    # Deselect all objects, then select the object you wish to delete, delete it and then deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')


def groupData():
    """
    This function is used to group the branch files into objects based on generation number and lobe number 
    """
    print(f"--------GROUPING BRANGES--------")

    #get all branch names from the directory they were exported into
    branches = os.listdir(stl_path)
    
    bList = [] #initalize a list to store branch data
    genList = set() #Initialize the set of all unique generation numbers from the branch data
    lobeList = set() #Initialize the set of all unique lobe numbers from the branch data

    #Extract the branch info for all the branch files in the directory they were exported to
    for branch in branches:
        #Filter out non stl files
        if ".stl" in branch:
            #create branch info object
            b = BranchFileInfo(branch)
            bList.append(b)
            
            #add gen number and lobe number to the list of gen and lobe numbers
            genList.add(b.gen)
            lobeList.add(b.lobe)
    
    #Run the groupGen and groupLobe functions to export grouped objects
    groupGen(bList, genList)
    groupLobe(bList, lobeList)

#Start the timer for when the code starts running
start = time.time()

# --------------------IMPORTANT----------------------
#
# set maximum generation number to create in blender
#
# ---------------------------------------------------

max_gen = 20

# --------------------IMPORTANT----------------------
#
# set csv file path to extract branch network data
#
# ---------------------------------------------------

path = "\\TreeData.csv"

# --------------------IMPORTANT----------------------
#
# set STL file export location
#
# ---------------------------------------------------


stl_path = f"\\AirwayModel"

# initialize variables for storing list of branch objects (branchList),
# and dictionary of objects at nodes (touchingBranches)
branchList = []

print("--------READING CSV FILE--------")

# read the csv file
with open(path, "r", newline='') as data:
    info = csv.reader(data)
    header = next(info)

    print("--------MAKING BRANCHES--------")
    # each row in (info) list stores data for each edge

    #Initialize number of branch being built
    branchIter = 0
    for row in info:
        
        #increase iteration number with every iteration
        branchIter += 1
        
        #initialize rowData variable
        rowData = []

        # convert row data to float type
        for elm in row:
            rowData.append(float(elm))

        # check if branch is in generation range
        if rowData[3] <= max_gen:
            # initialize branch object using row data (data for one edge)
            b = Branch(rowData)

            # append branch object to branch list for use later.
            branchList.append(b)

#Get number of branches in branch list
num = len(branchList)

#for branch in list, build the branch file
iter = 1
for b in branchList:
    print(f"--------BUILDING BRANCH ID:{int(b.id)} ({iter}/{num})--------")
    b.build_branch()
    iter += 1

#stop the stopwatch
end = time.time()

#convert time in seconds to hours/minutes/seconds and print completion time
stopwatch = datetime.timedelta(seconds=(end - start))
print(f"\n\nCOMPLETED BUILDING {num} BRANCHES IN: {stopwatch}\n\n")

#Start the group data function to export grouped branch files
groupData()

#Find when grouping is completed
end2 = time.time()

#convert time in seconds to hours/minutes/seconds
stopwatch2 = datetime.timedelta(seconds=(end2 - start))
stopwatch3 = datetime.timedelta(seconds=(end2 - end))

#print time to complete building branch files and time to export files
print(f"\n\nCOMPLETED BUILDING {num} BRANCHES IN: {stopwatch}\n\n")
print(f"\n\nCOMPLETED EXPORTING {num} BRANCHES IN: {stopwatch3}\n\n")

#print full code runtime
print(f"\n\nCODE FINISHED IN: {stopwatch2}\n\n")
