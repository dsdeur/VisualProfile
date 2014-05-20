from PIL import Image
import colorsys
import pickle

from operator import itemgetter
import pymeanshift as pms
from collections import Counter
import json
import SimpleCV as scv


class ImageBody(object):
    resizeSize = 50, 50
    resizeSizeMean = 200, 200
    saturatedRange = (0.43, 0.55, 0.75)

    def __init__(self, img):
        # Open the image
        self.emptyImage = scv.Image("emptyImage.jpg")
        self.backgroundImage = scv.Image(img)
        self.newImg = self.backgroundImage - self.emptyImage

        #self.mask = self.newImg.hueDistance(color=scv.Color.WHITE).binarize()
        #self.maskedBG = self.emptyImage - self.mask
        #self.maskedBG.save("maskedBg.jpg")

        #self.finalImage = self.newImg + self.maskedBG

        #self.finalImage.save("finalImage.jpg")
        self.newImg.save("newImage.jpg")
        self.inImage = Image.open("newImage.jpg")
        
        # Resize
        self.smallImage = self.inImage.resize(self.resizeSize, Image.ANTIALIAS)
        self.inImage.thumbnail(self.resizeSizeMean, Image.ANTIALIAS)

        # Get colors per pixel RGB and HSL
        self.allPixelsRGB = getColors(self.smallImage)
        self.allPixelsHSL = RGBtoHSL(self.allPixelsRGB)

        # Do magic
        self.nonSaturatedRGB, self.saturatedRGB = getSaturatedColors(self.allPixelsHSL, self.saturatedRange)
        self.meanshiftRGB = meanshift(self.inImage)


    def filterBackground(self, filterColors):
        """Filter the colors array with the provided filtercolors"""
        # Def filtered arrays
        self.filteredSatRGB = []
        self.filteredMeanRGB = []
        self.filteredMeanPerc = []

        if len(filterColors) > 0:
            print "\n\n\n FilterColors aanwezig!"
            filterOnlyColors = []
            for color in filterColors:
                filterOnlyColors.append(color[0])

            for color in self.saturatedRGB:
                # Check if color needs to be filtered
                if color not in filterOnlyColors:
                    # Add to result array
                    self.filteredSatRGB.append(color)

            for color in self.meanshiftRGB:
                print color
                # Check if color needs to be filtered
                if color[0] not in filterOnlyColors:
                    # Add to result array
                    self.filteredMeanRGB.append(color)
        else:
            self.filteredSatRGB = self.saturatedRGB
            self.filteredMeanRGB = self.meanshiftRGB

        # Convert RGB bit to RGB perc
        for color in self.filteredMeanRGB:
            r = getPercentage(color[0][0], 255)
            g = getPercentage(color[0][1], 255)
            b = getPercentage(color[0][2], 255)

            self.filteredMeanPerc.append(((r,g,b), color[1]))


    def palette(self):
        """Generate the palette"""
        # Create the palette arrays
        self.colorPaletteBit = []
        self.colorPalettePerc = []
        self.colorPaletteHEX = []

        # Add max 2 saturated colors
        while len(self.filteredSatRGB) >= 1 and len(self.colorPaletteBit) <= 1:
            color = self.filteredSatRGB.pop()
            self.colorPaletteBit.append(color)

        # Add meanshift colors till palette = 5
        while len(self.filteredMeanRGB) >= 1 and len(self.colorPaletteBit) <= 4:
            color = self.filteredMeanRGB.pop()
            self.colorPaletteBit.append(color[0])

       # for color in colorPaletteBit:


        # If not enough colors fill palette with white
        while len(self.colorPaletteBit) <= 4:
            self.colorPaletteBit.append((255,255,255))

        # Convert RGB bit to RGB perc and RGB HEX
        for color in self.colorPaletteBit:
            r = getPercentage(color[0], 255)
            g = getPercentage(color[1], 255)
            b = getPercentage(color[2], 255)

            self.colorPalettePerc.append((r,g,b))

            self.colorPaletteHEX.append(RGBToHTMLColor(color))

        # Create json file
        createJson(self.colorPaletteHEX, self.colorPaletteBit)

        return self.colorPalettePerc


class FilterColors(object):
    filename = "filtercolors.txt"

    def __init__(self):
        try:
            self.loadFromFile()
        except:
            self.colorsBit = []

        self.bitToPerc()


    def addColorPerc(self, color):
        self.colorsPerc.append(color)

        r = getBitValue(color[0][0], 255)
        g = getBitValue(color[0][1], 255)
        b = getBitValue(color[0][2], 255)

        self.colorsBit.append(((r,g,b), color[1]))
        self.updateFile()


    def removeColorPerc(self, color):
        if color in self.colorsPerc:
            self.colorsPerc.remove(color)

            r = getBitValue(color[0][0], 255)
            g = getBitValue(color[0][1], 255)
            b = getBitValue(color[0][2], 255)

            self.colorsBit.remove(((r,g,b), color[1]))
            self.updateFile()


    def loadFromFile(self):
        colorFile = open(self.filename, "rb")
        self.colorsBit = pickle.load(colorFile)

        if len(self.colorsBit) < 1:
            self.colorsBit.append((0,0,0),0) 
        colorFile.close()


    def updateFile(self):
        colorFile = open(self.filename, "wb")
        pickle.dump(self.colorsBit, colorFile)
        colorFile.close()


    def bitToPerc(self):
        self.colorsPerc = []

        for color in self.colorsBit:
            r = getPercentage(color[0][0], 255)
            g = getPercentage(color[0][1], 255)
            b = getPercentage(color[0][2], 255)

            self.colorsPerc.append(((r,g,b), color[1]))


    def reset(self):
        self.colorsBit = []
        self.colorsPerc = []

        self.updateFile()

"""
Create JSON file for colors
------------------------------------------------------------    
""" 
def createJson(colorsHEX, colorsRGB):
    jsonData = json.dumps({"colorsHEX": colorsHEX, "colorsRGB": colorsRGB})
    jsonFile = open("colors.json", "w+")
    #jsonFile = open("Y:/colors.json", "w+")
    jsonFile.write(jsonData)
    jsonFile.close()


"""
Meanshift functions
------------------------------------------------------------    
""" 
def meanshift(inputImg):
    """Generate meanshift colors"""
    # Let the meanshift magic happen
    segImg = segmentImage(inputImg, 50, 50, 300)

    # Convert meanshifted array to numpy img
    segImg = numpyToImage(segImg)
    segImg.save("test.jpg", "JPEG")

    # Get color array from generated image
    RGBarray = getColors(segImg)
    # Create count array
    countArray = getDiscPerc(RGBarray)

    # Convert to list and sort
    countList = countArray.items()
    countList.sort(key=lambda x: x[1])
    print countList

    return countList


def numpyToImage(npArray):
    """Get image from numpy array"""
    image = Image.fromarray(npArray, "RGB")
    return image


def getDiscPerc(RGBarray):
    """Sort array on percentage"""
    result = Counter(RGBarray);
    return result


def segmentImage(img, spatial_radius, range_radius, min_density):
    """Generate segmented image, the meanshift magic"""
    (segmented_image, labels_image, number_regions) = pms.segment(img, spatial_radius=10, range_radius=8, min_density=150)

    return segmented_image



"""
Get Saturated Colors from HSL array
------------------------------------------------------------    
""" 
def getSaturatedColors(allColorsHSL, minValues):
    allSaturatedColors = []

    for color in allColorsHSL:
        # Check if color is saturated
        colornew = (color[0], color[1]+0.1, color[2]+0.05)
        if (colornew[1] > minValues[0] 
            and colornew[1] < minValues[1] 
            and colornew[2] > minValues[2]):

            # Add saturated color to result, and remove from input
            allSaturatedColors.append(color)
            allColorsHSL.remove(color)

    allSaturatedColors.sort(key = itemgetter(2,1))
    return HSLtoRGB(allColorsHSL), HSLtoRGB(allSaturatedColors)



"""
Image to color array
------------------------------------------------------------    
"""     
def getColors(i):
    pixels = i.load()
    width, height = i.size

    allColorsRGB = []

    for x in range(width):
        for y in range(height):
            cpixel = pixels[x, y]
            allColorsRGB.append(cpixel)

    allColorsRGB.sort()
    print "%s RGB values collected \n" % len(allColorsRGB)
    return allColorsRGB



"""
Color Conversion Functions
------------------------------------------------------------    
"""
# Converts an array of RGB (0-255) to HSL (0-1)
def RGBtoHSL(allPixelsRGB):
    allPixelsHSL = []

    for i, valueRGB in enumerate(allPixelsRGB):
        r = getPercentage(valueRGB[0], 255)
        g = getPercentage(valueRGB[1], 255)
        b = getPercentage(valueRGB[2], 255)

        hsl = colorsys.rgb_to_hls(r, g, b)

        allPixelsHSL.append(hsl)

        sorted(allPixelsHSL, key=itemgetter(1))
        
    return allPixelsHSL
    

# Converts an array of HSL (0-1) to RGB (0-255) 
def HSLtoRGB(allPixelsHSL):
    allPixelsRGB = []

    for i, valueHSL in enumerate(allPixelsHSL):
        rgb = colorsys.hls_to_rgb(valueHSL[0], valueHSL[1], valueHSL[2]);

        r = getBitValue(rgb[0], 255)
        g = getBitValue(rgb[1], 255)
        b = getBitValue(rgb[2], 255)

        allPixelsRGB.append((r, g, b))

    return allPixelsRGB


# Converts an array of RGB (0-255) to HEX(#xxxxxx)
def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    return hexcolor

# Helper function for RGBtoHSL
def getPercentage(value, maxValue):
    return value / float(maxValue)

# Helper function for HSLtoRGB
def getBitValue(value, maximum):
    return int(value * maximum)