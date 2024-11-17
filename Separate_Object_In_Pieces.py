# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# ##### COMIENZO LICENCIA GPL ESPAÑOL #####
#
# Este programa es sofware libre; puedes redistribuirlo y/o
# Modificarlo bajo los terminos de la Licencia Publica General GNU
# Publicada por la Fundación para el Software Libre; ya sea la versión 2
# De la Licencia, o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# Pero SIN NINGUNA GARANTÍA; ni siquiera la garantía implícita de
# COMERCIALIZACIÓN o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Vea el
# Licencia Pública General GNU para más detalles.
#
# Debería haber recibido una copia de la Licencia Pública General GNU
# Junto a este programa; si no, escriba a la Free Software Foundation,
# Inc., 51 Franklin Street, Quinto Piso, Boston, MA 02110-1301, EE.UU..
#
# ##### FIN LICENCIA GPL ESPAÑOL #####

# English:
# This Blender addon allow separate an object in different pieces inside Object Mode
# The addon could take a bit to separated the object if the object have a lot of polygons
# The addon works on multiple selected objects and only works in Mesh Objects
# The addon have an option to set the origin to the center of the objects after separated them
# The addon have an option to remove the unused materials in the separated objects

# Español:
# Este addon para Blender permite separar un objecto en sus diferentes piezas en modo objeto
# El addon podria tardar un poco en separar el objecto si este tiene muchos polygonos
# El addon funciona con multiples objectos seleccionados
# El addon tiene una opcion para asignar el centro de pivote / origen en el centro despues de separar los objectos
# El addon tiene una opcion que permite borrar los materiales que no estan en uso despues de separar los objetos

# Happy Blendig!!!

bl_info = {
    "name": "Separate Objects in Pieces",
    "blender": (3, 2, 0),
    "category": "Object",
    "author": "Harold Tovar, Estación3D",
    "description": "Separate selected objects into pieces",
    "version": (1, 2, 1),
    "support": "COMMUNITY",
}

import bpy
from bpy import context, ops
from bpy.props import BoolProperty
from bpy.types import Operator, PropertyGroup, Panel


# Define a custom property group
class ObjectSeparationProperties(PropertyGroup):
    
    apply_origin_to_center: BoolProperty(
        name="Apply Origin to Center",
        description="Set the origin of separated objects to their center",
        default=False
    )
    
    clear_unused_materials: BoolProperty(
        name="Clear Unused Materials",
        description="Delete materials not used by the objects after separation",
        default=False
    )


# Define the operator for separating by loose parts
class OBJECT_OT_separate_and_apply_origin(Operator):
    
    bl_idname = "object.separate_and_apply_origin"
    bl_label = "Separate Object in Pieces"
    bl_description = "Separate selected objects into Pieces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == 'OBJECT' and \
               any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        props = context.scene.separation_properties

        for obj in selected_objects:
            context.view_layer.objects.active = obj
            ops.object.mode_set(mode='EDIT')
            ops.mesh.separate(type='LOOSE')
            ops.object.mode_set(mode='OBJECT')

            if props.apply_origin_to_center:
                for separated_obj in context.selected_objects:
                    context.view_layer.objects.active = separated_obj
                    ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

        if props.clear_unused_materials:
            for obj in selected_objects:
                self.clear_unused_materials(obj)

        self.report({'INFO'}, "All the selected objects were separated into pieces")
        return {'FINISHED'}

    def clear_unused_materials(self, obj):
        # Use the built-in operator to remove unused materials
        ops.object.material_slot_remove_unused()


# Define the operator for separating by material
class OBJECT_OT_separate_by_material_and_clear(Operator):
    
    bl_idname = "object.separate_by_material_and_clear"
    bl_label = "Separate Object by Material"
    bl_description = "Separate selected objects in pieces by material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == 'OBJECT' and \
               any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        props = context.scene.separation_properties

        for obj in selected_objects:
            context.view_layer.objects.active = obj
            ops.object.mode_set(mode='EDIT')
            ops.mesh.separate(type='MATERIAL')
            ops.object.mode_set(mode='OBJECT')

            if props.apply_origin_to_center:
                for separated_obj in context.selected_objects:
                    context.view_layer.objects.active = separated_obj
                    ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

        if props.clear_unused_materials:
            for obj in selected_objects:
                self.clear_unused_materials(obj)

        self.report({'INFO'}, "All the selected objects were separated by material")
        return {'FINISHED'}

    def clear_unused_materials(self, obj):
        # Use the built-in operator to remove unused materials
        ops.object.material_slot_remove_unused()


# Add a UI panel
class OBJECT_PT_separate_panel(Panel):
    
    bl_label = "Separate Object"
    bl_idname = "OBJECT_PT_separate_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Split Obj Tools'

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene

        layout.prop(scene.separation_properties, "apply_origin_to_center")
        layout.prop(scene.separation_properties, "clear_unused_materials")

        layout.operator("object.separate_and_apply_origin", text="Separate Object in Pieces")
        layout.operator("object.separate_by_material_and_clear", text="Separate Object by Material")


# Register classes and property group
classes = (
    ObjectSeparationProperties,
    OBJECT_OT_separate_and_apply_origin,
    OBJECT_OT_separate_by_material_and_clear,
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


if __name__ == "__main__":
    register()
