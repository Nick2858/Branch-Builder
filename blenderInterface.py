import bpy
import math
import csv
import math
import mathutils


class Branch:
    """
    This class is used to build the branch objects in blender. Branches are made from cylinders and spheres.
    """

    def __init__(self, rowData):
        """
        (object, [float,float,...]) -> Branch object

        The rowData variable contains the following information in this order:
        [id,predID,succID,generation,length,volume,lobe,segment,x1,y1,z1,x2,y2,z2]

        where id is the edge id,
        predID is the previous node id,
        succID is the successive node id,
        generation is the generation number of the branch
        length is the length of the branch
        volume is the volume of the branch
        lobe is the lobe number of the branch
        x1,y1,z1 are the coordinates of the predID node
        x2,y2,z2 are the coordinates of the succID node
        """

        self.id, self.predID, self.succID, self.generation, self.length, self.volume, self.lobe, self.segment = rowData[
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

    def make_branch(self):
        # create a cylinder object in blender using initialized parameters
        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.radius, depth=self.length)

        # assign cylinder object to Branch object and name it based on it's branch (b) id.
        self.cylinder = bpy.context.active_object
        self.cylinder.name = f"b:{self.id}"

        # set rotation of cylinder using mathutils vector functionality to convert vec to angle
        up_axis = mathutils.Vector([0.0, 0.0, 1.0])
        angle = self.vector.angle(up_axis, 0)
        axis = up_axis.cross(self.vector)
        self.euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()
        self.cylinder.rotation_euler = self.euler

        # create sphere object in blender using initialized parameters
        # each branch is the parent to the sphere/node at it's successive node location
        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1))

        # assign sphere object to Branch object and name it based on it's node (s - for sphere) id.
        self.sphere = bpy.context.active_object
        self.sphere.name = f"s:{self.succID}"

    def hollow(self):
        """
        This function is used to hollow out the branch object into tubes to use in CFD.
        """

        # Build replica cylinder with smaller radius assigned to self.hollow_branch
        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.radius * 0.99, depth=self.length * 2, rotation=self.euler)
        self.hollow_branch = bpy.context.active_object

        # carve the hollow_branch object out of the cylinder using the carver function
        carver(self.cylinder, self.hollow_branch)

        # Build replica sphere with smaller radius assigned to self.hollow_sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius * 0.99, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1))
        self.hollow_sphere = bpy.context.active_object

        # carve the hollow_sphere object out of the sphere using the carver function
        carver(self.sphere, self.hollow_sphere)

    def finalize(self):
        """
        This function is used to finalize the branch.
        First it unites the branch with it's child sphere using the boolean union modifier in blender.
        Then it renames the branch to include information about the branch id, generation and lob numbers.
        """

        # Unite cylinder with sphere using boolean union
        # must use exact solver and use_self solver option to properly unite objects.
        bpy.context.view_layer.objects.active = self.cylinder
        bool_one = self.cylinder.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = self.sphere
        bool_one.operation = "UNION"
        bool_one.solver = "EXACT"
        bool_one.use_self = True

        # Convert mesh to mesh to apply modifiers (this is a little hack to apply modifiers)
        bpy.ops.object.select_all(action="DESELECT")
        self.cylinder.select_set(True)
        bpy.ops.object.convert(target='MESH', keep_original=False)

        # Rename the branch object (saved to self.cylinder) to include branch id, generation and lob info.
        self.cylinder.name = f"Branch:{self.id} Gen:{self.generation} Lobe:{self.lobe}"

        # Use deleter function to delete sphere object which is duplicated after union.
        deleter(self.sphere)


def carver(obj1, obj2, delete=True):
    """
    (Branch object, Branch object, bool) -> None

    This function is used to remove overlap between objects.
    Object 1 (obj1) is modified using the boolean difference solver to remove parts of object 1 that overlap
    with object 2 (obj2).

    Object 2 is set to automatically be deleted as in most cases object 2 is a duplicate of a branch object.
    However, for future applications, I included functionality to leave object 2.
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


def clean():
    """
    This function iterates through a dictionary of nodes that have edge ID values of their connecting edges assigned to
    them. It goes through all the objects that share a node and removes all overlap.
    """

    # Iterate over each node (represented as sphere) which contains list of branches connected to it.
    for sphere, branches in touchingBranches.items():

        # rename sphere and branches to their object names in blender.
        sphere = f"s:{sphere}"
        for branch in range(len(branches)):
            branches[branch] = f"b:{branches[branch]}"

        # append sphere to branches list so all objects at the node are included in the list.
        branches.append(sphere)
        branches = branches[::-1]

        # Nested for loop to find the object1 for get carved and object 2 for carving with.
        for name1 in branches:
            for name2 in branches:

                # make sure that objects different for carving.
                if name2 != name1:

                    # Find object 2 in blender object data.
                    for obj in bpy.data.objects:
                        if obj.name == name2:

                            # check if object is a sphere
                            if "s" in name2:

                                # get sphere data from it's parent branch using self.sphere.name
                                for b in branchList:
                                    if b.sphere.name == name2:
                                        shape = b
                                        break

                                # build replica sphere using sphere parameters from (shape) object clone
                                bpy.ops.mesh.primitive_uv_sphere_add(radius=shape.radius, enter_editmode=False,
                                                                     align='WORLD',
                                                                     location=(shape.xyz2), scale=(1, 1, 1))

                            # otherwise object is a cylinder
                            else:
                                for b in branchList:
                                    if b.cylinder.name == name2:
                                        shape = b
                                        break

                                # build replica cylinder using cylinder parameters from (shape) object clone.
                                bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD',
                                                                    location=(shape.location),
                                                                    radius=shape.radius, depth=shape.length,
                                                                    rotation=shape.euler)
                            # asign replica object to obj2
                            obj2 = bpy.context.active_object
                            break

                    # get object 1
                    for obj in bpy.data.objects:
                        if obj.name == name1:
                            obj1 = obj
                            obj1.select_set(True)

                    # carve object 1 using object 2 (replica object)
                    carver(obj1, obj2)


# --------------------IMPORTANT----------------------
#
# set maximum generation number to create in blender
#
# ---------------------------------------------------

max_gen = 3

# --------------------IMPORTANT----------------------
#
# set csv file path to extract branch network data
#
# ---------------------------------------------------

path = "TreeData.csv"

# initialize variables for storing list of branch objects (branchList),
# and dictionary of objects at nodes (touchingBranches)
branchList = []
touchingBranches = {}

# read the csv file
with open(path, "r", newline='') as data:
    info = csv.reader(data)
    header = next(info)

    # each row in (info) list stores data for each edge
    for row in info:
        rowData = []

        # convert row data to float type
        for elm in row:
            rowData.append(float(elm))

        # check if branch is in generation range
        if rowData[3] <= max_gen:
            # build touchingBranch dictionary, ignoring first node which is the inflow.
            if rowData[1] != 0:
                if rowData[1] not in touchingBranches:
                    touchingBranches[rowData[1]] = [rowData[0], ]
                else:
                    touchingBranches[rowData[1]].append(rowData[0])
            if rowData[2] not in touchingBranches:
                touchingBranches[rowData[2]] = [rowData[0], ]
            else:
                touchingBranches[rowData[2]].append(rowData[0])

            # initialize branch object using row data (data for one edge)
            b = Branch(rowData)

            # build a branch object in blender
            b.make_branch()

            # append branch object to branch list for use later.
            branchList.append(b)

# Use clean function to remove overlap in branch objects
clean()

# Hollow out each branch (cylinder and sphere) and unite the cylinder and sphere, rename branch to include
# branch info in name (branch id, generation number and lobe number)
for branch in branchList:
    branch.hollow()
    branch.finalize()
