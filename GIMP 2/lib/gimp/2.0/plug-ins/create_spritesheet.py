#!/usr/bin/env python
# License: Public Domain - https://creativecommons.org/share-your-work/public-domain/cc0/
# https://github.com/Spydarlee/scripts/tree/master/GIMP
#
# Create a sprite sheet consisting of uniformly-sized image frames,
# current image size will be the spritesheet frame sizes
#
# 2022-04-30 script updated by BdR

from gimpfu import *
import math

def create_spritesheet(image, tileLayout, spriteCenter):

    # Grab all the layers from the original image, each one of which will become an animation frame
    layers = image.layers
    numLayers = len(layers)

    # Deterime how many rows and columns we need for each of our layers/animation frames
    if (tileLayout == 1):
        numCols = int(math.ceil(math.sqrt(numLayers)))
        numRows = int(math.ceil(1.0 * numLayers / numCols))
    else:
        numRows = 1 if (tileLayout == 2) else numLayers # Single row
        numCols = 1 if (tileLayout == 3) else numLayers # Single column

    # Determine frame sizes = current image size
    frameWidth = image.width
    frameHeight = image.height
    
    # Determine new image size, based on the number of rows and columns
    newImgWidth = frameWidth * numCols
    newImgHeight = frameHeight * numRows

    # Create a new image and a single layer that fills the entire canvas
    newImage = gimp.Image(newImgWidth, newImgHeight, RGB)
    newLayer = gimp.Layer(newImage, "Spritesheet", newImgWidth, newImgHeight, RGBA_IMAGE, 100, NORMAL_MODE)
    newImage.add_layer(newLayer, 1)

    # Select image size to ensure uniformly-sized frames (i.e. when original layer is larger than image then "crop" to image size)
    pdb.gimp_selection_all(image)

    # go through all layers (GIMP Layers used to be in the reverse order, not anymore)
    layerIndex = 0

    # Loop over our spritesheet grid filling each one row at a time
    for y in xrange(0, numRows):
        for x in xrange(0, numCols):
            # check layerIndex because it's possible there are less layers than grid positions
            # i.e. cannot always fill out entire grid, last tile positions will just be empty
            if layerIndex < numLayers:
                # Copy the layer's contents and paste it into a "floating" layer in the new image
                pdb.gimp_edit_copy(layers[layerIndex])
                floatingLayer = pdb.gimp_edit_paste(newLayer, TRUE)

                # Arrange frames as tiles from top-left to bottom-right
                xPos = x * frameWidth
                yPos = y * frameHeight
                
                # Floating layer defaults to center, get current offset and corrent for desired position
                xOffset, yOffset = floatingLayer.offsets
                xOffset = xPos - xOffset
                yOffset = yPos - yOffset

                # center if needed (i.e. when layer size is smaller than frame size)
                if spriteCenter and (floatingLayer.width < frameWidth):
                    xOffset += (frameWidth - floatingLayer.width) / 2
                if spriteCenter and (floatingLayer.height < frameHeight):
                    yOffset += (frameHeight - floatingLayer.height) / 2

                # Move the floating layer into the correct position
                pdb.gimp_layer_translate(floatingLayer, xOffset, yOffset)

                # Move to the next layer index
                layerIndex = layerIndex + 1

    # Merge the last floating layer into our final 'Spritesheet' layer
    pdb.gimp_image_merge_visible_layers(newImage, 0)

    # Create and show a new image window for our spritesheet
    gimp.Display(newImage)
    gimp.displays_flush()

# Register the plugin with Gimp so it appears in the filters menu
register(
    "python_fu_create_spritesheet",
    "Creates a new spritesheet image, from the layers of the current image.",
    "Creates a new spritesheet image, from the layers of the current image.",
    "Karn Bianco",
    "Karn Bianco",
    "2022",
    "Create Spritesheet",
    "*",
    [
        (PF_IMAGE, "image", "Input image:", None),
        (PF_RADIO, "tileLayout", "Spritesheet layout:", 1, (("Grid", 1), ("Single row", 2), ("Single column", 3))),
        (PF_BOOL, "spriteCenter", "Center sprite in frame\n(when sprites are smaller)", TRUE)
    ],
    [],
    create_spritesheet, menu="<Image>/Filters/Animation/")

main()
