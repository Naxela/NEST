import bpy
import subprocess

from ..utility import util

from bpy.types import (
    Panel,
    AddonPreferences,
    Operator,
    PropertyGroup,
)

# Cache the Rust check result
RUST_INSTALLED = None

def is_rust_installed():
    global RUST_INSTALLED
    if RUST_INSTALLED is None:
        try:
            subprocess.run(["rustc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            RUST_INSTALLED = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            RUST_INSTALLED = False
    return RUST_INSTALLED

class NX_PT_Panel(bpy.types.Panel):
    bl_label = "NEST"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        file_path = bpy.data.filepath

        # Check if the file has been saved
        if file_path:

            row = layout.row(align=True)

            if is_rust_installed():
                row.operator("nx.generate")
                row.operator("nx.compile_start")
                row.operator("nx.explore")
                row.operator("nx.clean")
            else:
                row.label(text="Rust is not installed. Please install Rust.")

            
            #row.operator("nx.compile_start")
            #row.operator("nx.generate")

        else:
            row = layout.row(align=True)
            row.label(text="Please save your project")

class NX_PT_Settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        # row = layout.row(align=True)
        # row.label(text="Environment:", icon="WORLD")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_initial_scene")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_regen_project")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_xr_mode")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_debug_mode")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_fullscreen")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_minify_json")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_compilation_mode")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_pipeline_mode")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_live_link")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_optimize")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_http_port")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_tcp_port")
        # row = layout.row(align=True)
        # row.prop(scene.NX_SceneProperties, "nx_texture_quality", slider=True)
        
        #row.operator("nx.compile")

class NX_PT_Shadows(bpy.types.Panel):
    bl_label = "Shadows"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)
    
    def draw_header(self, context):

        scene = context.scene
        sceneProperties = scene.NX_SceneProperties
        self.layout.prop(sceneProperties, "nx_enable_shadows", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()

class NX_PT_Postprocessing(bpy.types.Panel):
    bl_label = "Postprocessing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        sceneProperties = scene.NX_SceneProperties

class NX_PT_Modules(bpy.types.Panel):
    bl_label = "Modules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False