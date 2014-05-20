#from imagecolor import ImageBody, FilterColors
from camera import CameraBodyShot, CameraDetail
import time
import pexpect
import sys

def main():
	#filterColors = FilterColors()
	#cameraDetail = CameraDetail()

	child = pexpect.spawn("gphoto2 --capture-tethered", cwd="tempbody/")
	child.logfile = sys.stdout

	while True:
		print "Hello"
		time.sleep(2)


	"""imageBody = ImageBody("tempbody/boe.jpg")
	
	print "\nsaturatedRGB:"
	print imageBody.saturatedRGB
	print "\nnonSaturattedRGB:"
	print imageBody.nonSaturatedRGB
	print "\nmeanshiftRGB:"
	print imageBody.meanshiftRGB
	print "\nFilter Perc:"
	print filterColors.colorsPerc
	print "\nFilter Bit:"
	print filterColors.colorsBit

	imageBody.filterBackground(filterColors.colorsBit)
	print "\nFilteredSat:"
	print imageBody.filteredSatRGB
	print "\nFilteredMean:"
	print imageBody.filteredMeanRGB


	print "\nPalette:"
	print imageBody.palette()
"""
if __name__ == '__main__':
	main()