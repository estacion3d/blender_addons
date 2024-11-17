bl_info = {
    "name": "Separate Object in Pieces",
    "author": "Harold Tovar, Estación3D",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Tool > Split Tool > Separate Object",
    "description": "Separate object into individual pieces",
    "category": "Object",
}

import bpy
import bmesh

class SeparationSettings(bpy.types.PropertyGroup):
    apply_origin_to_center: bpy.props.BoolProperty(
        name = "Apply Origin to Center",
        description = "Set the origin to the center",
        default = False
    )

class OBJECT_OT_separate_geometry_clusters(bpy.types.Operator):
    bl_idname = "object.separate_geometry_clusters"
    bl_label = "Separate Geometry Clusters"
    bl_description = "Separate object into individual pieces in object mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Ensure there are selected objects and they are mesh objects
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Access the scene's property group
        separation_settings = context.scene.separation_settings
        apply_origin_to_center = separation_settings.apply_origin_to_center

        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            # Ensure in Object Mode
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Apply object transformations to prevent offsets
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            # Store the object's world matrix
            world_matrix = obj.matrix_world.copy()

            # Create a BMesh from the object
            bm = bmesh.new()
            bm.from_mesh(obj.data)

            # Find disconnected geometry islands
            islands = self.get_geometry_islands(bm)

            # Separate each island into a new object
            for island_verts in islands:
                # Create a new mesh and object for this island
                new_mesh = bpy.data.meshes.new(f"{obj.name}_Part")
                new_obj = bpy.data.objects.new(new_mesh.name, new_mesh)
                context.collection.objects.link(new_obj)

                # Preserve the original position by applying the world matrix
                new_obj.matrix_world = world_matrix

                # Create a new BMesh for the island
                island_bm = bmesh.new()
                vert_map = {}

                # Copy vertices and faces to the new BMesh
                for vert in island_verts:
                    new_vert = island_bm.verts.new(world_matrix @ vert.co)  # Transform to world space
                    vert_map[vert] = new_vert
                island_bm.verts.ensure_lookup_table()

                for face in bm.faces:
                    if all(v in island_verts for v in face.verts):
                        island_bm.faces.new([vert_map[v] for v in face.verts])

                # Update the new object with the island BMesh
                island_bm.to_mesh(new_mesh)
                island_bm.free()

                # Optionally set the origin to the center
                if apply_origin_to_center:
                    new_obj.select_set(True)
                    context.view_layer.objects.active = new_obj
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

            # Remove the original object
            bpy.data.objects.remove(obj, do_unlink=True)

        self.report({'INFO'}, "All selected objects were separated in pieces")
        return {'FINISHED'}

    def get_geometry_islands(self, bm):
        """Find disconnected geometry islands in a BMesh."""
        visited = set()
        islands = []

        for vert in bm.verts:
            if vert in visited:
                continue

            # Perform a flood fill to collect all connected vertices
            island = set()
            stack = [vert]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                island.add(current)
                stack.extend([e.other_vert(current) for e in current.link_edges])

            islands.append(island)

        return islands

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
