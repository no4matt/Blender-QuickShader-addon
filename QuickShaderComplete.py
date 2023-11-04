bl_info = {
    "name": "QuickShader",
    "author": "Vlad Liskovetskiy. Texture authors: Dario Barresi, Dimitrios Savva, Rob Tuytel, Amal Kumar, eye-candy.xyz, Rico Cilliers, Charlotte Baglioni",
    "version": (1, 0),
    "blender": (3, 40, 0),
    "location": "View3D > Toolshelf",
    "description": "This addon gives you an access to the library of shader presets and PBR-materials. Texture source: Poly Heaven",
    "warning": "",
    "doc_url": "",
    "category": "MATERIAL",
}

import bpy
import os

class ModifierPanel(bpy.types.Panel):
    bl_label = "Modify object"
    bl_idname = "PT_ ModifierPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QuickShader'
    

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        
        row = layout.row()
        row.label(text = "Select object modifier ", icon = 'TOOL_SETTINGS')
        col = layout.column()
        
        col.operator("object.shade_smooth", icon = 'ANTIALIASED')
        col.operator("object.shade_flat", icon = 'ALIASED')
        col.operator("object.subdivision_set", icon = 'SHADING_RENDERED', text = "Set subdivision",)
        col.operator("object.modifier_add", icon = 'MODIFIER_DATA')
        col.operator('object.remove_material', icon = 'CANCEL')


class RemoveMaterialOperator(bpy.types.Operator):
    bl_label = "Remove Material"
    bl_idname = 'object.remove_material'

    def execute(self, context):
        # Перевірка, чи обрано активний об'єкт
        if context.active_object is not None:
            if context.active_object.type == 'MESH':
                # Видалення всіх матеріалів з активного об'єкта
                context.active_object.data.materials.clear()
                self.report({'INFO'}, "Materials removed from the selected object.")
                return {'FINISHED'}
            else:
                # Якщо об'єкт не є мешем
                for slot in context.active_object.material_slots:
                    slot.material = None
                self.report({'INFO'}, "No material on a selected object.")
                return {'FINISHED'}



########################################################################################
#панель  шейдерів
class ShaderPanel(bpy.types.Panel):
    bl_label = "Shader presets"
    bl_idname = "SHADER_PT_MAINPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QuickShader'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        
        row = layout.row()
        col = layout.column()
        
        row.label(text = "Select a shader from a panel")
        


######################
######################
#Панель скла        
class GlassPanel(bpy.types.Panel):
        bl_label = "Glass shaders"
        bl_idname = "SHADER_PT_GLASSPANEL"
        bl_parent_id = "SHADER_PT_MAINPANEL"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'QuickShader'
        bl_options = {'DEFAULT_CLOSED'}

        def draw(self, context):
            layout = self.layout
            layout.scale_y = 1.2
        
            row = layout.row()
            col = layout.column()
                
            col.operator('shader.glass_operator') #кнопка Glass
            col.operator('shader.tr_glass_operator') #кнопка Transperent glass        
            col.operator('shader.mc_glass_operator') #кнопка Mosaic glass


#Шейдер скла
class SHADER_GLASS(bpy.types.Operator):
    bl_label = "Glass"
    bl_idname = 'shader.glass_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Glass
        material_glass = bpy.data.materials.new(name ="Glass")
        material_glass.use_nodes = True
        
        material_glass.node_tree.nodes.remove(material_glass.node_tree.nodes.get('Principled BSDF'))
        
        material_output = material_glass.node_tree.nodes.get('Material Output')
        material_output.location = (561, 213)
        
        glass1_node = material_glass.node_tree.nodes.new('ShaderNodeBsdfGlass')
        glass1_node.location = (187, 275)
        glass1_node.inputs[0].default_value = (1, 1, 1, 1)
        glass1_node.inputs[2].default_value = 1.470
                
        glass2_node = material_glass.node_tree.nodes.new('ShaderNodeBsdfGlass')
        glass2_node.location = (187, 140)
        glass2_node.inputs[0].default_value = (0.4, 0.6, 0.6, 1)
        glass2_node.inputs[2].default_value = 1.250
                
        mix_shader = material_glass.node_tree.nodes.new('ShaderNodeMixShader')
        mix_shader.location = (394, 243)
                
        material_glass.node_tree.links.new(glass1_node.outputs[0], mix_shader.inputs[1])
        material_glass.node_tree.links.new(glass2_node.outputs[0], mix_shader.inputs[2])
        material_glass.node_tree.links.new(mix_shader.outputs[0], material_output.inputs[0])
                
        bpy.context.object.active_material = material_glass
        
        return {'FINISHED'}
    

#Шейдер прозорішого скла
class SHADER_TRANPARENT_GLASS(bpy.types.Operator):
    bl_label = "Transperent glass"
    bl_idname = 'shader.tr_glass_operator'
    
    def execute(self, context):
        
        material_tr_glass = bpy.data.materials.new(name ="Trnasperent glass")
        material_tr_glass.use_nodes = True
        material_tr_glass.node_tree.nodes.remove(material_tr_glass.node_tree.nodes.get('Principled BSDF'))
        
        material_output = material_tr_glass.node_tree.nodes.get('Material Output')
        material_output.location = (-100, 176)
        
        #додавання першого нода Glass
        glass_node = material_tr_glass.node_tree.nodes.new('ShaderNodeBsdfGlass')
        glass_node.location = (-900, 300)

        glass_node.inputs[0].default_value = (0.55, 0.53, 0.53, 1)
        glass_node.inputs[1].default_value = 0.000
        glass_node.inputs[2].default_value = 1.000
                
        #додавання другого нода Glossy
        glossy_node = material_tr_glass.node_tree.nodes.new('ShaderNodeBsdfGlossy')
        glossy_node.location = (-900, 90)
        glossy_node.inputs[0].default_value = (1, 1, 1, 1)
        glossy_node.inputs[1].default_value = 0.100
                
        #додавання третього нода AddShader
        add_shader = material_tr_glass.node_tree.nodes.new('ShaderNodeAddShader')
        add_shader.location = (-700, 240)
                
        #додавання четвертого нода Transparent
        trans_node = material_tr_glass.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        trans_node.location = (-600, 100)
                
        #додавання п'ятого нода MixShader
        mix_shader = material_tr_glass.node_tree.nodes.new('ShaderNodeMixShader')
        mix_shader.location = (-300, 201)        
        
        #з'єднання нодів
        material_tr_glass.node_tree.links.new(glass_node.outputs[0], add_shader.inputs[0])
        material_tr_glass.node_tree.links.new(glossy_node.outputs[0], add_shader.inputs[1])
        material_tr_glass.node_tree.links.new(add_shader.outputs[0], mix_shader.inputs[1])
        material_tr_glass.node_tree.links.new(trans_node.outputs[0], mix_shader.inputs[2])
        material_tr_glass.node_tree.links.new(mix_shader.outputs[0], material_output.inputs[0])
                
        bpy.context.object.active_material = material_tr_glass
        
        return {'FINISHED'}


#Шейдер скла-мозайки
class SHADER_MOSAIC_GLASS(bpy.types.Operator):
    bl_label = "Mosaic glass"
    bl_idname = 'shader.mc_glass_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Glass
        material_mc_glass = bpy.data.materials.new(name ="Mosaic glass")
        material_mc_glass.use_nodes = True        
        material_mc_glass.node_tree.nodes.remove(material_mc_glass.node_tree.nodes.get('Principled BSDF'))
        
        material_output = material_mc_glass.node_tree.nodes.get('Material Output')
        material_output.location = (400, 90)
        
        voronoi_outline = material_mc_glass.node_tree.nodes.new('ShaderNodeTexVoronoi')
        voronoi_outline.feature = 'DISTANCE_TO_EDGE'
        voronoi_outline.location = (-1000, 265)
        
        color_ramp = material_mc_glass.node_tree.nodes.new('ShaderNodeValToRGB')
        # Отримуємо объект color_ramp з узла ValToRGB
        color_ramp_node = color_ramp.color_ramp
        
        color_ramp_node.elements[0].position = 0.01
        color_ramp_node.elements[1].position = 0.080
        color_ramp.location = (-800, 275)
        
        voronoi_color = material_mc_glass.node_tree.nodes.new('ShaderNodeTexVoronoi')
        voronoi_color.location = (-600, 20)
        
        mix_node = material_mc_glass.node_tree.nodes.new('ShaderNodeMixRGB')
        mix_node.blend_type = 'MULTIPLY'
        mix_node.inputs[0].default_value = 1
        mix_node.location = (-400, 250)
        
        glossy_node = material_mc_glass.node_tree.nodes.new('ShaderNodeBsdfGlossy')
        glossy_node.inputs[1].default_value = 0.26
        glossy_node.location = (-200, 300)
                
        trans_node = material_mc_glass.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        trans_node.location = (-200, 110)
        
        mix_shader = material_mc_glass.node_tree.nodes.new('ShaderNodeMixShader')
        mix_shader.inputs[0].default_value = 0.18
        mix_shader.location = (100, 300)
                        
        material_mc_glass.node_tree.links.new(voronoi_outline.outputs[0], color_ramp.inputs[0])
        material_mc_glass.node_tree.links.new(color_ramp.outputs[0], mix_node.inputs[1])
        material_mc_glass.node_tree.links.new(voronoi_color.outputs[1], mix_node.inputs[2])
        material_mc_glass.node_tree.links.new(voronoi_color.outputs[2], material_output.inputs[2])
        material_mc_glass.node_tree.links.new(mix_node.outputs[0], glossy_node.inputs[0])
        material_mc_glass.node_tree.links.new(glossy_node.outputs[0], mix_shader.inputs[1])
        material_mc_glass.node_tree.links.new(trans_node.outputs[0], mix_shader.inputs[2])
        material_mc_glass.node_tree.links.new(mix_shader.outputs[0], material_output.inputs[0])
        
        bpy.context.object.active_material = material_mc_glass
        
        return {'FINISHED'}


####################
####################
#Панель металів
class MetalicPanel(bpy.types.Panel):
        bl_label = "Metal shaders"
        bl_idname = "SHADER_PT_METALPANEL"
        bl_parent_id = "SHADER_PT_MAINPANEL"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'QuickShader'
        bl_options = {'DEFAULT_CLOSED'}

        def draw(self, context):
            layout = self.layout
            layout.scale_y = 1.2
        
            row = layout.row()
            col = layout.column()
                
            col.operator('shader.gold_operator')
            col.operator('shader.aluminium_operator') 
            col.operator('shader.copper_operator')
            col.operator('shader.steel_operator')
                
    
#Золото
class SHADER_GOLD(bpy.types.Operator):
    bl_label = "Gold"
    bl_idname = 'shader.gold_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Gold
        material_gold = bpy.data.materials.new(name ="Gold")
        material_gold.use_nodes = True

        material_output = material_gold.node_tree.nodes.get('Material Output')
        
        principled_bsdf = material_gold.node_tree.nodes.get('Principled BSDF')
        principled_bsdf.inputs[6].default_value = 1
        principled_bsdf.inputs[9].default_value = 0.16
        
        color_ramp = material_gold.node_tree.nodes.new('ShaderNodeValToRGB')
        # Отримуємо объект color_ramp из узла ValToRGB
        color_ramp_node = color_ramp.color_ramp
        color_ramp_node.elements[0].color = (1, 0.69, 0.22, 1)
        color_ramp_node.elements[1].color = (0.59, 0.21, 0.037, 1)
        color_ramp_node.elements[0].position = 0.335
        color_ramp_node.elements[1].position = 0.845
        color_ramp.location = (-500, 400)        
        
        musgrave = material_gold.node_tree.nodes.new('ShaderNodeTexMusgrave')
        musgrave.inputs[2].default_value = 215
        musgrave.inputs[3].default_value = 16
        musgrave.location = (-800, 300)
                
        material_gold.node_tree.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
        material_gold.node_tree.links.new(musgrave.outputs[0], color_ramp.inputs[0])
        
        bpy.context.object.active_material = material_gold
        
        return {'FINISHED'}
    

#Алюміній
class SHADER_ALUMINIUM(bpy.types.Operator):
    bl_label = "Aluminium"
    bl_idname = 'shader.aluminium_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Aluminium
        material_aluminium = bpy.data.materials.new(name ="Aluminium")
        material_aluminium.use_nodes = True

        material_output = material_aluminium.node_tree.nodes.get('Material Output')
        
        principled_bsdf = material_aluminium.node_tree.nodes.get('Principled BSDF')
        principled_bsdf.inputs[6].default_value = 1
        principled_bsdf.inputs[9].default_value = 0.275
        
        color_ramp = material_aluminium.node_tree.nodes.new('ShaderNodeValToRGB')
        # Отримуємо объект color_ramp из узла ValToRGB
        color_ramp_node = color_ramp.color_ramp
        color_ramp_node.elements[0].color = (0.37, 0.37, 0.37, 1)
        color_ramp_node.elements[1].color = (1, 1, 1, 1)
        color_ramp_node.elements[0].position = 0.23
        color_ramp_node.elements[1].position = 0.76
        color_ramp.location = (-500, 400)
        
        bump = material_aluminium.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs[0].default_value = 0.025
        bump.inputs[1].default_value = 0.1
        bump.location = (-500, 180)
        
        noise = material_aluminium.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs[2].default_value = 2
        noise.inputs[3].default_value = 15
        noise.inputs[4].default_value = 0.883
        noise.location = (-800, 300)
                
        material_aluminium.node_tree.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
        material_aluminium.node_tree.links.new(bump.outputs[0], principled_bsdf.inputs[22])
        material_aluminium.node_tree.links.new(noise.outputs[0], color_ramp.inputs[0])
        material_aluminium.node_tree.links.new(noise.outputs[0], bump.inputs[2])
        
        bpy.context.object.active_material = material_aluminium
        
        return {'FINISHED'}


#Шейдер міді
class SHADER_COPPER(bpy.types.Operator):
    bl_label = "Copper"
    bl_idname = 'shader.copper_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Copper
        material_copper = bpy.data.materials.new(name ="Copper")
        material_copper.use_nodes = True

        material_output = material_copper.node_tree.nodes.get('Material Output')
        
        principled_bsdf = material_copper.node_tree.nodes.get('Principled BSDF')
        principled_bsdf.inputs[6].default_value = 1
        principled_bsdf.inputs[9].default_value = 0.22
        
        color_ramp = material_copper.node_tree.nodes.new('ShaderNodeValToRGB')
        color_ramp_node = color_ramp.color_ramp
    
        # вказання позиції нового елемнту
        new_color_element = color_ramp_node.elements.new(0.5)  

        # колір нового елементу
        new_color_element.color = (0.84, 0.18, 0.06, 1)
        new_color_element.position = 0.5
        
        color_ramp_node.elements[0].color = (0.92, 0, 0, 1)
        color_ramp_node.elements[2].color = (0.07, 0.008, 0, 1)
        color_ramp.location = (-500, 150)        
        
        bump = material_copper.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs[0].default_value = 0.015
        bump.inputs[1].default_value = 0.1
        bump.location = (-500, -250)
        
        noise = material_copper.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs[2].default_value = 16
        noise.inputs[3].default_value = 8
        noise.inputs[4].default_value = 0.8
        noise.location = (-800, 300)        
                
        material_copper.node_tree.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
        material_copper.node_tree.links.new(bump.outputs[0], principled_bsdf.inputs[22])
        material_copper.node_tree.links.new(noise.outputs[1], color_ramp.inputs[0])
        material_copper.node_tree.links.new(noise.outputs[1], bump.inputs[2])
        
        bpy.context.object.active_material = material_copper
        
        return {'FINISHED'}
    

#Сталь
class SHADER_STEEL(bpy.types.Operator):
    bl_label = "Steel"
    bl_idname = 'shader.steel_operator'
    
    def execute(self, context):
        
        #створення нового шейдера під назвою Aluminium
        material_steel = bpy.data.materials.new(name ="Steel")
        material_steel.use_nodes = True

        material_output = material_steel.node_tree.nodes.get('Material Output')
        
        principled_bsdf = material_steel.node_tree.nodes.get('Principled BSDF')
        principled_bsdf.inputs[6].default_value = 1
        principled_bsdf.inputs[9].default_value = 0.185
        
        color_ramp = material_steel.node_tree.nodes.new('ShaderNodeValToRGB')
        color_ramp_node = color_ramp.color_ramp
        
        # вказання позиції нового елемнту
        new_color_element = color_ramp_node.elements.new(0.5)  

        # колір нового елементу
        new_color_element.color = (0.163, 0.163, 0.163, 1)
        new_color_element.position = 0.5
        
        color_ramp_node.elements[0].color = (1, 1, 1, 1)
        color_ramp_node.elements[2].color = (0.0005, 0.03, 0.23, 1)
        color_ramp_node.elements[2].position = 0.93
        color_ramp.location = (-500, 150)        
        
        bump = material_steel.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs[1].default_value = 20
        bump.location = (-500, -250)
        
        noise = material_steel.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs[2].default_value = 9
        noise.inputs[3].default_value = 15
        noise.inputs[4].default_value = 0.9
        noise.location = (-800, 100)
        
        musgrave = material_steel.node_tree.nodes.new('ShaderNodeTexMusgrave')
        musgrave.inputs[2].default_value = 10.1
        musgrave.inputs[3].default_value = 0.1
        musgrave.location = (-800, -200)
        
        material_steel.node_tree.links.new(color_ramp.outputs[0], principled_bsdf.inputs[0])
        material_steel.node_tree.links.new(bump.outputs[0], principled_bsdf.inputs[22])
        material_steel.node_tree.links.new(noise.outputs[0], color_ramp.inputs[0])
        material_steel.node_tree.links.new(noise.outputs[0], bump.inputs[2])
        material_steel.node_tree.links.new(musgrave.outputs[0], bump.inputs[0])
                        
        bpy.context.object.active_material = material_steel
        
        return {'FINISHED'}


##########################
##########################
#Панель шейдерів освіщення
class EmissionPanel(bpy.types.Panel):
        bl_label = "Emission"
        bl_idname = "SHADER_EMISSION_PANEL"
        bl_parent_id = "SHADER_PT_MAINPANEL"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'QuickShader'
        bl_options = {'DEFAULT_CLOSED'}

        def draw(self, context):
            layout = self.layout
            layout.scale_y = 1.2
            obj = context.active_object

            row = layout.row()
            col = layout.column()            
            
            add_emit_operator = col.operator('shader.add_emit_operator')
            col.prop(obj, "color", text="Color")
            add_emit_operator.color = obj.color[:4]
                                   
#Шейдер освітлення
class SHADER_ADD_EMITER(bpy.types.Operator):
    bl_label = "Add emit"
    bl_idname = 'shader.add_emit_operator'
    
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,  
        default=(1.0, 1.0, 1.0, 1.0),  
    )
    
    def execute(self, context):
        material_emit = bpy.data.materials.new(name="Emission")
        material_emit.use_nodes = True

        # Видалення всіх вузлів з матеріалу
        for node in material_emit.node_tree.nodes:
            material_emit.node_tree.nodes.remove(node)

        emission_node = material_emit.node_tree.nodes.new(type='ShaderNodeEmission')
        emission_node.location = (0, 0)
        emission_node.inputs[0].default_value = self.color
        emission_node.inputs[1].default_value = 20
        
        material_output = material_emit.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        material_output.location = (200, 0)

        material_emit.node_tree.links.new(emission_node.outputs[0], material_output.inputs[0])

        bpy.context.object.active_material = material_emit        
        return {'FINISHED'}


################################################################################################
#панель PBR текстур
class PBRPanel(bpy.types.Panel):
    bl_label = "PBR materials"
    bl_idname = "PT_PBR_MAINPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QuickShader'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        
        row = layout.row()
        col = layout.column()
        
        row.label(text = "Choose material from library ")

#батьківський клас для PBR операторів              
class PBRMaterialOperator(bpy.types.Operator):
    bl_label = "PBR Material Operator"
    bl_idname = 'pbr.material_operator'

    def execute(self, context):
        # Створення нового матеріала
        self.pbr_material = bpy.data.materials.new(name=self.material_name)
        self.pbr_material.use_nodes = True

        # Отримання вузлів
        material_output = self.pbr_material.node_tree.nodes.get('Material Output')
        principled_bsdf = self.pbr_material.node_tree.nodes.get('Principled BSDF')
        material_output.location = (600, -60)

        mix_node = self.pbr_material.node_tree.nodes.new('ShaderNodeMixRGB')
        mix_node.blend_type = 'MULTIPLY'
        mix_node.location = (-300, 300)

        ao_node = self.pbr_material.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
        ao_node.samples = 32
        ao_node.location = (-550, 190)

        normal_map = self.pbr_material.node_tree.nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-300, -200)

        mapping = self.pbr_material.node_tree.nodes.new('ShaderNodeMapping')
        mapping.location = (-1600, -20)

        texture_coord = self.pbr_material.node_tree.nodes.new('ShaderNodeTexCoord')
        texture_coord.location = (-1850, -50)

        # Лінкінг основних вузлів 
        self.pbr_material.node_tree.links.new(mix_node.outputs[0], principled_bsdf.inputs[0])
        self.pbr_material.node_tree.links.new(ao_node.outputs[1], mix_node.inputs[0])
        self.pbr_material.node_tree.links.new(ao_node.outputs[0], mix_node.inputs[2])
        self.pbr_material.node_tree.links.new(normal_map.outputs[0], principled_bsdf.inputs[22])
        

        bpy.context.object.active_material = self.pbr_material
        
        # Зберігання вузлів як атрибутів класу
        self.principled_bsdf = principled_bsdf
        self.mix_node = mix_node
        self.ao_node = ao_node
        self.normal_map = normal_map
        self.mapping = mapping
        self.texture_coord = texture_coord

        return {'FINISHED'}
    
    def add_texture_node(self, texture_path):
        texture_node = self.pbr_material.node_tree.nodes.new('ShaderNodeTexImage')
        texture_node.image = bpy.data.images.load(texture_path)
        texture_node.location = self.texture_node_location
        return texture_node
    
    def load_texture(self, file_name):
        script_path = os.path.abspath(__file__) # розкоментувати при створенні ZIP архіва, нижне закоментувати
        "script_path = bpy.data.texts['QuickShaderOptimizedPBR.py'].filepath"
        script_directory = os.path.dirname(script_path)
        texture_path = os.path.join(script_directory, self.texture_folder, file_name)
        texture_node = self.add_texture_node(texture_path)
        return texture_node

    

####################
####################
#Підпанель Tree wood        
class pbrWoodPanel(bpy.types.Panel):
            bl_label = "Tree wood"
            bl_idname = "PT_PBR_WOODPANEL"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                col.operator('pbr.wl_wood_operator')
                col.operator('pbr.oak_wood_operator')
                col.operator('pbr.moss_wood_operator')
                col.operator('pbr.mp_wood_operator')
                col.operator('pbr.sk_wood_operator')


#дерево іви
class PBR_WILLOWWOOD(PBRMaterialOperator):
    bl_label = "Willow wood"
    bl_idname = 'pbr.wl_wood_operator'
    material_name = "Willow wood"
    texture_folder = 'PBR/Tree wood/Willow wood'
    texture_node_location = (-900, 380)
    
    def execute(self, context):
        super().execute(context)
        # Завантаження текстур
        base_color_tex = self.load_texture('bark_willow_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('bark_willow_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('bark_willow_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('bark_willow_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        
        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        # Лінкінг Image Texture нод до mapping
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])

        # Лінкінг texture coordinate до mapping
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}


#дерево дуба
class PBR_OAKWOOD(PBRMaterialOperator):
    bl_label = "Oak wood"
    bl_idname = 'pbr.oak_wood_operator'
    material_name = "Oak wood"
    texture_folder = 'PBR/Tree wood/Oak wood'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('bark_oak_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('bark_oak_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('bark_oak_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('bark_oak_normal_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
    
#дерево з мхом
class PBR_MOSSWOOD(PBRMaterialOperator):
    bl_label = "Moss wood"
    bl_idname = 'pbr.moss_wood_operator'
    material_name = "Moss wood"
    texture_folder = 'PBR/Tree wood/Moss wood'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('bark_brown_02_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('bark_brown_02_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('bark_brown_02_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('bark_brown_02_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])              
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#дерево клену
class PBR_MAPLEWOOD(PBRMaterialOperator):
    bl_label = "Maple wood"
    bl_idname = 'pbr.mp_wood_operator'
    material_name = "Maple wood"
    texture_folder = 'PBR/Tree wood/Maple wood'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('maple_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('maple_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('maple_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('maple_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])     
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}                  

#дерево сакури
class PBR_SAKURAWOOD(PBRMaterialOperator):
    bl_label = "Sakura wood"
    bl_idname = 'pbr.sk_wood_operator'
    material_name = "Sakura wood"
    texture_folder = 'PBR/Tree wood/Sakura wood'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('sakura_bark_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('sakura_bark_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('sakura_bark_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('sakura_bark_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])     
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

####################
####################
#Підпанель Wooden structs        
class pbrWoodStructs(bpy.types.Panel):
            bl_label = "Wooden structs"
            bl_idname = "PT_PBR_WOODSTRUCTSPANEL"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                col.operator('pbr.raw_planks_operator')
                col.operator('pbr.wd_door_operator')
                col.operator('pbr.lm1_planks_operator')
                col.operator('pbr.lm2_planks_operator')
                col.operator('pbr.wd_shelf_operator')
                
#сирі дошки
class PBR_RAW_PLANKS(PBRMaterialOperator):
    bl_label = "Raw planks"
    bl_idname = 'pbr.raw_planks_operator'
    material_name = "Raw planks"
    texture_folder = 'PBR/Wooden structs/Raw planks'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('raw_plank_wall_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('raw_plank_wall_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('raw_plank_wall_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('raw_plank_wall_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#дерев'яні двері 
class PBR_WOOD_DOOR(PBRMaterialOperator):
    bl_label = "Wooden door"
    bl_idname = 'pbr.wd_door_operator'
    material_name = "Raw planks"
    texture_folder = 'PBR/Wooden structs/Wooden door'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('wooden_garage_door_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('wooden_garage_door_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('wooden_garage_door_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('wooden_garage_door_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        
        self.mapping.inputs[3].default_value[0] = 4.5
        self.mapping.inputs[3].default_value[1] = 4.5
        self.mapping.inputs[3].default_value[2] = 4.5
        return {'FINISHED'}
    
#ламінат крупний
class PBR_LAMINATE_1(PBRMaterialOperator):
    bl_label = "Laminate 1"
    bl_idname = 'pbr.lm1_planks_operator'
    material_name = "Laminate 1"
    texture_folder = 'PBR/Wooden structs/Laminate 1'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('laminate_floor_03_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('laminate_floor_03_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('laminate_floor_03_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('laminate_floor_03_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#ламінат мілкий
class PBR_LAMINATE_2(PBRMaterialOperator):
    bl_label = "Laminate 2"
    bl_idname = 'pbr.lm2_planks_operator'
    material_name = "Laminate 2"
    texture_folder = 'PBR/Wooden structs/Laminate 2'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('laminate_floor_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('laminate_floor_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('laminate_floor_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('laminate_floor_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#дерев'яна полиця
class PBR_WOOD_SHELF(PBRMaterialOperator):
    bl_label = "Wooden shelf"
    bl_idname = 'pbr.wd_shelf_operator'
    material_name = "Wooden shelf"
    texture_folder = 'PBR/Wooden structs/Wooden shelf'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('wood_table_001_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('wood_table_001_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('wood_table_001_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('wood_table_001_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}


####################
####################
#Підпанель Terrain       
class pbrTerrain(bpy.types.Panel):
            bl_label = "Terrain"
            bl_idname = "PT_PBR_TERRAIN"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                
                col.operator('pbr.moss_ground_operator')
                col.operator('pbr.forest_ground_operator')
                col.operator('pbr.fall_leaves_operator')
                col.operator('pbr.st_dirt_operator')
                col.operator('pbr.bh_sand_operator')
               

#земля з мхом
class PBR_MOSSY_GROUND(PBRMaterialOperator):
    bl_label = "Mossy ground"
    bl_idname = 'pbr.moss_ground_operator'
    material_name = "Mossy ground"
    texture_folder = 'PBR/Terrain/Mossy ground'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('coast_sand_rocks_02_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('coast_sand_rocks_02_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('coast_sand_rocks_02_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('coast_sand_rocks_02_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#лісовий ландшафт
class PBR_FOREST_GROUND(PBRMaterialOperator):
    bl_label = "Forest ground"
    bl_idname = 'pbr.forest_ground_operator'
    material_name = "Forest ground"
    texture_folder = 'PBR/Terrain/Forest ground'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('forest_leaves_04_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('forest_leaves_04_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('forest_leaves_04_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('forest_leaves_04_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#опале листя
class PBR_FALLEN_LEAVES(PBRMaterialOperator):
    bl_label = "Fallen leaves"
    bl_idname = 'pbr.fall_leaves_operator'
    material_name = "Fallen leaves"
    texture_folder = 'PBR/Terrain/Fallen leaves'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('forest_floor_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('forest_floor_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('forest_floor_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('forest_floor_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#бруд з камінням
class PBR_STONY_DIRT(PBRMaterialOperator):
    bl_label = "Stony dirt"
    bl_idname = 'pbr.st_dirt_operator'
    material_name = "Stony dirts"
    texture_folder = 'PBR/Terrain/Stony dirt'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('stony_dirt_path_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('stony_dirt_path_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('stony_dirt_path_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('stony_dirt_path_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#пляжний пісок
class PBR_BEACH_SAND(PBRMaterialOperator):
    bl_label = "Beach sand"
    bl_idname = 'pbr.bh_sand_operator'
    material_name = "Beach sand"
    texture_folder = 'PBR/Terrain/Beach sand'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('aerial_beach_01_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('aerial_beach_01_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('aerial_beach_01_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('aerial_beach_01_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

####################
####################
#Підпанель Concrete      
class pbrConcrete(bpy.types.Panel):
            bl_label = "Concrete"
            bl_idname = "PT_PBR_CONCRETE"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                
                col.operator('pbr.asphalt1_operator')
                col.operator('pbr.asphalt2_operator')
                col.operator('pbr.conc_plates_operator')
                col.operator('pbr.pn_pavers_operator')
                col.operator('pbr.pavement_operator')
                

#асфальт чистий
class PBR_ASPHALT_1(PBRMaterialOperator):
    bl_label = "Asphalt 1"
    bl_idname = 'pbr.asphalt1_operator'
    material_name = "Asphalt 1"
    texture_folder = 'PBR/Concrete/Asphalt 1'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('asphalt_01_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('asphalt_01_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('asphalt_01_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('asphalt_01_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#асфальт зі слідом
class PBR_ASPHALT_2(PBRMaterialOperator):
    bl_label = "Asphalt 2"
    bl_idname = 'pbr.asphalt2_operator'
    material_name = "Asphalt 2"
    texture_folder = 'PBR/Concrete/Asphalt 2'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('aerial_asphalt_01_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('aerial_asphalt_01_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('aerial_asphalt_01_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('aerial_asphalt_01_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#бетонні плити
class PBR_CONCRETE_PALTES(PBRMaterialOperator):
    bl_label = "Concrete paltes"
    bl_idname = 'pbr.conc_plates_operator'
    material_name = "Concrete paltes"
    texture_folder = 'PBR/Concrete/Concrete plates'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('concrete_wall_008_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('concrete_wall_008_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('concrete_wall_008_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('concrete_wall_008_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9])  
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#бетонний патерн
class PBR_PATTERNED_PAVERS(PBRMaterialOperator):
    bl_label = "Pattern pavers"
    bl_idname = 'pbr.pn_pavers_operator'
    material_name = "Pattern pavers"
    texture_folder = 'PBR/Concrete/Pattern pavers'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('worn_patterned_pavers_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('worn_patterned_pavers_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('worn_patterned_pavers_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('worn_patterned_pavers_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#бруківка
class PBR_PAVEMENT(PBRMaterialOperator):
    bl_label = "Pavement"
    bl_idname = 'pbr.pavement_operator'
    material_name = "Pavement"
    texture_folder = 'PBR/Concrete/Pavement'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('pavement_02_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('pavement_02_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('pavement_02_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('pavement_02_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

####################
####################
#Підпанель Bricks      
class pbrBricks(bpy.types.Panel):
            bl_label = "Bricks"
            bl_idname = "PT_PBR_BRICKS"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                
                col.operator('pbr.gray_brick_operator')
                col.operator('pbr.dark_brick_operator')
                col.operator('pbr.oldred_brick_operator')
                col.operator('pbr.stone_slab_operator')
                col.operator('pbr.medieval_operator')
                

#сійра цегла
class PBR_GRAY_BRICK(PBRMaterialOperator):
    bl_label = "Gray brick"
    bl_idname = 'pbr.gray_brick_operator'
    material_name = "Gray brick"
    texture_folder = 'PBR/Bricks/Gray brick'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('pavement_03_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('pavement_03_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('pavement_03_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('pavement_03_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#чорна цегла
class PBR_DARK_BRICK(PBRMaterialOperator):
    bl_label = "Dark brick"
    bl_idname = 'pbr.dark_brick_operator'
    material_name = "Dark brick"
    texture_folder = 'PBR/Bricks/Dark brick'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('dark_brick_wall_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('dark_brick_wall_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('dark_brick_wall_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('dark_brick_wall_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#стара червона цегла
class PBR_OLD_RED_BRICK(PBRMaterialOperator):
    bl_label = "Old red brick"
    bl_idname = 'pbr.oldred_brick_operator'
    material_name = "Old red brick"
    texture_folder = 'PBR/Bricks/Old red brick'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('brick_4_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('brick_4_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('brick_4_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('brick_4_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#стара червона цегла
class PBR_OLD_RED_BRICK(PBRMaterialOperator):
    bl_label = "Old red brick"
    bl_idname = 'pbr.oldred_brick_operator'
    material_name = "Old red brick"
    texture_folder = 'PBR/Bricks/Old red brick'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('brick_4_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('brick_4_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('brick_4_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('brick_4_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

#кам'яна плита
class PBR_STONE_SLAB(PBRMaterialOperator):
    bl_label = "Stone slab"
    bl_idname = 'pbr.stone_slab_operator'
    material_name = "Stone slab"
    texture_folder = 'PBR/Bricks/Stone slab'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('stone_brick_wall_001_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('stone_brick_wall_001_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('stone_brick_wall_001_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('stone_brick_wall_001_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#середньовічні блоки
class PBR_MEDIEVAL(PBRMaterialOperator):
    bl_label = "Medieval blocks"
    bl_idname = 'pbr.medieval_operator'
    material_name = "Medieval blocks"
    texture_folder = 'PBR/Bricks/Medieval blocks'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('medieval_blocks_03_diff_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('medieval_blocks_03_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('medieval_blocks_03_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('medieval_blocks_03_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

####################
####################
#Підпанель Metal     
class pbrMetal(bpy.types.Panel):
            bl_label = "Metal"
            bl_idname = "PT_PBR_METAL"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                
                col.operator('pbr.metal_panel_operator')
                col.operator('pbr.rusty_panel_operator')
                col.operator('pbr.steel_operator')
                col.operator('pbr.ind_steel_operator')
                col.operator('pbr.cor_metal_operator')
                
                
#металева панель
class PBR_METAL_PANEL(PBRMaterialOperator):
    bl_label = "Metal panel"
    bl_idname = 'pbr.metal_panel_operator'
    material_name = "Metal panel"
    texture_folder = 'PBR/Metal/Metal plate'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('metal_plate_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('metal_plate_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('metal_plate_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('metal_plate_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        metal_tex = self.load_texture('metal_plate_metal_1k.png')
        metal_tex.location = (-350, 650)
        
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        metal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(metal_tex.outputs[0], self.principled_bsdf.inputs[6])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], metal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#ржава металева панель
class PBR_RUSTY_PANEL(PBRMaterialOperator):
    bl_label = "Rusty panel"
    bl_idname = 'pbr.rusty_panel_operator'
    material_name = "Metal panel"
    texture_folder = 'PBR/Metal/Rusty panel'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('rusty_metal_sheet_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('rusty_metal_sheet_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('rusty_metal_sheet_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('rusty_metal_sheet_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        metal_tex = self.load_texture('rusty_metal_sheet_arm_1k.png')
        metal_tex.location = (-350, 650)
        
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        metal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(metal_tex.outputs[0], self.principled_bsdf.inputs[6])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], metal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#полірована сталь
class PBR_STEEL(PBRMaterialOperator):
    bl_label = "Polished steel"
    bl_idname = 'pbr.steel_operator'
    material_name = "Polished steel"
    texture_folder = 'PBR/Metal/Polished steel'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('MetalSteelBrushed001_COL_2K_METALNESS.png')
        base_color_tex.location = (-900, 380)
        roughness_tex = self.load_texture('MetalSteelBrushed001_ROUGHNESS_2K_METALNESS.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('MetalSteelBrushed001_NRM_2K_METALNESS.png')
        normal_tex.location = (-600, -250)
        metal_tex = self.load_texture('MetalSteelBrushed001_METALNESS_2K_METALNESS.png')
        metal_tex.location = (-350, 650)
        
        
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        metal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(metal_tex.outputs[0], self.principled_bsdf.inputs[6])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], metal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
                
#індустріальна сталь
class PBR_IND_STEEL(PBRMaterialOperator):
    bl_label = "Industrial steel"
    bl_idname = 'pbr.ind_steel_operator'
    material_name = "Industrial steel"
    texture_folder = 'PBR/Metal/Industrial steel'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('MetalGalvanizedSteelWorn001_COL_2K_METALNESS.jpg')
        base_color_tex.location = (-900, 380)
        roughness_tex = self.load_texture('MetalGalvanizedSteelWorn001_ROUGHNESS_2K_METALNESS.jpg')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('MetalGalvanizedSteelWorn001_NRM_2K_METALNESS.jpg')
        normal_tex.location = (-600, -250)
        metal_tex = self.load_texture('MetalGalvanizedSteelWorn001_METALNESS_2K_METALNESS.jpg')
        metal_tex.location = (-350, 650)
        
        
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        metal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(metal_tex.outputs[0], self.principled_bsdf.inputs[6])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], metal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#метал з корозією
class PBR_CORRODED_METAL(PBRMaterialOperator):
    bl_label = "Corroded metal"
    bl_idname = 'pbr.cor_metal_operator'
    material_name = "Corroded metal"
    texture_folder = 'PBR/Metal/Corroded metal'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('MetalCorrodedHeavy001_COL_2K_METALNESS.jpg')
        base_color_tex.location = (-900, 380)
        roughness_tex = self.load_texture('MetalCorrodedHeavy001_ROUGHNESS_2K_METALNESS.jpg')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('MetalCorrodedHeavy001_NRM_2K_METALNESS.jpg')
        normal_tex.location = (-600, -250)
        metal_tex = self.load_texture('MetalCorrodedHeavy001_METALNESS_2K_METALNESS.jpg')
        metal_tex.location = (-350, 650)
        
        
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'
        metal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        self.pbr_material.node_tree.links.new(metal_tex.outputs[0], self.principled_bsdf.inputs[6])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], metal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}

####################
####################
#Підпанель Fabric     
class pbrFabric(bpy.types.Panel):
            bl_label = "Fabric"
            bl_idname = "PT_PBR_FABRIC"
            bl_parent_id = "PT_PBR_MAINPANEL"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = 'QuickShader'
            bl_options = {'DEFAULT_CLOSED'}

            def draw(self, context):
                layout = self.layout
                layout.scale_y = 1.2
        
                row = layout.row()
                col = layout.column()
                
                col.operator('pbr.leather_operator')
                col.operator('pbr.denim_operator')
                col.operator('pbr.fabric_operator')
                col.operator('pbr.fabric_pat1_operator')
                col.operator('pbr.fabric_pat2_operator')    
                
                
#шкіра
class PBR_LEATER(PBRMaterialOperator):
    bl_label = "Leather"
    bl_idname = 'pbr.leather_operator'
    material_name = "Leather"
    texture_folder = 'PBR/Fabric/Leather'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('brown_leather_albedo_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('brown_leather_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('brown_leather_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('brown_leather_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#джинсовий матеріал
class PBR_DENIM(PBRMaterialOperator):
    bl_label = "Denim"
    bl_idname = 'pbr.denim_operator'
    material_name = "Denim"
    texture_folder = 'PBR/Fabric/Denim'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('denmin_fabric_02_diff_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('denmin_fabric_02_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('denmin_fabric_02_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('denmin_fabric_02_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#тканина
class PBR_FABRIC(PBRMaterialOperator):
    bl_label = "Fabric"
    bl_idname = 'pbr.fabric_operator'
    material_name = "Fabric"
    texture_folder = 'PBR/Fabric/Fabric material'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('book_pattern_col1_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('book_pattern_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('book_pattern_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('book_pattern_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        return {'FINISHED'}
    
#тканиний патерн 1
class PBR_FABRIC_PATTERN_1(PBRMaterialOperator):
    bl_label = "Fabric pattern 1"
    bl_idname = 'pbr.fabric_pat1_operator'
    material_name = "Fabric pattern 1"
    texture_folder = 'PBR/Fabric/Fabric pattern 1'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('fabric_pattern_05_col_01_2k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('fabric_pattern_05_ao_2k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('fabric_pattern_05_rough_2k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('fabric_pattern_05_nor_gl_2k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])
        
        self.mapping.inputs[3].default_value[0] = 4
        self.mapping.inputs[3].default_value[1] = 4
        self.mapping.inputs[3].default_value[2] = 4
        
        return {'FINISHED'}
    
#тканиний патерн 2
class PBR_FABRIC_PATTERN_2(PBRMaterialOperator):
    bl_label = "Fabric pattern 2"
    bl_idname = 'pbr.fabric_pat2_operator'
    material_name = "Fabric pattern 2"
    texture_folder = 'PBR/Fabric/Fabric pattern 2'
    texture_node_location = (-900, 380)
    def execute(self, context):
        super().execute(context)

        # Завантаження текстур
        base_color_tex = self.load_texture('fabric_pattern_07_col_1_1k.png')
        base_color_tex.location = (-900, 380)
        ambient_oc_tex = self.load_texture('fabric_pattern_07_ao_1k.png')
        ambient_oc_tex.location = (-1250, 80)
        roughness_tex = self.load_texture('fabric_pattern_07_rough_1k.png')
        roughness_tex.location = (-900, -100)
        normal_tex = self.load_texture('fabric_pattern_07_nor_gl_1k.png')
        normal_tex.location = (-600, -250)
        
        ambient_oc_tex.image.colorspace_settings.name = 'Non-Color'
        roughness_tex.image.colorspace_settings.name = 'Non-Color'
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        # Отримання вузлів з батьківського класу
        self.pbr_material.node_tree.links.new(base_color_tex.outputs[0], self.mix_node.inputs[1])
        self.pbr_material.node_tree.links.new(ambient_oc_tex.outputs[0], self.ao_node.inputs[0])
        self.pbr_material.node_tree.links.new(roughness_tex.outputs[0], self.principled_bsdf.inputs[9]) 
        self.pbr_material.node_tree.links.new(normal_tex.outputs[0], self.normal_map.inputs[1])
        
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], base_color_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], ambient_oc_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], roughness_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.mapping.outputs[0], normal_tex.inputs[0])
        self.pbr_material.node_tree.links.new(self.texture_coord.outputs[2], self.mapping.inputs[0])        
        return {'FINISHED'}
                 
def register():
    #Головні панелі
    bpy.utils.register_class(ModifierPanel)
    bpy.utils.register_class(ShaderPanel)
    bpy.utils.register_class(PBRPanel)
    #кнопка видалення матеріалу
    bpy.utils.register_class(RemoveMaterialOperator)
        
    #регістер підпанелей ShaderPanel
    bpy.utils.register_class(GlassPanel)
    bpy.utils.register_class(MetalicPanel)
    bpy.utils.register_class(EmissionPanel)
        
    #регістер підпанелей PBRPanel
    bpy.utils.register_class(pbrWoodPanel)
    bpy.utils.register_class(pbrWoodStructs)
    bpy.utils.register_class(pbrTerrain)
    bpy.utils.register_class(pbrConcrete)
    bpy.utils.register_class(pbrBricks)
    bpy.utils.register_class(pbrMetal)
    bpy.utils.register_class(pbrFabric)
    
    #Шейдери
    #шейдери скла
    bpy.utils.register_class(SHADER_GLASS)
    bpy.utils.register_class(SHADER_TRANPARENT_GLASS)
    bpy.utils.register_class(SHADER_MOSAIC_GLASS)    
    #шейдери металів
    bpy.utils.register_class(SHADER_GOLD)
    bpy.utils.register_class(SHADER_ALUMINIUM)
    bpy.utils.register_class(SHADER_COPPER)
    bpy.utils.register_class(SHADER_STEEL)
    #шейдери освіщення
    bpy.utils.register_class(SHADER_ADD_EMITER)
                 
    #PBR-матеріали
    #Батьківський основний клас
    bpy.utils.register_class(PBRMaterialOperator)
    #Tree wood#      
    bpy.utils.register_class(PBR_WILLOWWOOD)
    bpy.utils.register_class(PBR_OAKWOOD)
    bpy.utils.register_class(PBR_MOSSWOOD)
    bpy.utils.register_class(PBR_MAPLEWOOD)
    bpy.utils.register_class(PBR_SAKURAWOOD)
    #Wooden structs
    bpy.utils.register_class(PBR_RAW_PLANKS)
    bpy.utils.register_class(PBR_WOOD_DOOR)
    bpy.utils.register_class(PBR_LAMINATE_1)
    bpy.utils.register_class(PBR_LAMINATE_2)
    bpy.utils.register_class(PBR_WOOD_SHELF) 
    #Terrain
    bpy.utils.register_class(PBR_MOSSY_GROUND) 
    bpy.utils.register_class(PBR_FOREST_GROUND)
    bpy.utils.register_class(PBR_FALLEN_LEAVES)
    bpy.utils.register_class(PBR_STONY_DIRT)
    bpy.utils.register_class(PBR_BEACH_SAND)
    #Concrete
    bpy.utils.register_class(PBR_ASPHALT_1)
    bpy.utils.register_class(PBR_ASPHALT_2)
    bpy.utils.register_class(PBR_CONCRETE_PALTES)
    bpy.utils.register_class(PBR_PATTERNED_PAVERS)
    bpy.utils.register_class(PBR_PAVEMENT)
    #Bricks
    bpy.utils.register_class(PBR_GRAY_BRICK)
    bpy.utils.register_class(PBR_DARK_BRICK)
    bpy.utils.register_class(PBR_OLD_RED_BRICK)
    bpy.utils.register_class(PBR_STONE_SLAB)
    bpy.utils.register_class(PBR_MEDIEVAL)
    #Metal
    bpy.utils.register_class(PBR_METAL_PANEL)
    bpy.utils.register_class(PBR_RUSTY_PANEL)
    bpy.utils.register_class(PBR_STEEL)
    bpy.utils.register_class(PBR_IND_STEEL)
    bpy.utils.register_class(PBR_CORRODED_METAL)
    #Fabric
    bpy.utils.register_class(PBR_LEATER)
    bpy.utils.register_class(PBR_DENIM)
    bpy.utils.register_class(PBR_FABRIC)
    bpy.utils.register_class(PBR_FABRIC_PATTERN_1)
    bpy.utils.register_class(PBR_FABRIC_PATTERN_2)


def unregister():
    # Головні панелі
    bpy.utils.unregister_class(ModifierPanel)
    bpy.utils.unregister_class(ShaderPanel)
    bpy.utils.unregister_class(PBRPanel)
    # кнопка видалення матеріалу
    bpy.utils.unregister_class(RemoveMaterialOperator)

    # регістер підпанелей ShaderPanel
    bpy.utils.unregister_class(GlassPanel)
    bpy.utils.unregister_class(MetalicPanel)
    bpy.utils.unregister_class(EmissionPanel)

    # регістер підпанелей PBRPanel
    bpy.utils.unregister_class(pbrWoodPanel)
    bpy.utils.unregister_class(pbrWoodStructs)
    bpy.utils.unregister_class(pbrTerrain)
    bpy.utils.unregister_class(pbrConcrete)
    bpy.utils.unregister_class(pbrBricks)
    bpy.utils.unregister_class(pbrMetal)
    bpy.utils.unregister_class(pbrFabric)

    # Шейдери
    # шейдери скла
    bpy.utils.unregister_class(SHADER_GLASS)
    bpy.utils.unregister_class(SHADER_TRANPARENT_GLASS)
    bpy.utils.unregister_class(SHADER_MOSAIC_GLASS)
    # шейдери металів
    bpy.utils.unregister_class(SHADER_GOLD)
    bpy.utils.unregister_class(SHADER_ALUMINIUM)
    bpy.utils.unregister_class(SHADER_COPPER)
    bpy.utils.unregister_class(SHADER_STEEL)
    # шейдери освіщення
    bpy.utils.unregister_class(SHADER_ADD_EMITER)

    # PBR-матеріали
    # Батьківський основний клас
    bpy.utils.unregister_class(PBRMaterialOperator)
    # Tree wood#
    bpy.utils.unregister_class(PBR_WILLOWWOOD)
    bpy.utils.unregister_class(PBR_OAKWOOD)
    bpy.utils.unregister_class(PBR_MOSSWOOD)
    bpy.utils.unregister_class(PBR_MAPLEWOOD)
    bpy.utils.unregister_class(PBR_SAKURAWOOD)
    # Wooden structs
    bpy.utils.unregister_class(PBR_RAW_PLANKS)
    bpy.utils.unregister_class(PBR_WOOD_DOOR)
    bpy.utils.unregister_class(PBR_LAMINATE_1)
    bpy.utils.unregister_class(PBR_LAMINATE_2)
    bpy.utils.unregister_class(PBR_WOOD_SHELF)
    # Terrain
    bpy.utils.unregister_class(PBR_MOSSY_GROUND)
    bpy.utils.unregister_class(PBR_FOREST_GROUND)
    bpy.utils.unregister_class(PBR_FALLEN_LEAVES)
    bpy.utils.unregister_class(PBR_STONY_DIRT)
    bpy.utils.unregister_class(PBR_BEACH_SAND)
    # Concrete
    bpy.utils.unregister_class(PBR_ASPHALT_1)
    bpy.utils.unregister_class(PBR_ASPHALT_2)
    bpy.utils.unregister_class(PBR_CONCRETE_PALTES)
    bpy.utils.unregister_class(PBR_PATTERNED_PAVERS)
    bpy.utils.unregister_class(PBR_PAVEMENT)
    # Bricks
    bpy.utils.unregister_class(PBR_GRAY_BRICK)
    bpy.utils.unregister_class(PBR_DARK_BRICK)
    bpy.utils.unregister_class(PBR_OLD_RED_BRICK)
    bpy.utils.unregister_class(PBR_STONE_SLAB)
    bpy.utils.unregister_class(PBR_MEDIEVAL)
    # Metal
    bpy.utils.unregister_class(PBR_METAL_PANEL)
    bpy.utils.unregister_class(PBR_RUSTY_PANEL)
    bpy.utils.unregister_class(PBR_STEEL)
    bpy.utils.unregister_class(PBR_IND_STEEL)
    bpy.utils.unregister_class(PBR_CORRODED_METAL)
    # Fabric
    bpy.utils.unregister_class(PBR_LEATER)
    bpy.utils.unregister_class(PBR_DENIM)
    bpy.utils.unregister_class(PBR_FABRIC)
    bpy.utils.unregister_class(PBR_FABRIC_PATTERN_1)
    bpy.utils.unregister_class(PBR_FABRIC_PATTERN_2)

if __name__ == "__main__":
    register()