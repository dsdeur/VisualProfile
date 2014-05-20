from xml.etree import ElementTree as ET

def makeXML(colorHEX, colorRGB):
	#C:/Users/S-LAP/Desktop/Shore/
	#emotieXML = "Z:/current/UNITI/emotie.xml"
	emotieXML = "emotieDefault.xml"

	emotieFile = open(emotieXML, "r+")
	f = emotieFile.read()
	emotieFile.close()
	emotieFile = open(emotieXML, "w")
	print f
	print "\n\n\n"

	index = f.rfind("person>")
	print "\n\n\n Index:"

	backup = False
	try:
		if f[index-1] != "/":
			emotieFinal = f[:index] + "/" + f[index:]
			print "\n\n\n Final:"
			print emotieFinal
			emotieFile.write(emotieFinal)
		else:
			emotieFile.write(f)
	except:
		print "\n\n\n\n"
		print "BACKUP"
		print "\n\n\n\n"
		backupEmotion = open("emotieDefault.xml", "r+")
		backupText = backupEmotion.read()
		backupEmotion.close()
		emotieFile.write(backupText)
		backup = True		

	emotieFile.close()

	tree = ET.ElementTree()
	tree.parse(emotieXML)
	person = tree.getroot()

	age = tree.findtext("emotion/Age")
	age = int(float(age))
	ageDeviation = tree.findtext("emotion/AgeDeviation")
	ageDeviation = int(float(ageDeviation))

	happy = tree.findtext("emotion/Happy") 
	sad = tree.findtext("emotion/Sad")
	angry = tree.findtext("emotion/Angry")
	surprised = tree.findtext("emotion/Surprised")
	
	happy = happy[:-2]
	sad = sad[:-2]
	angry = angry[:-2]
	surprised = surprised[:-2]
	

	emotions =  [float(happy), float(sad), float(angry), float(surprised)]

	video = emotions.index(max(emotions)) + 1
	print video

	person = ET.Element("person")

	colorsRGB = ET.SubElement(person, "colorsRGB")
	for color in colorRGB:
		colorNode = ET.SubElement(colorsRGB, "color")

		titleR = ET.SubElement(colorNode, "R")
		titleR.text = str(color[0])
		titleG = ET.SubElement(colorNode, "G")
		titleG.text = str(color[1])
		titleB = ET.SubElement(colorNode, "B")
		titleB.text = str(color[2])


	title = ET.SubElement(person, "video")
	title.text = str(video) + ".mov"

	title = ET.SubElement(person, "age")
	title.text = str(age - ageDeviation) + " - " + str(age + ageDeviation)

	if backup == True:
		title.text = "###"

	emotion = ET.SubElement(person, "emotion")
	title = ET.SubElement(emotion, "angry")
	title.text = angry
	title = ET.SubElement(emotion, "happy")
	title.text = happy
	title = ET.SubElement(emotion, "sad")
	title.text = sad
	title = ET.SubElement(emotion, "surprised")
	title.text = surprised

	# Alles samenvoegen en opslaan als .xml
	tree = ET.ElementTree(person)
	#tree.write("Z:/current/UNITIV/visualprofile.xml", encoding="utf-8", xml_declaration=True)
	#tree.write("Y:/visualprofile.xml", encoding="utf-8", xml_declaration=True)
	tree.write("visualprofile.xml", encoding="utf-8", xml_declaration=True)

#predefined HEX en RGB voor testen
#HEX = ["#643650","#3a191d","#6a3641","#492028","#331714"]
#RGB = ["RGB(255,155,13)","RGB(255,155,13)","RGB(255,155,13)","RGB(255,155,13)","RGB(255,155,13)"]
#makeXML(HEX,RGB)
