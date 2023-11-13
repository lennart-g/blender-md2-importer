import os.path
import shutil

# files to include in the output zip file
files = [
    "util/MD2.py",
    "md2_importer/__init__.py",
    "md2_importer/blender_load_md2.py",
    "util/prepare_skin_paths.py"
]

# intermediary location for the directory to be zipped
dest = "build/io_import_md2"

if os.path.exists("build") and os.path.isdir("build"):
    shutil.rmtree("build")
os.makedirs(dest)

for file in files:
    shutil.copyfile(file, os.path.join(dest, os.path.basename(file)))

# create zip file
shutil.make_archive("blender-md2-importer", 'zip', "build")
