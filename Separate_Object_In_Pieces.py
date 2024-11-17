bl_info = {
    "name": "Separate Object in Pieces",
    "author": "Harold Tovar, Estación3D",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Tool > Split Tool > Separate Object in Pieces",
    "description": "Separate object in different pieces",
    "category": "Object",
}

import bpy

class SeparationSettings(bpy.types.PropertyGroup):
    apply_origin_to_center: bpy.props.BoolProperty(
        name ="Set Origin to Center",
        description ="Set the origin of separated objects to their center",
        default = False
    )
    apply_transformations: bpy.props.BoolProperty(
        name = "Apply Transformations",
        description = "Apply location, rotation, and scale to the new objects",
        default = False
    )

class OBJECT_OT_separate_geometry_clusters(bpy.types.Operator):
    bl_idname = "object.separate_geometry_clusters"
    bl_label = "Separate Object in Pieces"
    bl_description = "Separate into individual objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Ensure there are selected objects and they are mesh objects
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Access the scene's property group
        separation_settings = context.scene.separation_settings
        apply_origin_to_center = separation_settings.apply_origin_to_center
        apply_transformations = separation_settings.apply_transformations

        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            # Ensure in Object Mode
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Optionally, apply transformations if needed (scale, rotation, location)
            if apply_transformations:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            # Switch to Edit mode and separate geometry by loose parts
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')

            # Now, new objects are created for each loose geometry island
            for new_obj in context.view_layer.objects:
                if new_obj.select_get() and new_obj.type == 'MESH' and new_obj != obj:
                    # Preserve the original object's materials
                    new_obj.data.materials.clear()  # Clear default materials
                    for mat in obj.data.materials:
                        new_obj.data.materials.append(mat)

                    # Optionally set the origin to the center
                    if apply_origin_to_center:
                        new_obj.select_set(True)
                        context.view_layer.objects.active = new_obj
                        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

            # Remove the original object after separation
            bpy.data.objects.remove(obj, do_unlink=True)

        self.report({'INFO'}, "Geometry clusters separated and original objects deleted")
        return {'FINISHED'}

class OBJECT_PT_separate_panel(bpy.types.Panel):
    bl_label = "Separate Object in Pieces"
    bl_idname = "OBJECT_PT_separate_geometry_clusters_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Split Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Property from Scene's property group
        layout.prop(scene.separation_settings, "apply_origin_to_center", text="Apply Origin to Center")
        layout.prop(scene.separation_settings, "apply_transformations", text="Apply Transformations (Location/Rotation/Scale)")
        layout.operator("object.separate_geometry_clusters")

classes = (
    SeparationSettings,
    OBJECT_OT_separate_geometry_clusters,
    OBJECT_PT_separate_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.separation_settings = bpy.props.PointerProperty(type=SeparationSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.separation_settings

if __name__ == "__main__":
    register()
