import bpy, os, json, webbrowser, subprocess, shutil, re

from .. operations import compile, clean, filemaker, live_link

from .. utility import util, projectMaker

import bpy
import os
import json
import subprocess

class NX_Generate(bpy.types.Operator):
    bl_idname = "nx.generate"
    bl_label = "Generate"
    bl_description = "Generates the project (pre-generated dependencies and files)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Get the current Blender file's name and directory
        file_path = bpy.data.filepath
        if not file_path:
            self.report({'ERROR'}, "Please save your Blender project first.")
            return {"CANCELLED"}

        # Sanitize the project name
        blend_file_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(os.path.basename(file_path))[0])
        project_directory = os.path.join(os.path.dirname(file_path), "build")

        # Invoke the modal operator and pass the necessary data
        bpy.ops.nx.warning_modal('INVOKE_DEFAULT', project_directory=project_directory, blend_file_name=blend_file_name)

        return {'FINISHED'}



class NX_WarningModal(bpy.types.Operator):
    bl_idname = "nx.warning_modal"
    bl_label = "Warning"
    bl_description = "Make sure to open the console to track progress"

    # Pass the project directory and file name as properties to the modal
    project_directory: bpy.props.StringProperty()
    blend_file_name: bpy.props.StringProperty()

    def execute(self, context):
        # Generate the project after user clicks OK
        project_directory = self.project_directory
        blend_file_name = self.blend_file_name

        try:
            # Create a clean build directory
            if os.path.exists(project_directory):
                shutil.rmtree(project_directory)
            os.makedirs(project_directory)

            self.report({'INFO'}, f"Build directory created at: {project_directory}")

            # Initialize Cargo project
            subprocess.run(["cargo", "init", "--name", blend_file_name], cwd=project_directory, check=True)
            self.report({'INFO'}, "Cargo project initialized.")

            # Add Bevy dependency
            subprocess.run(["cargo", "add", "bevy"], cwd=project_directory, check=True)
            self.report({'INFO'}, "Bevy dependency added.")

            # Retrieve the path to the bundled `template` folder
            bundled_template_path = os.path.join(util.get_bundled_path(), "template")
            if not os.path.exists(bundled_template_path):
                raise FileNotFoundError(f"Template folder not found: {bundled_template_path}")

            # Define the destination path (for example, within a build directory)
            src_directory = os.path.join(project_directory, "src")

            # Ensure the destination directory exists
            if not os.path.exists(src_directory):
                os.makedirs(src_directory)

            # Copy the contents of the template folder to the destination
            for item in os.listdir(bundled_template_path):
                source_path = os.path.join(bundled_template_path, item)
                destination_path = os.path.join(src_directory, item)

                if os.path.isdir(source_path):
                    # Copy directories recursively, overwriting existing ones
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                else:
                    # Copy individual files
                    shutil.copy2(source_path, destination_path)

            print(f"Template files successfully copied to: {src_directory}")

            # Build the Cargo project
            subprocess.run(["cargo", "build"], cwd=project_directory, check=True)
            self.report({'INFO'}, "Cargo project built successfully.")

        except FileNotFoundError:
            self.report({'ERROR'}, "Cargo not found. Make sure Rust is installed.")
            return {"CANCELLED"}
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"An error occurred: {e}")
            return {"CANCELLED"}

        # This line must be outside the try-except block but inside the method
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.bl_label)
        layout.label(text=self.bl_description)

class NX_Start(bpy.types.Operator):
    bl_idname = "nx.compile_start"
    bl_label = "Start"
    bl_description = "Start your project (generate if no dependencies present)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Get the current Blender file's name and directory
        file_path = bpy.data.filepath
        if not file_path:
            self.report({'ERROR'}, "Please save your Blender project first.")
            return {"CANCELLED"}

        project_directory = os.path.join(os.path.dirname(file_path), "build")
        assets_directory = os.path.join(project_directory, "assets")

        # Ensure the build and assets directories exist
        if not os.path.exists(project_directory):
            self.report({'INFO'}, "No build directory found. Generating project first...")
            bpy.ops.nx.generate()
            return {"CANCELLED"}
        
        if not os.path.exists(assets_directory):
            os.makedirs(assets_directory)

        # Create the project.nest file
        project_name = os.path.splitext(os.path.basename(file_path))[0]
        project_nest_path = os.path.join(project_directory, "project.nest")
        project_data = {
            "name": project_name,
            "bversion": "0.15",  # Replace with the actual Bevy version you want to use
            "nversion": "0.1",
            "scene": f"{project_name}.glb"
        }
        try:
            with open(project_nest_path, "w") as f:
                json.dump(project_data, f, indent=4)
            self.report({'INFO'}, f"Project file created: {project_nest_path}")
        except IOError as e:
            self.report({'ERROR'}, f"Failed to create project.nest: {e}")
            return {"CANCELLED"}

        # Export the scene as a GLB file
        glb_path = os.path.join(assets_directory, f"{project_name}.glb")
        try:

            bpy.ops.export_scene.gltf(
                export_format="GLB",
                export_draco_mesh_compression_enable=False,
                export_apply=True,
                use_visible=True,
                use_renderable=True,
                use_active_scene=True,
                export_yup=True,
                filepath=glb_path)

            self.report({'INFO'}, f"Scene exported to: {glb_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export scene: {e}")
            return {"CANCELLED"}

        #Copy over the template files

        #I have a util function util.get_bundled_path(), which retrieves the addon/bundled path
        #In here, I have a folder called template, from which I would like to copy over (overwrite) the contents into the assets/src folder

        try:
            # Retrieve the path to the bundled `template` folder
            bundled_template_path = os.path.join(util.get_bundled_path(), "template")
            if not os.path.exists(bundled_template_path):
                raise FileNotFoundError(f"Template folder not found: {bundled_template_path}")

            # Define the destination path (for example, within a build directory)
            src_directory = os.path.join(project_directory, "src")

            # Ensure the destination directory exists
            if not os.path.exists(src_directory):
                os.makedirs(src_directory)

            # Copy the contents of the template folder to the destination
            for item in os.listdir(bundled_template_path):
                source_path = os.path.join(bundled_template_path, item)
                destination_path = os.path.join(src_directory, item)

                if os.path.isdir(source_path):
                    # Copy directories recursively, overwriting existing ones
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                else:
                    # Copy individual files
                    shutil.copy2(source_path, destination_path)

            print(f"Template files successfully copied to: {src_directory}")

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


        # Run `cargo run` in the build directory
        try:
            subprocess.run(["cargo", "run"], cwd=project_directory, check=True)
            self.report({'INFO'}, "Project started successfully.")
        except FileNotFoundError:
            self.report({'ERROR'}, "Cargo not found. Make sure Rust is installed.")
            return {"CANCELLED"}
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"An error occurred: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}

class NX_Stop(bpy.types.Operator):
    bl_idname = "nx.stop"
    bl_label = "Stop"
    bl_description = "Stop your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        stop_server(bpy.context.scene.NX_SceneProperties.nx_live_link)

        return {"FINISHED"}
    
class NX_Clean(bpy.types.Operator):
    bl_idname = "nx.clean"
    bl_label = "Clean"
    bl_description = "Clean your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        file_path = bpy.data.filepath
        if not file_path:
            self.report({'ERROR'}, "Please save your Blender project first.")
            return {"CANCELLED"}

        project_directory = os.path.join(os.path.dirname(file_path), "build")

        try:
            subprocess.run(["cargo", "clean"], cwd=project_directory, check=True)
            self.report({'INFO'}, "Project started successfully.")

        return {"FINISHED"}
    
class NX_Explore(bpy.types.Operator):
    bl_idname = "nx.explore"
    bl_label = "Explore"
    bl_description = "Explore your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        #Open the path in explorer

        path = util.get_project_path()

        os.startfile(path)

        return {"FINISHED"}
    
# OBJECT OPERATORS

class NX_ModuleListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "nx_modulelist.new_item"
    bl_label = "Add a new module"
    bl_description = "Add a new module"

    def execute(self, context):
        obj = context.object

        obj.NX_UL_ModuleList.add()

        obj.NX_UL_ModuleListItem = len(obj.NX_UL_ModuleList) - 1
        obj.NX_UL_ModuleList[len(obj.NX_UL_ModuleList) - 1].name = "Module"

        util.getProjectJSScripts()
        util.getBundledScripts()

        return{'FINISHED'}
    
class NX_UL_PostprocessListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "nx_postprocesslist.new_item"
    bl_label = "Add a new postprocess"
    bl_description = "Add a new postprocess"

    def execute(self, context):
        scene = context.scene

        scene.NX_UL_PostprocessList.add()

        scene.NX_UL_PostprocessListItem = len(scene.NX_UL_PostprocessList) - 1
        scene.NX_UL_PostprocessList[len(scene.NX_UL_PostprocessList) - 1].name = "Postprocess"

        return{'FINISHED'}
    
class NX_UL_PostprocessListRemoveItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "nx_postprocesslist.delete_item"
    bl_label = "Removes the postprocess"
    bl_description = "Delete a postprocess"

    # @classmethod
    # def poll(self, context):
    #     """ Enable if there's something in the list """
    #     obj = context.object
    #     return len(obj.NX_UL_PostprocessList) > 0

    def execute(self, context):
        scene = context.scene
        list = scene.NX_UL_PostprocessList
        index = scene.NX_UL_PostprocessListItem

        list.remove(index)

        if index > 0:
            index = index - 1

        scene.NX_UL_PostprocessListItem = index

        return{'FINISHED'}
    
class NX_ModuleListRemoveItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "nx_modulelist.delete_item"
    bl_label = "Removes the module"
    bl_description = "Delete a module"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        obj = context.object
        return len(obj.NX_UL_ModuleList) > 0

    def execute(self, context):
        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        list.remove(index)

        if index > 0:
            index = index - 1

        obj.NX_UL_ModuleListItem = index

        util.getProjectJSScripts()
        util.getBundledScripts()

        return{'FINISHED'}
    
class NX_NewJavascriptFile(bpy.types.Operator):
    bl_idname = "nx_modulelist.new_script"
    bl_label = "New Script"

    filename: bpy.props.StringProperty(name="Filename (*.js/*.ts)")
    fileformat: bpy.props.EnumProperty(
        items = [('TypeScript', 'TypeScript', 'TypeScript format'),
                 ('JavaScript', 'JavaScript', 'JavaScript format'),],
                name = "Script format", 
                description="Select the script format",
                default='JavaScript')

    def execute(self, context):

        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        self.filename = self.filename.capitalize()

        print("Creating javascript file at sources folder", self.filename)

        if(filemaker.create_javascript_file(self.filename, self.fileformat)):

            obj.NX_UL_ModuleList[index].nx_module_script = self.filename
            obj.NX_UL_ModuleList[index].nx_module_script_format = self.fileformat

            util.fetchBundledScriptProps(obj.NX_UL_ModuleList[index])

            print("Javascript file created")

        else:
            
            print("TODO: ERROR")

        util.getProjectJSScripts()
        util.getBundledScripts()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
class NX_EditJavascriptFile(bpy.types.Operator):
    bl_idname = "nx_modulelist.edit_script"
    bl_label = "Edit Script"

    def execute(self, context):

        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        #If file exists
        if os.path.exists(os.path.join(util.get_sources_path(), list[index].nx_module_script + ".js")):
            file = os.path.join(util.get_sources_path(), list[index].nx_module_script + ".js")
        else:
            file = os.path.join(util.get_sources_path(), list[index].nx_module_script + ".ts")

        os.system(file)

        print("Editing javascript file at sources folder: ", list[index].nx_module_script)

        util.getProjectJSScripts()
        util.getBundledScripts()

        return {'FINISHED'}
    
class NX_RefreshScripts(bpy.types.Operator):
    bl_idname = "nx_modulelist.refresh_scripts"
    bl_label = "Refresh scripts"

    def execute(self, context):

        util.getProjectJSScripts()
        util.getBundledScripts()

        # wrd = bpy.data.worlds['Arm']
        # wrd.arm_bundled_scripts_list.clear()

        # with WorkingDir(get_sdk_path() + '/armory/Sources/armory/trait'):
        #     for file in glob.glob('*.hx'):
        #         wrd.arm_bundled_scripts_list.add().name = file.rsplit('.', 1)[0]

        #Fetch bundled scripts
        #Fetch bundled props
        #Fetch script names
        #Fetch script props

        return {'FINISHED'}
    
class NX_OpenStore(bpy.types.Operator):
    bl_idname = "nx.open_store"
    bl_label = "Open Store"

    def execute(self, context):

        print("TODO: Open Store")
        #store.start_store()

        return {'FINISHED'}

class OBJECT_OT_injection_component(bpy.types.Operator):
    bl_idname = "object.injection_component"
    bl_label = "Injection Component"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.empty_add(type='SINGLE_ARROW')  # This adds an empty object to the scene
        component = bpy.context.object
        component.name = "InjectionComponent"
        component["NX_InjectionComponent"] = True

        return {'FINISHED'}
    
class VIEW3D_MT_nax_menu(bpy.types.Menu):
    bl_label = "NAX Engine"
    bl_idname = "VIEW3D_MT_nax_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_injection_component.bl_idname, icon='NODE')