bl_info = {
    "name": "Experimental MD2 Importer",
    "author": "Lennart G",
    "location": "File > Import > Quake 2 (.md2)",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export"
}


from dataclasses import dataclass
import struct
from typing import List
"""
This part is used to load an md2 file into a MD2 dataclass object
"""
""" 
Dataclasses resembling structs in C. Used for storing MD2 information, being nested and forming one big dataclass
"""

@dataclass
class vec3_t:
    x: float
    y: float
    z: float


@dataclass
class vertex_t:  # 4 bytes in total
    v: list  # unsigned char (in python 1 byte int), list of len 3, compressed vertex
    lightnormalindex: int  # unsigned char, index to a normal vector for the lighting


@dataclass
class frame_t:  # 40 + num_xyz*4 bytes
    scale: vec3_t  # scale values, 3 elements
    translate: vec3_t  # translation vector, 3 elements
    name: str  # frame name, 16 characters aka bytes at most
    verts: List[vertex_t]  # list of num_xyz vertex_t's


@dataclass
class md2_t:
    ident: int              # magic number. must be equal to "IDP2" or 844121161 as int
    version: int            # md2 version. must be equal to 8

    skinwidth: int          # width of the texture
    skinheight: int         # height of the texture
    framesize: int          # size of one frame in bytes

    num_skins: int          # number of textures
    num_xyz: int            # number of vertices
    num_st: int             # number of texture coordinates
    num_tris: int           # number of triangles
    num_glcmds: int         # number of opengl commands
    num_frames: int         # total number of frames

    ofs_skins: int          # offset to skin names (64 bytes each)
    ofs_st: int             # offset to s-t texture coordinates
    ofs_tris: int           # offset to triangles
    ofs_frames: int         # offset to frame data
    ofs_glcmds: int         # offset to opengl commands
    ofs_end: int            # offset to end of file


@dataclass
class triangle_t:  # 12 bytes each
    vertexIndices: List[int]  # short, 3 values
    textureIndices: List[int]  # short, 3 values


@dataclass
class textureCoordinate_t: # 4 bytes each
    s: int  # short
    t: int  # short


@dataclass
class glCommandVertex_t:
    s: float
    t: float
    vertexIndex: int


@dataclass
class glCommand_t:
    mode: str  # string saying GL_TRIANGLE_STRIP or GL_TRIANGLE_FAN
    vertices: List[glCommandVertex_t]  # all vertices rendered with said mode


@dataclass
class md2_object:
    header: md2_t
    skin_names: List[str]
    triangles: List[triangle_t]
    frames: List[frame_t]
    texture_coordinates: List[textureCoordinate_t]
    gl_commands: List[glCommand_t]

"""
Functions used to create an MD2 Object
"""
def load_gl_commands(gl_command_bytes):
    """
    Loads gl_commands which are a list of GL_TRIANGLE_STRIP and GL_TRIANGLE_FAN calls that reduce fps
    Code differs much from original loading code in C
    :param gl_command_bytes: bytes belonging to gl_commands lump from md2 file
    :return: list of dataclasses storing gl commands
    """
    offset = 0
    gl_commands = list()
    while True:  # ends when mode is 0
        (mode,) = struct.unpack("<i", gl_command_bytes[offset:offset+4])
        num_verts = abs(mode)
        if mode > 0:
            mode = "GL_TRIANGLE_STRIP"
        elif mode == 0:
            offset += 4
            break
        else:
            mode = "GL_TRIANGLE_FAN"
        offset += 4
        gl_vertices = list()
        for i in range(num_verts):
            s_and_t = struct.unpack("<ff", gl_command_bytes[offset+12*i:offset+12*i+8])
            vertex_index = struct.unpack("<i", gl_command_bytes[offset+12*i+8:offset+12*i+12])
            gl_vertices.append(glCommandVertex_t(*s_and_t, *vertex_index))
        # print(gl_vertices)
        offset += 12*num_verts
        gl_commands.append(glCommand_t(mode, gl_vertices))
    return gl_commands


def load_triangles(triangle_bytes, header):
    """
    Creates basic list of triangle dataclasses which contain indices to vertices
    :param triangle_bytes: bytes from md2 file belonging to triangles lump
    :param header: dataclass containing header information
    :return: list of triangles
    """
    triangles = list()
    for i in range(header.num_tris):
        triangle = triangle_t(list(struct.unpack("<hhh", triangle_bytes[12*i:12*i+6])), list(struct.unpack("<hhh", triangle_bytes[12*i+6:12*i+12])))
        # print(triangle)
        triangles.append(triangle)
    return triangles


def load_frames(frames_bytes, header):
    """
    Loads frames
    :param frames_bytes: bytes from md2 file belonging to frames lump
    :param header: header dataclass
    :return: list of frame dataclass objects
    """
    # # check if header.ofs_glcmds - header.ofs_frames == header.num_frames*(40+4*header.num_xyz) # #
    # print("len", len(frames_bytes))
    # print("frames", header.num_frames)
    # print("check", header.num_frames*(40+4*header.num_xyz))

    frames = list()
    for current_frame in range(header.num_frames):
        scale = vec3_t(*struct.unpack("<fff", frames_bytes[(40+4*header.num_xyz)*current_frame:(40+4*header.num_xyz)*current_frame+12]))
        translate = vec3_t(*struct.unpack("<fff", frames_bytes[(40+4*header.num_xyz)*current_frame+12:(40+4*header.num_xyz)*current_frame+24]))
        name = frames_bytes[(40+4*header.num_xyz)*current_frame+24:(40+4*header.num_xyz)*current_frame+40].decode("ascii", "ignore")
        verts = list()
        for v in range(header.num_xyz):
            # print(v)
            verts.append(vertex_t(list(struct.unpack("<BBB", frames_bytes[(40+4*header.num_xyz)*current_frame+40+v*4:(40+4*header.num_xyz)*current_frame+40+v*4+3])), *struct.unpack("<B", frames_bytes[(40+4*header.num_xyz)*current_frame+43+v*4:(40+4*header.num_xyz)*current_frame+44+v*4])))  # list() only for matching expected type
        # print(scale, translate, name, verts)
        frame = frame_t(scale, translate, name, verts)
        # print(frame)
        frames.append(frame)
    return frames


def load_header(file_bytes):
    """
    Creates header dataclass object
    :param file_bytes: bytes from md2 file belonging to header
    :return: header dataclass object
    """
    # print(file_bytes[:4].decode("ascii", "ignore"))
    arguments = struct.unpack("<iiiiiiiiiiiiiiiii", file_bytes[:68])
    header = md2_t(*arguments)
    # Verify MD2
    if not header.ident == 844121161 or not header.version == 8:
        print(f"Error: File type is not MD2. Ident or version not matching")
        print(f'Ident: {file_bytes[:4].decode("ascii", "ignore")} should be "IDP2"')
        print(f"Version: {header.version} should be 8")
    return header


def load_texture_coordinates(texture_coordinate_bytes, header):
    """
    Loads UV (in Q2 term ST) coordinates
    :param texture_coordinate_bytes:
    :param header:
    :return: list of texture coordinate dataclass objects
    """
    texture_coordinates = list()
    for i in range(header.num_st):
        texture_coordinates.append(textureCoordinate_t(*struct.unpack("<hh", texture_coordinate_bytes[4*i:4*i+4])))
    return texture_coordinates


def load_file(path):
    """
    Master function returning one dataclass object containing all the MD2 information
    :param path:
    :return:
    """
    with open(path, "rb") as f:  # bsps are binary files
        byte_list = f.read()  # stores all bytes in bytes1 variable (named like that to not interfere with builtin names
    header = load_header(byte_list)
    skin_names = [byte_list[header.ofs_skins + 64 * x:header.ofs_skins + 64 * x + 64].decode("ascii", "ignore") for x in range(header.num_skins)]
    triangles = load_triangles(byte_list[header.ofs_tris:header.ofs_frames], header)
    frames = load_frames(byte_list[header.ofs_frames:header.ofs_glcmds], header)
    texture_coordinates = load_texture_coordinates(byte_list[header.ofs_st:header.ofs_tris], header)
    gl_commands = load_gl_commands(byte_list[header.ofs_glcmds:header.ofs_end])
    # print(header)
    # print(skin_names)
    # print(triangles)
    # print(frames)
    # print(texture_coordinates)
    for i in range(len(texture_coordinates)):
        texture_coordinates[i].s = texture_coordinates[i].s/header.skinwidth
        texture_coordinates[i].t = texture_coordinates[i].t / header.skinheight
    # print(texture_coordinates)
    # print(header.num_xyz)
    for i_frame in range(len(frames)):
        for i_vert in range((header.num_xyz)):
            frames[i_frame].verts[i_vert].v[0] = frames[i_frame].verts[i_vert].v[0]*frames[i_frame].scale.x+frames[i_frame].translate.x
            frames[i_frame].verts[i_vert].v[1] = frames[i_frame].verts[i_vert].v[1] * frames[i_frame].scale.y + frames[i_frame].translate.y
            frames[i_frame].verts[i_vert].v[2] = frames[i_frame].verts[i_vert].v[2] * frames[i_frame].scale.z + frames[i_frame].translate.z
    model = md2_object(header, skin_names, triangles, frames, texture_coordinates, gl_commands)
    return model


import bpy
import sys
from importlib import reload # required when a self-written module is imported that's edited simultaneously
from PIL import Image, ImageFile
import os  # for checking if skin pathes exist


def blender_load_md2(md2_path, displayed_name, use_custom_md2_skin, custom_md2_skin_path):
    """
    This function uses the information from a md2 dataclass into a blender object.
    This will consist of an animated mesh and its material (which is not much more than the texture.
    For better understanding, steps are:
        - Create the MD2 object containing all information that's inside the loaded md2
        - Get the absolute path of the UV map / skin to load
        - Get necessary information about the mesh (vertices, tris, uv coordinates)
        - Create the scene structure and create the mesh for the first frame
        - Assign UV coordinates to each triangle
        - Create shape animation (Add keyframe to each vertex)
        - Assign skin to mesh
    """
    """ Create MD2 dataclass object """
    # ImageFile.LOAD_TRUNCATED_IMAGES = True # Necessary for loading jpgs with PIL

    object_path = md2_path  # Kept for testing purposes
    # A dataclass containing all information stored in a .md2 file
    my_object = load_file(object_path)
    
    
    """ Create skin path. By default, the one stored inside of the MD2 is used. Some engines like the Digital Paintball 2 one
    check for any image file with that path disregarding the file extension. For a given custom path, it is checked
    whether it (apparently) is an absolute or relative (to the MD2) path.
    """
    """ get absolute skin path based on input / the one stored inside of the MD2 """
    # check box must be checked (alternatively it could be checked if the input field was empty or not ...)
    if use_custom_md2_skin:
        # an absolute path is recognized by usage of '/' (obviously not perfect detection of an absolute path)
        if "/" in custom_md2_skin_path:
            skin_path = custom_md2_skin_path
        else:
            # take everything before last '/' of MD2 path, add '/' and path of skin in same directory
            custom_abs_path = "/".join(md2_path.split("/")[:-1])+"/"+custom_md2_skin_path
            print(custom_abs_path)
            skin_path = custom_abs_path
    else:
        print("stored path:", my_object.skin_names) # unchanged path or pathes stored in the MD2
        # strings are always stored as 64 bytes, so unused bytes are set to '\x00'
        first_stored_path = my_object.skin_names[0].rstrip("\x00")
        # only first stored path is used since Digital Paintball 2 only uses that one
        first_stored_path = first_stored_path.split("/")[-1]
        print(first_stored_path)
        # absolute path is formed by using the given md2 object path
        absolute_first_stored_path = "/".join(md2_path.split("/")[:-1])+"/"+first_stored_path
        print(absolute_first_stored_path)
        skin_path = absolute_first_stored_path
    
    """ Look for existing file of given name and supported image format """
    supported_image_formats = [".png", ".jpg", ".jpeg", ".tga",".pcx"] # Order doesn't match DP2 image order
    skin_path_unextended = os.path.splitext(skin_path)[0] # remove extension (last one)
    print(skin_path_unextended)
    for format in supported_image_formats:
        if os.path.isfile(skin_path_unextended+format):
            skin_path = skin_path_unextended+format
            break
    print("used skin path", skin_path)

    """ Loads required information for mesh generation and UV mapping from the .md2 file"""
    # Gets name to give to the object and mesh in the outliner
    if not displayed_name:
        object_name = "/".join(object_path.split("/")[-2:]).split(".")[:-1]
        print(object_name)
    else:
        print(displayed_name)
        object_name = [displayed_name]

    # List of vertices [x,y,z] for all frames extracted from the md2 object
    all_verts = [[x.v for x in my_object.frames[y].verts] for y in range(my_object.header.num_frames)]
    # List of vertex indices forming a triangular face
    tris = ([x.vertexIndices for x in my_object.triangles])
    # uv coordinates (in q2 terms st coordinates) for projecting the skin on the model's faces
    # blender flips images upside down when loading so v = 1-t for blender imported images
    uvs_pcx = ([(x.s, x.t) for x in my_object.texture_coordinates]) 
    uvs_others = ([(x.s, 1-x.t) for x in my_object.texture_coordinates]) 
    # blender uv coordinate system originates at lower left

    """ Lots of code (copy and pasted) that creates a mesh and adds it to the scene collection/outlines """
    mesh = bpy.data.meshes.new(*object_name)  # add the new mesh, * extracts string from list
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections.get("Collection")
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # Creates mesh by taking first frame's vertices and connects them via indices in tris
    mesh.from_pydata(all_verts[0], [], tris) 

    """ UV Mapping: Create UV Layer, assign UV coordinates from md2 files for each face to each face's vertices """
    uv_layer=(mesh.uv_layers.new())
    mesh.uv_layers.active = uv_layer

    # add uv coordinates to each polygon (here: triangle since md2 only stores vertices and triangles)
    # note: faces and vertices are stored exactly in the order they were added
    for face_idx, face in enumerate(mesh.polygons):
        for idx, (vert_idx, loop_idx) in enumerate(zip(face.vertices, face.loop_indices)):
            if skin_path.endswith(".pcx"):
                print("PCX LOADED")
                uv_layer.data[loop_idx].uv = uvs_pcx[my_object.triangles[face_idx].textureIndices[idx]]
            else:
                uv_layer.data[loop_idx].uv = uvs_others[my_object.triangles[face_idx].textureIndices[idx]]
                
    """ Create animation for animated models: set keyframe for each vertex in each frame individually """
    # Create keyframes from first to last frame
    for i in range(my_object.header.num_frames):
        for idx,v in enumerate(obj.data.vertices):
            obj.data.vertices[idx].co = all_verts[i][idx]
            v.keyframe_insert('co', frame=i*10)  # parameter index=2 restricts keyframe to dimension

    # insert first keyframe after last one to yield cyclic animation
    for idx,v in enumerate(obj.data.vertices):
        obj.data.vertices[idx].co = all_verts[0][idx]
        v.keyframe_insert('co', frame=60)

    """ Assign skin to mesh: Create material (barely understood copy and paste again) and set the image. 
    Might work by manually setting the textures pixels to the pixels of a PIL.Image if it would actually
    load non-empty .pcx files
    idea/TODO: Write an own pcx loader from scratch ... """
    # Creating material and corresponding notes (see Shading tab)
    mat = bpy.data.materials.new(name="md2_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')

    # if only a pcx version of the desired skin exists, load it via PIL
    # and copy pixels into the materials texture
    # otherwise use blender internal image loader (supporting .png, .jpg and .tga)
    if skin_path.endswith(".pcx"):
        skin = Image.open(skin_path)
        skin.load()
        skin = skin.convert("RGBA")
        skin_rgba = list(skin.getdata())
        print("important", skin_rgba[:40])
        print("path:", skin_path)
        texImage.image = bpy.data.images.new("MyImage", width=skin.size[0], height=skin.size[1])
        texImage.image.pixels = [y for x in skin_rgba for y in x]
    else:
        texImage.image = bpy.data.images.load(skin_path)
    # again copy and paste
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    # Assign it to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    print("YAY NO ERRORS!!")
    return {'FINISHED'} # no idea, seems to be necessary for the UI
        
"""
This part is required for the UI, to make the Addon appear under File > Import once it's
activated and to have additional input fields in the file picking menu
Code is taken from Templates > Python > Operator File Import in Text Editor
The code here calls blender_load_md2
"""

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    """Loads a Quake 2 MD2 File"""
    bl_idname = "import_md2.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import MD2"

    ## ImportHelper mixin class uses this
    #filename_ext = ".md2"

    filter_glob: StringProperty(
        default="*.*", # only shows md2 files in opening screen
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    displayed_name: bpy.props.StringProperty(name="Displayed name",
                                        description="What this model should be named in the outliner\ngood for default file names like tris.md2",
                                        default="",
                                        maxlen=1024)
    
    use_custom_skin: BoolProperty(
        name="Load custom skin: ",
        description="To load a skin from a path different to the one stored in the .md2.",
        default=False,
    )
    custom_skin_path: bpy.props.StringProperty(name="Optional: skin path",
                                        description="If load custom skin checked: path to skin to load.",
                                        default="",
                                        maxlen=1024)

    def execute(self, context):
        return blender_load_md2(self.filepath, self.displayed_name, self.use_custom_skin, self.custom_skin_path)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="WIP Quake 2 Model Import (.md2)")

# called when addon is activated (adds script to File > Import
def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

# called when addon is deactivated (removed script from menu)
def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_md2.some_data('INVOKE_DEFAULT')


