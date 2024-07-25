import bpy
import math
import csv
import math
import mathutils


class Branch:
    def __init__(self, rowData):
        self.id, self.predID, self.succID, self.generation, self.length, self.volume, self.lobe, self.segment = rowData[
                                                                                                                :8]
        self.xyz1 = rowData[8:11]
        self.xyz2 = rowData[11:14]
        self.orient = rowData[-1]
        self.location = [(self.xyz1[0] + self.xyz2[0]) / 2, (self.xyz1[1] + self.xyz2[1]) / 2,
                         (self.xyz1[2] + self.xyz2[2]) / 2]

        self.orient = 1

        self.vector = mathutils.Vector(
            [(self.xyz2[0] - self.xyz1[0]) * self.orient, (self.xyz2[1] - self.xyz1[1]) * self.orient,
             (self.xyz2[2] - self.xyz1[2]) * self.orient])

        self.diameter = math.sqrt(self.volume / (self.length * math.pi))

    def make_cylinder(self):
        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.diameter, depth=self.length)

        self.ob = bpy.context.active_object  # the newly added cylinder.

        self.ob.name = f"b:{self.id}"

        # ob.dimensions = self.diameter, self.diameter, self.length

        up_axis = mathutils.Vector([0.0, 0.0, 1.0])
        angle = self.vector.angle(up_axis, 0)
        axis = up_axis.cross(self.vector)
        self.euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()

        self.ob.rotation_euler = self.euler

        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.diameter * 1, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1))
        self.ob2 = bpy.context.active_object
        self.ob2.name = f"s:{self.succID}"

    def hollow_branch(self):

        bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD', location=(self.location),
                                            radius=self.diameter * 0.90, depth=self.length * 2, rotation=self.euler)

        self.hollow_branch = bpy.context.active_object

        self.hollow_branch.name = "branch hollower"

        bpy.context.view_layer.objects.active = self.ob

        bool_one = self.ob.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = self.hollow_branch
        bool_one.operation = 'DIFFERENCE'
        bool_one.solver = 'FAST'

        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.data.objects:
            if obj.name == self.ob.name:
                obj.select_set(True)

        bpy.ops.object.convert(target='MESH', keep_original=False)

        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.data.objects:
            if obj.name == self.hollow_branch.name:
                obj.select_set(True)

        bpy.ops.object.delete()

        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.diameter * 0.9, enter_editmode=False, align='WORLD',
                                             location=(self.xyz2), scale=(1, 1, 1))

        self.hollower = bpy.context.active_object
        self.hollower.name = "hollower"

        bpy.context.view_layer.objects.active = self.ob2

        bool_one = self.ob2.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = self.hollower
        bool_one.operation = 'DIFFERENCE'
        bool_one.solver = 'FAST'

        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.data.objects:
            if obj.name == self.ob2.name:
                obj.select_set(True)

        bpy.ops.object.convert(target='MESH', keep_original=False)

        bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.data.objects:
            if obj.name == self.hollower.name:
                obj.select_set(True)

        bpy.ops.object.delete()

    def final_branch(self):
        bpy.context.view_layer.objects.active = self.ob
        bool_one = self.ob.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = self.ob2
        bool_one.operation = "UNION"
        bool_one.solver = "EXACT"
        bool_one.use_self = True

        bpy.ops.object.select_all(action="DESELECT")
        self.ob.select_set(True)
        bpy.ops.object.convert(target='MESH', keep_original=False)

        self.ob.name = f"Branch:{self.id} Gen:{self.generation} Lobe:{self.lobe}"

        bpy.ops.object.duplicate()
        self.copy = bpy.context.active_object
        self.copy.name = f"COPY:{self.id}"

        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.ob2.select_set(True)
        bpy.ops.object.delete()
        bpy.ops.object.select_all(action='DESELECT')


def carver(ob1, ob2):
    bpy.context.view_layer.objects.active = ob1
    bool_one = ob1.modifiers.new(type="BOOLEAN", name="bool 1")
    bool_one.object = ob2
    bool_one.operation = "DIFFERENCE"
    bool_one.solver = "EXACT"
    bool_one.use_self = True

    bpy.ops.object.select_all(action="DESELECT")
    ob1.select_set(True)
    bpy.ops.object.convert(target='MESH', keep_original=False)


def clean_branches():
    for sphere, branches in touchingBranches.items():
        sphere = f"s:{sphere}"

        # branches.append(sphere)
        branches = branches[::-1]
        for name1 in branches:
            for name2 in branches:
                if name2 != name1:
                    for obj in bpy.data.objects:
                        if obj.name == name2:
                            if "s" in name2:
                                shape = 0
                                for b in branchList:
                                    if b.ob2.name == name2:
                                        shape = b

                                bpy.ops.mesh.primitive_uv_sphere_add(radius=shape.diameter, enter_editmode=False,
                                                                     align='WORLD',
                                                                     location=(shape.xyz2), scale=(1, 1, 1))

                                obj2 = bpy.context.active_object
                            else:
                                shape = 0
                                for b in branchList:
                                    if b.ob.name == name2:
                                        shape = b

                                bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD',
                                                                    location=(shape.location),
                                                                    radius=shape.diameter, depth=shape.length,
                                                                    rotation=shape.euler)

                                obj2 = bpy.context.active_object

                    for obj in bpy.data.objects:
                        if obj.name == name1:
                            obj1 = obj
                            obj1.select_set(True)

                    carver(obj1, obj2)


def clean_spheres():
    for sphere, branches in touchingBranches.items():

        branchID = branches
        sphere = f"s:{sphere}"

        # branches.append(sphere)

        for branch in branches:
            for obj in bpy.data.objects:
                if obj.name == sphere:
                    obj1 = obj
                    shape = 0
                    for b in branchList:
                        if b.ob2.name == sphere:
                            shape = b

                    bpy.ops.mesh.primitive_uv_sphere_add(radius=shape.diameter, enter_editmode=False,
                                                         align='WORLD',
                                                         location=(shape.xyz2), scale=(1, 1, 1))

                    sphereShape = bpy.context.active_object
                    sphereShape.name = "sphere1"

            for obj in bpy.data.objects:
                if obj.name == branch:
                    obj2 = obj
                    shape = 0

                    for b in branchList:
                        if b.ob.name == branch:
                            shape = b

                    bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False, align='WORLD',
                                                        location=(shape.location),
                                                        radius=shape.diameter, depth=shape.length,
                                                        rotation=shape.euler)

                    cylShape = bpy.context.active_object
                    cylShape.name = "cylinder1"

            carver(obj1, cylShape)
            if sphere != f"s:{shape.succID}":
                carver(obj2, sphereShape)
            else:
                bpy.ops.object.select_all(action='DESELECT')
                sphereShape.select_set(True)
                bpy.ops.object.delete()
                bpy.ops.object.select_all(action='DESELECT')


def clean():
    for branches in touchingBranches.values():
        for branch1 in branches:
            for branch2 in branches:
                if branch1 != branch2:
                    for obj in bpy.data.objects:
                        if branch1 in obj.name:
                            for b in branchList:
                                if branch2 in b.ob.name:
                                    obj2 = b.copy

                    for obj in bpy.data.objects:
                        if branch1 in obj.name:
                            obj1 = obj

                    carver(obj1, obj2)


with open("C:\\Users\\nichk\\3DObjConverter\.venv\TreeData2.csv", "r", newline='') as data:
    info = csv.reader(data)
    header = next(info)

    branchList = []
    touchingBranches = {}

    # bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(500, 500, 500), scale=(1, 1, 1), size=1000)
    # cube = bpy.context.active_object
    # cube.name = "CUBE"
    for row in info:
        rowData = []
        for elm in row:
            if elm in ["True", "False"]:
                rowData.append(bool(elm))
            else:
                rowData.append(float(elm))

        if rowData[1] != 0:
            if rowData[1] not in touchingBranches:
                touchingBranches[rowData[1]] = [rowData[0], ]
            else:
                touchingBranches[rowData[1]].append(rowData[0])

        if rowData[2] not in touchingBranches:
            touchingBranches[rowData[2]] = [rowData[0], ]
        else:
            touchingBranches[rowData[2]].append(rowData[0])

        b = Branch(rowData)

        b.make_cylinder()
        b.final_branch()
        branchList.append(b)

        # carver(cube, b.ob)
        # carver(cube, b.ob2)

    for branches in touchingBranches.values():
        for branch in range(len(branches)):
            branches[branch] = f"Branch:{branches[branch]}"

    # clean_branches()
    # clean_spheres()
    clean()

    # for branch in branchList:

    # branch.hollow_branch()
    # branch.final_branch()


