import bpy, os
from bpy.utils import register_class, unregister_class
from . import scene, object

classes = [
    scene.NX_PT_Panel,
    scene.NX_PT_Settings
    #scene.NX_PT_Modules,
    #object.NX_PT_ObjectMenu,
    #object.NX_PT_Modules,
    #scene.NX_PT_Shadows,
    #scene.NX_PT_Postprocessing
]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)