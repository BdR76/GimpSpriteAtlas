GIMP SpriteAtlas
================

GIMP SpriteAtlas is a python script to compile sprite textures for use in games and websites.

It is a plug-in which takes several smaller images, compiles them into a single image
using as litte space as possible, and it exports a JSON, XML or CSS file with the sprite names and coordinates.

![GIMP Sprite Atlas plug-in summary](/spriteatlas_summary.png?raw=true "GIMP Sprite Atlas plug-in summary")

How to install
-------------
Install GIMP and place the plug-in file `create_spriteatlas.py` in the GIMP folder,
usually located in the directory `C:\Program Files`:

	.\GIMP 2\lib\gimp\2.0\plug-ins\

After you've copied the file in this directory, open GIMP and the plug-in is available in the menu:

	Filters -> Animation -> Sprite Atlas

How to use it
-------------

1. Open GIMP
2. Open your images as layers
3. Start the plug-in
4. Select output folder
5. Press OK

So first open all your images as layers. You can do this from the menu `Open As Layers`
(Ctrl + Alt + O), select all your files and click `Open`.
Alternatively, you can first open one image (preferably the largest one),
and then drag and drop all the remaining images onto the layers window.

Note: opening images as layers can be remarkably slow (see [issue report](https://gitlab.gnome.org/GNOME/gimp/-/issues/8200)).

![GIMP Sprite Atlas plug-in how to use 1](/gimp_screenshot1.png?raw=true "GIMP Sprite Atlas plug-in how to use 1")

Then go to the menu `Filters > Animation > Sprite Atlas` to open the GIMP SpriteAtlas plug-in, you'll see the following dialog.

![GIMP Sprite Atlas plug-in how to use 1](/gimp_screenshot2.png?raw=true "GIMP Sprite Atlas plug-in how to use 2")

Make sure to select an output folder, this is where the output image and coordinates datafile will be exported to.

The default export folder is just `\tmp\`, if you don't change this to an actual existing folder you will get this error message:

	RuntimeError: Could not open '\tmp\sprites.png' for writing: No such file or directory

Press OK and it will generate and export the sprite texture and sprite metadata file.

![GIMP Sprite Atlas plug-in how to use 1](/gimp_screenshot3.png?raw=true "GIMP Sprite Atlas plug-in how to use 3")

Options
-------

**Export filename**: Export filename for both the texture image and the coordinates file,
for examplke, if set to `sprites123` then the output files will be named `sprites123.png` and `sprites123.json`.

**Export folder**: Output folder for both the texture image and the coordinates file.

**Export filetype**

* JSON TexturePacker-array, compatible with the TexturePacker format
* JSON TexturePacker hash, compatible with the TexturePacker format
* CSS sprites, can be used for html and websites
* XML, plain xml format

The TexturePacker-array/hash output is the preferred format for use with [Phaser.io](https://phaser.io/).
For any other needed format, you can edit the Python code and add a ne format or post an [issue here](https://github.com/BdR76/GIMPSpriteAtlas/issues).

**Pad one pixel between sprites** separate all sprites by at least one pixel, recommended to avoid *texture bleeding*.
Meaning in some graphics engines, the texture tiles can "overflow" and pick up parts of neighboring tiles.

**Extending sprites** the plugin can automatically extend the edges on some sprites Up Down Left and/or Right.
For example if you want to extend a sprite **D**own and **R**right you can add `[ext=DR]` to the name, so like this

	mytile01 [ext=dr].png

In the compiled texture, the plug-in will extend this sprite by one pixel down and one pixel right,
meaning it will copy the bottom row pixels and the right-most column of pixels of that sprite.

![GIMP Sprite Atlas plug-in extend edges](/spriteatlas_extend.png?raw=true "GIMP Sprite Atlas plug-in extend edges")

Sprite Sheet
------------
This repository also includes a `create_spriteeheet.py` plugin, for the sake of completeness.
It creates same size and no coordinates file.

Sprites in a grid, where all sprites are tiles with the same size.
The tile size will be the width and height of the original image.

It is based on a [plug-in by Spydarlee](https://github.com/Spydarlee/scripts/tree/master/GIMP)
but with some bugfixes and additional options

Trouble shooting / Known issues
-------------------------------
* Opening images as layers is remarkably slow in GIMP (see [issue report](https://gitlab.gnome.org/GNOME/gimp/-/issues/8200)).
Once you've created a sprite texture, it's best to also save the original image with the layers as a `.xcf`.
If you want to make changes to the texture at a later time (add/remove sprites)
then you can more quickly open the `.xcf` instead of having to re-add all the images as layers again.

* You can use this plug-in create any custom coordinates format or custom preprocessing
by editing the Python file.
Alternatively you can also create sprite atlas/textures using the 
[TexturePacker Online (free)](https://www.codeandweb.com/tp-online)
or [Leshy SpriteSheet Tool](https://www.leshylabs.com/apps/sstool/)

History
-------
26-may-2022 - v0.1 first release  

BdR©2022 Free to use - send questions or comments: Bas de Reuver - bdr1976@gmail.com
