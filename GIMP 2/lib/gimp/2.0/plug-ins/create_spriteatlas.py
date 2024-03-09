# GIMP plug-in Create SpriteAtlas
# Take layers as images and compile into spriteatlas
# including a coordinates file in json/atlas/css/xml format
# uses rectangle packing algorithm
#
# https://github.com/BdR76/GimpSpriteAtlas/

from gimpfu import *
import math
import os

layer_rects = []
spaces = []
pixel_space = 1
ATLAS_PLUGIN_VERSION = "v0.3"

# empty space
class spaceobj(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    def __cmp__(self, other):
        return (self.width * self.height < other.width * other.height)
    def __lt__(self, other):
        return (self.width * self.height < other.width * other.height)

# image layer metadata
class imgRect(object):
    def __init__(self, n, w, h, i):
        # process stuff
        if n.endswith(('.png', '.jpg')):
            n = os.path.splitext(n)[0]
        # set parameters
        self.name = n
        self.width = w
        self.height = h
        self.index  = i
        # extra stuff
        self.pack_x = 0
        self.pack_y = 0
        self.ext_up = 0
        self.ext_down = 0
        self.ext_left = 0
        self.ext_right = 0
        # determinate name and optional extend direction, example "green_pipe [ext=UD].png" -> name="green_pipe" ext_up=1 ext_down=1
        pos1 = n.find('[')
        pos2 = n.find(']')
        if pos1 >= 0 and pos2 >= 0 and pos1 < pos2:
            self.name = n[0:pos1].strip()
            ex = n[pos1+1:pos2].strip().lower()
            if ex.startswith("ext="):
                ex = ex[4:]
                self.ext_up = 1 if "u" in ex else 0
                self.ext_down = 1 if "d" in ex else 0
                self.ext_left = 1 if "l" in ex else 0
                self.ext_right = 1 if "r" in ex else 0
        # total width and height, including extruding parts
        self.tot_width = self.width + self.ext_left + self.ext_right
        self.tot_height = self.height + self.ext_up + self.ext_down
    def __cmp__(self, other):
        return (self.height < other.height)
    def __lt__(self, other):
        return (self.height < other.height)

def prepare_layers_metadata(layers):
    # Collect metadata from all layers as custom list
    idx = 0
    area = 0
    maxWidth = 0
    for lyr in layers:
        # layer image metadata
        n = lyr.name
        w = lyr.width
        h = lyr.height
        newrec = imgRect(n, w, h, idx)
        layer_rects.append(newrec)
        # calculate total layer area and maximum layer width
        area += (newrec.tot_width + pixel_space) * (newrec.tot_height + pixel_space);
        maxWidth = max(newrec.tot_width + pixel_space, maxWidth + pixel_space)
        idx = idx + 1

    # sort the layer data for packing by height, descending
    layer_rects.sort(reverse=True);

    # aim for a square-ish resulting container,
    # slightly adjusted for sub-100% space utilization
    startWidth = max(math.ceil(math.sqrt(area / 0.95)), maxWidth)

    # also initialise list of spaces, start with a single empty space based on average layer size
    spaces.append(spaceobj(0, 0, startWidth, (startWidth+startWidth)))
    return

def calc_layers_packing():
    # packing algorithm, explanation and code example by Volodymyr Agafonkin
    # https://observablehq.com/@mourner/simple-rectangle-packing
    for box in layer_rects:
    
        # look through spaces backwards so that we check smaller spaces first
        i = len(spaces)-1
        while i >= 0:
    
            space = spaces[i];
    
            # look for empty spaces that can accommodate the current box
            if (box.tot_width > space.width or box.tot_height > space.height):
                i -= 1;
                continue;
    
            # found the space; add the box to its top-left corner
            # |-------|-------|
            # |  box  |       |
            # |_______|       |
            # |         space |
            # |_______________|
            box.pack_x = space.x + box.ext_left
            box.pack_y = space.y + box.ext_up
    
            if (box.tot_width + pixel_space == space.width and box.tot_height + pixel_space == space.height):
                # space matches the box exactly; remove it
                spaces.remove(space)
    
            elif (box.tot_height + pixel_space == space.height):
                # space matches the box height; update it accordingly
                # |-------|---------------|
                # |  box  | updated space |
                # |_______|_______________|
                spaces[i].x += (box.tot_width + pixel_space);
                spaces[i].width -= (box.tot_width + pixel_space);
            elif (box.tot_width + pixel_space == space.width):
                # space matches the box width; update it accordingly
                # |---------------|
                # |      box      |
                # |_______________|
                # | updated space |
                # |_______________|
                spaces[i].y += (box.tot_height + pixel_space);
                spaces[i].height -= (box.tot_height + pixel_space);
            else:
                # otherwise the box splits the space into two spaces
                # |-------|-----------|
                # |  box  | new space |
                # |_______|___________|
                # | updated space     |
                # |___________________|
                spaces.append(spaceobj(space.x + box.tot_width + pixel_space, space.y, space.width - box.tot_width - pixel_space, box.tot_height + pixel_space));
                spaces[i].y += (box.tot_height + pixel_space);
                spaces[i].height -= (box.tot_height + pixel_space);
            i -= 1;
            break;
    return

def extrude_edges_2(img, lyr, x, y, w, h, xgoal, ygoal):
    # render output atlas based on current layer coordinates
    pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, x, y, w, h)
    pdb.gimp_edit_copy(lyr)
    floatselection = pdb.gimp_edit_paste(lyr, FALSE)
    
    # Floating layer defaults to center, get current offset and corrent for desired position
    xOffset, yOffset = floatselection.offsets
    xOffset = xgoal - xOffset
    yOffset = ygoal - yOffset

    # Move the floating layer into the correct position
    pdb.gimp_layer_translate(floatselection, xOffset, yOffset)
    pdb.gimp_floating_sel_anchor(floatselection)

def extrude_edges(img, lyr, x, y, w, h):
    # render output atlas based on current layer coordinates
    pdb.gimp_image_select_rectangle(img, CHANNEL_OP_REPLACE, x, y, w, 1)
    pdb.gimp_edit_copy(lyr)
    floatselection = pdb.gimp_edit_paste(lyr, FALSE)
    
    # Floating layer defaults to center, get current offset and corrent for desired position
    xOffset, yOffset = floatselection.offsets
    xOffset = x - xOffset
    yOffset = y - 1 - yOffset

    # Move the floating layer into the correct position
    pdb.gimp_layer_translate(floatselection, xOffset, yOffset)

def render_spriteatlas(layers, filename, filetag):
    # render output atlas based on current layer coordinates
    
    # determine total width, height
    img_w = 0
    img_h = 0
    for obj in layer_rects:
        w = obj.pack_x + obj.width + obj.ext_right
        h = obj.pack_y + obj.height + obj.ext_up
        if w > img_w:
            img_w = w
        if h > img_h:
            img_h = h

    # create new image
    imgAtlas = gimp.Image(img_w, img_h, RGB)
    newLayer = gimp.Layer(imgAtlas, filetag, img_w, img_h, RGBA_IMAGE, 100, NORMAL_MODE)
    imgAtlas.add_layer(newLayer, 1)
    
    # copy all layers to new positions
    for obj in layer_rects:

        # Copy the layer's contents and paste it into a "floating" layer in the new image
        pdb.gimp_edit_copy(layers[obj.index])
        floatingLayer = pdb.gimp_edit_paste(newLayer, FALSE)

        # Floating layer defaults to center, get current offset and corrent for desired position
        xOffset, yOffset = floatingLayer.offsets
        xOffset = obj.pack_x - xOffset
        yOffset = obj.pack_y - yOffset

        # Move the floating layer into the correct position
        pdb.gimp_layer_translate(floatingLayer, xOffset, yOffset)
        # Anchor the floating selection before making another selection
        pdb.gimp_floating_sel_anchor(floatingLayer)

        # extrude up, down, left, right
        if obj.ext_up == 1: # up
            extrude_edges_2(imgAtlas, newLayer, obj.pack_x, obj.pack_y, obj.width, 1, obj.pack_x, obj.pack_y-1)
        if obj.ext_down == 1: # down
            extrude_edges_2(imgAtlas, newLayer, obj.pack_x, obj.pack_y+obj.height-1, obj.width, 1, obj.pack_x, obj.pack_y+obj.height)
        if obj.ext_left == 1: # left
            extrude_edges_2(imgAtlas, newLayer, obj.pack_x, obj.pack_y, 1, obj.height, obj.pack_x-1, obj.pack_y)
        if obj.ext_right == 1: # right
            extrude_edges_2(imgAtlas, newLayer, obj.pack_x+obj.width-1, obj.pack_y, 1, obj.height, obj.pack_x+obj.width, obj.pack_y)

        #pdb.gimp_drawable_set_pixel(floatingLayer, 10, 10, 4, [240, 0,   0, 255])
        #pdb.gimp_drawable_set_pixel(floatingLayer, 11, 10, 4, [240, 0, 240, 255])
        #pdb.gimp_drawable_set_pixel(floatingLayer, 12, 10, 4, [240, 240, 0, 255])
        
    # Merge the last floating layer into our final 'Spritesheet' layer
    pdb.gimp_image_merge_visible_layers(imgAtlas, 0)

    # look through spaces backwards so that we check smaller spaces first
    horzmark = True
    xmark = img_w
    ymark = img_h
    spaces.sort(); # sort smallest first

    idx = 0
    for sp in spaces:
        # adjust space for out-of-bounds of final image size
        if (sp.x + sp.width > img_w):
            sp.width -= (sp.x + sp.width - img_w)
        if (sp.y + sp.height > img_h):
            sp.height -= (sp.y + sp.height - img_h)
        # check if watermark fits inside space
        idx += 1
        if (sp.width >= 54 and sp.height >= 8) or (sp.width >= 8 and sp.height >= 54):
            xmark = sp.x
            ymark = sp.y
            horzmark = (sp.width >= 54)
            break

    #pdb.gimp_message_set_handler(ERROR_CONSOLE)
    #pdb.gimp_message("xmark=%d ymark=%d" % (xmark, ymark))

    # add small watermark
    drwLayer = pdb.gimp_image_active_drawable(imgAtlas)
    pixelwm = [7, 5, 6, 0, 7, 0, 55, 65, 50, 1, 119, 80, 119, 3, 64, 0, 84, 119, 97, 0, 7, 3, 112, 119, 97, 0, 103, 112, 1, 119, 49, 96, 7, 7, 21, 112, 70, 3, 118, 81, 119, 1, 16, 119, 68, 0, 54, 35, 118, 0, 4, 7, 1]
    for wm in pixelwm:
        for b in range(0, 7):
            if wm & (1 << b): # bitwise-and
                xplot = xmark if horzmark else xmark+8-b
                yplot = ymark+b if horzmark else ymark
                if (xplot < img_w and yplot < img_h):
                    pdb.gimp_drawable_set_pixel(drwLayer, xplot, yplot, 4, [255, 255, 255, 255]) # xposition, yposition, nr-channels-per-pixel(3 or 4), [r,g,b]
                    #rectimg.putpixel((xplot, yplot), (255,0,255))
        if horzmark:
            xmark += 1
        else:
            ymark += 1

    # save as png
    outputname = '%s.png' % (filename)
    pdb.gimp_file_save(imgAtlas, imgAtlas.active_layer, outputname, outputname)

    # Create and show a new image window for our spritesheet
    gimp.Display(imgAtlas)
    gimp.displays_flush()
    return img_w, img_h

def write_spriteatlas_jsonarray(filename, filetag, sizex, sizey):
    stroutput = "{\n\t\"frames\":["
    
    # insert all sprite metadata
    for obj in layer_rects:
        stroutput += '\n\t\t{"filename":"%s","frame":{"x":%d,"y":%d,"w":%d,"h":%d},"rotated":"false","trimmed":"false",' % (obj.name, obj.pack_x, obj.pack_y, obj.width, obj.height)
        stroutput += '"spriteSourceSize":{"x":0,"y":0,"w":%d,"h":%d},' % (obj.width, obj.height)
        stroutput += '"sourceSize":{"w":%d,"h":%d}},' % (obj.width, obj.height)

    # remove last comma
    stroutput = stroutput[:-1]

    # meta data
    stroutput += "\n\t],\n"
    stroutput += "\t\"meta\":{\n"
    stroutput += "\t\t\"app\":\"https://github.com/BdR76/GimpSpriteAtlas/\",\n"
    stroutput += "\t\t\"version\":\"GIMP SpriteAtlas plug-in %s\",\n" % ATLAS_PLUGIN_VERSION
    stroutput += "\t\t\"author\":\"Bas de Reuver\",\n"
    stroutput += ("\t\t\"image\":\"%s.png\",\n" % filetag)
    stroutput += ("\t\t\"size\":{\"w\":%d,\"h\":%d},\n" % (sizex, sizey))
    stroutput += "\t\t\"scale\":1\n"
    stroutput += "\t}\n"
    stroutput += "}"
    
    # export filename
    outputname = '%s.json' % (filename)

    # export coordinate variables to textfile
    outputfile = file(outputname, 'w')
    outputfile.write(stroutput)
    outputfile.close()
    return
    
def write_spriteatlas_jsonhash(filename, filetag, img_w, img_h):
    stroutput = "{\n\t\"frames\":{"
    
    # insert all sprite metadata
    for obj in layer_rects:
        stroutput += '\n\t\t"%s":{"frame":{"x":%d,"y":%d,"w":%d,"h":%d},"rotated":"false","trimmed":"false",' % (obj.name, obj.pack_x, obj.pack_y, obj.width, obj.height)
        stroutput += '"spriteSourceSize":{"x":0,"y":0,"w":%d,"h":%d},' % (obj.width, obj.height)
        stroutput += '"sourceSize":{"w":%d,"h":%d}},' % (obj.width, obj.height)

    # remove last comma
    stroutput = stroutput[:-1]

    # meta data
    stroutput += "\n\t},\n"
    stroutput += "\t\"meta\":{\n"
    stroutput += "\t\t\"app\":\"https://github.com/BdR76/GimpSpriteAtlas/\",\n"
    stroutput += "\t\t\"version\":\"GIMP SpriteAtlas plug-in %s\",\n" % ATLAS_PLUGIN_VERSION
    stroutput += "\t\t\"author\":\"Bas de Reuver\",\n"
    stroutput += ("\t\t\"image\":\"%s.png\",\n" % filetag)
    stroutput += ("\t\t\"size\":{\"w\":%d,\"h\":%d},\n" % (img_w, img_h))
    stroutput += "\t\t\"scale\":1\n"
    stroutput += "\t}\n"
    stroutput += "}"
    
    # export filename
    outputname = '%s.json' % (filename)

    # export coordinate variables to textfile
    outputfile = file(outputname, 'w')
    outputfile.write(stroutput)
    outputfile.close()
    return
    
def write_spriteatlas_libgdx(filename, filetag, img_w, img_h):

    stroutput = ("%s.png\nsize: %d,%d\nformat: RGBA8888\nfilter: Linear,Linear\nrepeat: none\n" % (filetag, img_w, img_h))

    # insert all sprite metadata
    for obj in layer_rects:
        stroutput +=  ("%s\n  rotate: false\n  xy: %d, %d\n  size: %d, %d\n  orig: %d, %d\n  offset: 0, 0\n  index: -1\n" % (obj.name, obj.pack_x, obj.pack_y, obj.width, obj.height, obj.width, obj.height))
    
    # export filename
    outputname = '%s.atlas' % (filename)

    # export coordinate variables to textfile
    outputfile = file(outputname, 'w')
    outputfile.write(stroutput)
    outputfile.close()
    return
    
def write_spriteatlas_css(filename, filetag):
    
    stroutput = "/* GIMP SpriteAtlas plug-in %s by Bas de Reuver 2023 */\n" % ATLAS_PLUGIN_VERSION

    # insert all sprite metadata
    for obj in layer_rects:
        stroutput += ".%s {\n" % obj.name
        stroutput += "\tbackground: url('%s.png') no-repeat -%dpx -%dpx;\n" % (filetag, obj.pack_x, obj.pack_y)
        stroutput += "\twidth: %dpx;\n" % obj.width
        stroutput += "\theight: %dpx;\n" % obj.height
        stroutput += "}\n"
    
    # export filename
    outputname = '%s.css' % (filename)

    # export coordinate variables to textfile
    outputfile = file(outputname, 'w')
    outputfile.write(stroutput)
    outputfile.close()
    return
    

def write_spriteatlas_xml(filename, filetag):
    
    stroutput = ('<textureatlas xmlns="http://www.w3.org/1999/xhtml" imagepath="%s.png">\n' % filetag)
    stroutput += '\t<!-- GIMP SpriteAtlas plug-in %s by Bas de Reuver 2023 -->\n' % ATLAS_PLUGIN_VERSION

    # insert all sprite metadata
    for obj in layer_rects:
        stroutput += '\t<subtexture name="%s" x="%d" y="%d" width="%d" height="%d">\n' % (obj.name, obj.pack_x, obj.pack_y, obj.width, obj.height)
        stroutput += '\t</subtexture>\n'

    stroutput += '</textureatlas>\n'
    
    # export filename
    outputname = '%s.xml' % (filename)

    # export coordinate variables to textfile
    outputfile = file(outputname, 'w')
    outputfile.write(stroutput)
    outputfile.close()
    return
    
def create_spriteatlas(image, filetag, foldername, outputtype, padding):
    global pixel_space

    # create list of all layers
    layers = image.layers
    numLayers = len(layers)

    # add 1 pixel padding
    pixel_space = 1 if padding else 0

    # Clear any selections on the original image to esure we copy each layer in its entirety
    pdb.gimp_selection_none(image)
    prepare_layers_metadata(layers)

    # export filename(s)
    outputname = '%s\\%s' % (foldername, filetag)

    # compile image
    calc_layers_packing()
    img_w, img_h = render_spriteatlas(layers, outputname, filetag)

    # write to output file
    if outputtype == 1:
        write_spriteatlas_jsonarray(outputname, filetag, img_w, img_h)
    elif outputtype == 2:
        write_spriteatlas_jsonhash(outputname, filetag, img_w, img_h)
    elif outputtype == 3:
        write_spriteatlas_libgdx(outputname, filetag, img_w, img_h)
    elif outputtype == 4:
        write_spriteatlas_css(outputname, filetag)
    else: # outputtype == 5
        write_spriteatlas_xml(outputname, filetag)
    
# Register the plugin with Gimp so it appears in the filters menu
register(
    "python_fu_create_spriteatlas",
    "Create a sprite texture image from the layers of the current image.",
    "Create a sprite texture image from the layers of the current image.",
    "Bas de Reuver",
    "Bas de Reuver",
    "2023",
    "Create SpriteAtlas",
    "*",
    [
        (PF_IMAGE, 'image', 'Input image:', None),
        (PF_STRING, "fileName", "Export file name (without extension):", "sprites"),
        (PF_DIRNAME, "outputFolder", "Export to folder:", "/tmp"),
        (PF_RADIO, "fileType", "Export file type:", 1, (("JSON-TexturePacker Array", 1), ("JSON-TexturePacker Hash", 2), ("libGDX TextureAtlas", 3), ("CSS", 4), ("XML", 5))),
        (PF_BOOL, "addPadding", "Pad one pixel between sprites:", TRUE)
    ],
    [],
    create_spriteatlas, menu="<Image>/Filters/Animation/")

main()