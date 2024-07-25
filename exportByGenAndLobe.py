import bpy


class BranchInfo:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        
        info = name.split(" ")
        self.id = int(float((info[0]).replace("Branch:", "")))
        self.gen = int(float((info[1]).replace("Gen:", "")))
        self.lobe = int(float((info[2]).replace("Lobe:", "")))
    
def exportByGen():
    
    for g in gen:
        bpy.ops.object.select_all(action='DESELECT')  
        print(f"Exporting Gen:{g}")
        for b in branchList:
            if b.gen == g:
                b.obj.select_set(True)
        stl_path = f"{path}\\gen{g}.stl"
        bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
        
def exportByLobe():
    for l in lobe:
        bpy.ops.object.select_all(action='DESELECT')  
        print(f"Exporting Gen:{l}")
        for b in branchList:
            if b.lobe == l:
                b.obj.select_set(True)
        stl_path = f"{path}\\lobe{l}.stl"
        bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)

context = bpy.context
scene = context.scene
viewlayer = context.view_layer


path_gen = "\\GenExtract"
path_lobe = "\\LobeExtract"
gen = set()
lobe = set()
branchList = []

for obj in bpy.data.objects:
    b = BranchInfo(obj.name, obj)
    
    gen.add(b.gen)
    lobe.add(b.lobe)
    branchList.append(b)

exportByGen()
exportByLobe()
