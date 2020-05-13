#Quake 2 MD2 import add-on for Blender 2.8x
This add-on allows importing .md2 model files. This hasn't been
natively supported by [Blender](https://www.blender.org/) for
a decade now. Please note that this add-on is still work
in progress.

##What can this importer (!) do so far?
- load an MD2 object to Blender
- attach a UV map linked in the .md2 file or a custom one
    - supported formats: .png, .jpg, .tga, .pcx
- load and run keyframe animations

##What is missing?
- proper error handling (proper error handling (some .md2 files store broken skin pathes or ones to files that don't exist))
- aligning the animation keyframes to the fps used for the different animations
- .pcx is no longer natively supported by Blender so a different package is used
that loads all skins as grayscale

##Installation
- download the script and follow [this guide](https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Addon-Installation-and-Uninstallation)
- [install PIL (used for loading .pcx files)](https://blender.stackexchange.com/a/122337)

##How to use
The script can be accessed via File > Import:

![Run importer](imgs/run_script.png)

Checking "Load custom skin" allows loading a UV map different
from the one specified in the .md2 file. By entering a 
"displayed name" the object and mesh name in the outliner
is specified.

![Loading options](imgs/loading_options.png)

Model keyframes are loaded with 9 empty frames in between
and displayed in the dope sheet.

![animation frames](imgs/flag_animation_frames.png)

In the UV editor you can see both the UV map and
the UV layout.

![UV Layout](imgs/uv_layout.png)

Using texture paint mode, this allows easily editing
and adding new UV maps. The current importer does not
support exporting a modified UV layout though.

![UV editing](imgs/texture_paint.png)