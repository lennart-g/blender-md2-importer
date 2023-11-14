bl_info = {
    "name": "Experimental MD2 Importer",
    "author": "Lennart G",
    "location": "File > Import > Quake 2 (.md2)",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export"
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
    import importlib
    try:
        importlib.reload(MD2)
    except NameError:
        from util import MD2
        importlib.reload(MD2)

    try:
        importlib.reload(prepare_skin_paths)
    except NameError:
        from util import prepare_skin_paths
        importlib.reload(prepare_skin_paths)
    from . import blender_load_md2
    importlib.reload(blender_load_md2)
    print("Reloaded multifiles")
else:
    from . import blender_load_md2
    print("Imported multifiles")

"""
This part is required for the UI, to make the Addon appear under File > Import once it's
activated and to have additional input fields in the file picking menu
Code is taken from Templates > Python > Operator File Import in Text Editor
The code here calls blender_load_md2
"""

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
import bpy  # noqa: E402
from bpy_extras.io_utils import ImportHelper  # noqa: E402


class ImportSomeData(bpy.types.Operator, ImportHelper):
    """Loads a Quake 2 MD2 File"""
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "import_md2.some_data"
    bl_label = "Import MD2"

    # ImportHelper mixin class uses this
    # filename_ext = ".md2"

    # the following type annotations ignore linter complaints because the properties are
    # defined in C code and thus not accessible to the linter
    filter_glob: bpy.props.StringProperty(
        default="*.*",  # only shows md2 files in opening screen  # noqa: F722
        options={'HIDDEN'},  # noqa: F722 F821
        maxlen=255,  # Max internal buffer length, longer would be clamped.  # noqa: F722
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    displayed_name: bpy.props.StringProperty(
        name="Displayed name",  # noqa: F722
        description=(
            "What this model should be named in the outliner\n"  # noqa: F722
            "good for default file names like tris.md2"
        ),
        default="",  # noqa: F722
        maxlen=1024
    )

    use_custom_skin: bpy.props.BoolProperty(
        name="Load custom skin: ",  # noqa: F722
        description=(
            "To load a skin from a path different to the one stored in the .md2."  # noqa: F722
        ),
        default=False,
    )
    custom_skin_path: bpy.props.StringProperty(
        name="Optional: skin path",  # noqa: F722
        description="If load custom skin checked: path to skin to load.",  # noqa: F722
        default="",  # noqa: F722
        maxlen=1024,
    )

    def execute(self, context):
        return blender_load_md2.blender_load_md2(
            self.filepath, self.displayed_name, self.use_custom_skin, self.custom_skin_path)


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
