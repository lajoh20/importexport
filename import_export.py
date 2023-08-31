import bpy
import json
import os

def find_layer_collection(layer_collection, name):
    for lc in layer_collection.children:
        if lc.name == name:
            return lc
        lc_found = find_layer_collection(lc, name)
        if lc_found:
            return lc_found
    return None

def export_visibility_status(context, file_path):
    visibility_data = {'objects': {}, 'collections': {}}
    
    for obj in bpy.context.scene.objects:
        visibility_data['objects'][obj.name] = obj.hide_get()
    
    view_layer = bpy.context.view_layer
    for coll in bpy.data.collections:
        lc = find_layer_collection(view_layer.layer_collection, coll.name)
        if lc:
            visibility_data['collections'][coll.name] = lc.hide_viewport
    
    with open(file_path, "w") as f:
        json.dump(visibility_data, f)

def import_visibility_status(context, file_path):
    try:
        with open(file_path, "r") as f:
            visibility_data = json.load(f)
        
        for obj_name, is_hidden in visibility_data['objects'].items():
            if obj_name in bpy.context.scene.objects:
                bpy.context.scene.objects[obj_name].hide_set(is_hidden)
        
        view_layer = bpy.context.view_layer
        for col_name, is_hidden in visibility_data['collections'].items():
            lc = find_layer_collection(view_layer.layer_collection, col_name)
            if lc:
                lc.hide_viewport = is_hidden

    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")

class ExportVisibilityOperator(bpy.types.Operator):
    bl_idname = "object.export_visibility"
    bl_label = "Export Visibility to File"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        export_visibility_status(context, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ImportVisibilityOperator(bpy.types.Operator):
    bl_idname = "object.import_visibility"
    bl_label = "Import Visibility from File"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        import_visibility_status(context, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VisibilityPanel(bpy.types.Panel):
    bl_label = "Visibility Control"
    bl_idname = "OBJECT_PT_visibility_control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.export_visibility")
        layout.operator("object.import_visibility")

def register():
    bpy.utils.register_class(ExportVisibilityOperator)
    bpy.utils.register_class(ImportVisibilityOperator)
    bpy.utils.register_class(VisibilityPanel)

def unregister():
    bpy.utils.unregister_class(ExportVisibilityOperator)
    bpy.utils.unregister_class(ImportVisibilityOperator)
    bpy.utils.unregister_class(VisibilityPanel)

if __name__ == "__main__":
    register()
