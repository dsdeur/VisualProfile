import sys, os
import glob
from PIL import Image
import time
import distutils.core


class CameraBodyShot(object):
    def captureImage(self):
        image = glob.glob("tempbody/*.jpg")
        
        if len(image) >= 1:
            return image[0]
        else:
            return False


    def clearTemp(self):
        files = glob.glob("tempbody/*")
        fromDir = "tempbody"
        toDir = "bodypics"

        distutils.dir_util.copy_tree(fromDir, toDir)

        for tempfile in files:

            os.unlink(tempfile)


class CameraDetail(object):
    def getPictures(self):
        images = glob.glob("tempdetail/*.jpg")

        if len(images) >= 5:
            finalImages = cropAndMove(images)
            return True, finalImages
        else:
            return False, 5-len(images)


def cropAndMove(images):
    finalImages = []

    for (counter, image) in enumerate(images):
        if counter < 5:
            img = Image.open(image)
            w,h = img.size

            size = 220, 220

            a = w/3
            b = (h-a)/2

            newimg = img.crop((a,b,a+a,b+a))

            newimg.resize(size, Image.ANTIALIAS)
            newimg.save("current/UNITIV/brandfoto_%s.jpg" % str(counter), "JPEG")
            #newimg.save("Z:/current/UNITIV/brandfoto_%s.jpg" % str(counter), "JPEG")

            #img = Image.open("Z:/current/UNITIV/brandfoto_%s.jpg" % str(counter))
            #img.save("Y:/brandfoto_%s.jpg" % str(counter), "JPEG")

            finalImages.append("Z:/current/UNITIV/brandfoto_%s.jpg" % str(counter))
        
        os.unlink(image)

    return finalImages


