import bpy
import json
from bpy.types import Operator
from bpy.app.handlers import persistent
from bpy.app import driver_namespace
from bpy.app.handlers import depsgraph_update_post
from math import radians

class UnOpenBFifyOperator(Operator):
	"""Remove 'openbf-data' from an object"""
	bl_idname = "object.unopenbfify"
	bl_label = "Remove OpenBF-data"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		active = bpy.context.active_object
		if "openbf-data" in active:
			del active["openbf-data"]
		return {'FINISHED'}

def get_verts_edges(nurbs_object, doRound=False, roundTo=4):
	obj_data = nurbs_object.to_mesh(preserve_all_data_layers=False)
	verts = [v.co for v in obj_data.vertices]

	if doRound:
		for i in range(len(verts)):
			v = verts[i]
			nv = (round(v.x, roundTo), round(v.y, roundTo), round(v.z, roundTo))
			verts[i] = nv
	edges = obj_data.edge_keys

	nurbs_object.to_mesh_clear()
	return verts, edges

def copyDataToCustomProps (active):
	data = {}
	if active.rigid_body != None:
		data["collision"] = {"shape":active.rigid_body.collision_shape, "radius":1}
		data["physics"] = {"mass":active.rigid_body.mass, "friction":active.rigid_body.friction, "restitution":active.rigid_body.restitution,"dynamic":active.rigid_body.enabled}
	if active.type == "CURVE":
		verts, edges = get_verts_edges(active)
		data["path"] = {"verts":verts, "edges":edges}
	elif active.type == "LIGHT":
		data["light"] = {}
		data["light"]["type"] = active.data.type
		data["light"]["intensity"] = active.data.energy / 3.14159
		data["light"]["use_shadow"] = active.data.use_shadow
		data["light"]["decay"] = 2 #Three.js default is 1, 2 is physically correct
		data["light"]["color"] = {"r":active.data.color.r, "g":active.data.color.g, "b":active.data.color.b}
		if active.data.type == "POINT":
			data["light"]["distance"] = active.data.distance
		#elif active.data.type == "SUN":
			#TODO - direction
		elif active.data.type == "SPOT":
			data["light"]["angle"] = radians(active.data.spot_size)
			data["light"]["penumbra"] = active.data.spot_blend
			#TODO - calculate position of light (threejs style) from rotations of blender node
			#data["light"]["position"] = active.location
		#elif active.data.type == "AREA":
			#Unsupported for now
	active["openbf-data"] = json.dumps(data)

class OpenBFifyOperator(Operator):
	"""OpenBF-ify an object (add custom openbf properties if they don't exist)"""
	bl_idname = "object.openbfify"
	bl_label = "OpenBF-ify"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		active = bpy.context.active_object
		
		copyDataToCustomProps(active)
		return {'FINISHED'}

class CustomPropOpenBFPanel(bpy.types.Panel):
	"""Creates a panel in the 'object properties' context of the properties editor"""
	bl_label = "OpenBF"
	bl_idname = "OBJECT_PT_layout"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "object"

	def draw(self, context):
		layout = self.layout
    
		scene = context.scene
		active = bpy.context.active_object
		
		if "openbf-data" in active:
			layout.operator(UnOpenBFifyOperator.bl_idname)
			if active.type == "LIGHT":
				layout.prop(active.data, "type")
				layout.prop(active.data, "energy")
				layout.prop(active.data, "use_shadow")
				layout.prop(active.data, "color")
			elif active.type == "CURVE":
				layout.label(text=" Curve As Mesh Vertices/Edges")
			elif active.type == "MESH":
				if active.rigid_body != None:
					layout.operator("rigidbody.object_remove")
					layout.prop(active.rigid_body, 'collision_shape')
					layout.label(text=" Enabled = Dynamic, Disabled = Static")
					layout.prop(active.rigid_body, "enabled")
					layout.prop(active.rigid_body, 'mass')
					layout.prop(active.rigid_body, 'friction')
					layout.prop(active.rigid_body, 'restitution')
				else:
					layout.operator("rigidbody.object_add")
		else:
			layout.operator(OpenBFifyOperator.bl_idname)

onSceneUpdateKey = "onSceneUpdate"

@persistent
def onSceneUpdate ( dummy ):
	active = bpy.context.active_object
	if "openbf-data" in active:
		copyDataToCustomProps(active)

#If key is in driver
if onSceneUpdateKey in driver_namespace:

	#if listener is in update listeners
	if driver_namespace[onSceneUpdateKey] in depsgraph_update_post:
		print("Listener in listeners")
		#Remove listener
		depsgraph_update_post.remove(driver_namespace[onSceneUpdateKey])

		#Delete the driver for the listener
		del driver_namespace[onSceneUpdateKey]

#Add a new listener
depsgraph_update_post.append(onSceneUpdate)

#Add a driver for the listener
driver_namespace[onSceneUpdateKey] = onSceneUpdate

def register():
	bpy.utils.register_class(CustomPropOpenBFPanel)
	bpy.utils.register_class(OpenBFifyOperator)
	bpy.utils.register_class(UnOpenBFifyOperator)

def unregister():
	bpy.utils.unregister_class(CustomPropOpenBFPanel)
	bpy.utils.unregister_class(OpenBFifyOperator)
	bpy.utils.unregister_class(UnOpenBFifyOperator)

if __name__ == "__main__":
	register()
