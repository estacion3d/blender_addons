bl_info = {
    "name": "Separate Object in Pieces",
    "blender": (3, 2, 0),
    "category": "Object",
    "author": "Harold Tovar, Estación3D",
    "description": "Separate selected mesh objects into pieces",
    "version": (1, 0, 0),
    "support": "COMMUNITY",
}

import bpy

# Define a custom property group
class ObjectSeparationProperties(bpy.types.PropertyGroup):
    apply_origin_to_center: bpy.props.BoolProperty(
        name="Apply Origin to Center",
        description="Set the origin of separated objects to their center",
        default=True
    )

# Define the operator
class OBJECT_OT_separate_and_apply_origin(bpy.types.Operator):
    bl_idname = "object.separate_and_apply_origin"
    bl_label = "Separate Object into Pieces"
    bl_description = "Separate selected objects into pieces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if we are in Object Mode and at least one object is selected
        return context.object and context.object.mode == 'OBJECT' and \
               any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Get the selected objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            # Make the object active
            context.view_layer.objects.active = obj

            # Get the property group for the object
            props = context.scene.separation_properties  # Use scene properties instead of object

            # Enter Edit Mode to separate
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')

            # Apply origin to center if the property is True
            if props.apply_origin_to_center:
                for separated_obj in context.selected_objects:
                    context.view_layer.objects.active = separated_obj
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

        self.report({'INFO'}, "All the selected objects were separated into pieces")
        return {'FINISHED'}

# Add a UI panel
class OBJECT_PT_separate_panel(bpy.types.Panel):
    bl_label = "Separate Object in Pieces"
    bl_idname = "OBJECT_PT_separate_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Split Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Draw the UI elements for scene-level properties
        layout.prop(scene.separation_properties, "apply_origin_to_center")

        # Only enable the button if poll conditions are met
        layout.operator("object.separate_and_apply_origin", text="Separate Object in Pieces")

# Register classes and property group
classes = (
    ObjectSeparationProperties,
    OBJECT_OT_separate_and_apply_origin,
    OBJECT_PT_separate_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.separation_properties = bpy.props.PointerProperty(type=ObjectSeparationProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.separation_properties

# Only run the register function if the script is executed as a standalone addon.
if __name__ == "__main__":
    register()
