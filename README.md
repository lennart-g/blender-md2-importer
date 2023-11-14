# Quake 2 MD2 import add-on for Blender 3.x
This add-on allows importing .md2 model files. This hasn't been
natively supported by [Blender](https://www.blender.org/) for
a decade now.

Please note that this add-on is still incomplete. **Bug reports and feature
requests are welcome!**

Developed and tested with Blender 3.6.5 and Python 3.10.13.
Older versions might still (partially) work.

1. [What can this importer (!) do so far?](#what-can-this-importer--do-so-far)
2. [What is missing?](#what-is-missing)
3. [Releases](#releases)
4. [Installation](#installation)
6. [How to use](#how-to-use)
5. [Development](#development)

## What can this importer (!) do so far?

- load an MD2 object to Blender
- attach a UV map linked in the .md2 file or a custom one
  - Blender native formats (not verified except .jpg):
  - custom format: .pcx
- load and run keyframe animations

### Blender native image formats in Blender 3.6.5 / Python 3.10.13:
```python3
>>> bpy.path.extensions_image
frozenset({'.tx', '.png', '.cin', '.tiff', '.bmp', '.rgb', '.tga', '.sgi', '.jpeg', '.dpx', '.psd', '.jp2', '.j2c', '.hdr', '.webp', '.rgba', '.exr', '.pdd', '.jpg', '.psb', '.dds', '.tif'})
```
## What is missing?

- aligning the animation keyframes to the fps used for the different animations

## [Releases](https://github.com/lennart-g/blender-md2-importer/releases)

## Installation
Install the provided .zip via the Edit > Preferences > Add-ons menu.

### Optional: PCX skin files
When loading a .pcx file, a message referring to this README is shown.

1. [install Pillow (used for loading .pcx files)](https://blender.stackexchange.com/a/122337). 
Replace `pip install scipy` with `pip install pillow`.
On old Blender / Python versions, an upgrade of pip might be necessary.
2. Check the plugin activation checkbox again.

## How to use

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

## Development
Follow [these instructions](https://github.com/lennart-g/bsp_hacking/blob/master/docs/blender_importer.md)
with adjustments for this repository.

### Pre-release quality assurance
#### Code style:
```bash
flake8 .
```

#### Type checking:
This ignores the `md2_importer` directory as there
are no stubs available for the Blender API (bpy).
```bash
mypy . --strict
```

#### Automated tests:
```bash
python3 -m pytest .
```

#### Manual testing with the built add-on archive:
1. Delete and re-extract Blender from the downloaded archive
2. Install and enable the add-on from the built archive
3. Load the .md2 files from the archive (**ensure being in material preview mode**)
   1. `bigleaf2.md2` should by default load `leaf02.jpg`
   2. `car.md2` should by default not load a skin
   3. `car.md2` should load `car.jpg` when "Load custom skin" is checked
4. Loading `doomguy.md2` (not included) which requires `doomguy.pcx`
should show a message that `.pcx` loading failed.
5. Install Pillow with the linked instructions
6. Load `doomguy.md2` again