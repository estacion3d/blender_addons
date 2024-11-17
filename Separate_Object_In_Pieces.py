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

      def execute(self, context):
        obj = context.active_object

        # Ensure it's a mesh object
        if obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        # Get the property group
        props = obj.separation_properties
        
        # Enter Edit Mode to separate
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply origin to center if the property is True
        if props.apply_origin_to_center:
            for obj in context.selected_objects:
                if obj.type == 'MESH':  # Ensure we only modify mesh objects
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

        self.report({'INFO'}, "Objects separated and origins updated")
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
