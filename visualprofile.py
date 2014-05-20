import kivy
kivy.require('1.7.2')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from imagecolor import ImageBody, FilterColors
from camera import CameraBodyShot, CameraDetail

from maakxmltotaal import makeXML
import time

class MainLayout(FloatLayout):
    potentialFilterColors = []

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

        # Create the camera objects
        self.cameraDetail = CameraDetail()
        self.cameraBodyShot = CameraBodyShot()

        # Create the filterColors object
        self.filterColors = FilterColors()


    def filterColor(self, instance):
        """Function to add a filter color, callback for color button"""
        # Get background color
        rgb = instance.background_color
        # remove a from rgba (r,g,b,a) to (r,g,b)
        rgb = tuple(rgb[0:3])
        # Get button text
        intstext = instance.text
        
        # Add the color to filterColors
        self.filterColors.addColorPerc((rgb, intstext))
        # Update potentialColors if needed
        if (rgb,intstext) in self.potentialFilterColors:
            self.potentialFilterColors.remove((rgb, intstext))

        # Create the new button
        bttn = Button(text=instance.text, background_color=instance.background_color)
        bttn.bind(on_press=self.removeFilterColor)

        # Remove old and add new button
        self.buttons.remove_widget(instance)
        self.buttons_filter.add_widget(bttn)


    def removeFilterColor(self, instance):
        """Function to remove a filter color, callback for filter color button"""
        # Get background color
        rgb = instance.background_color
        # remove a from rgba (r,g,b,a) to (r,g,b)
        rgb = tuple(rgb[0:3])
        # Get button text
        intstext = instance.text

        # Remove the color from filterColors
        self.filterColors.removeColorPerc((rgb, intstext))
        # Update potentialColors if needed
        if (rgb, intstext) not in self.potentialFilterColors:
            self.potentialFilterColors.append((rgb, intstext))

        # Create the new button
        bttn = Button(text=instance.text, background_color=instance.background_color)
        bttn.bind(on_press=self.filterColor)

        # Remove old and add new button
        self.buttons.add_widget(bttn)
        self.buttons_filter.remove_widget(instance)


    def resetFilterColors(self):
        """Remove all filter colors"""
        self.filterColors.reset()
        self.buttons_filter.clear_widgets()


    def start(self, instance):
        """The magic, create the color palette"""

        # Get the new image from the camera object
        newimg = self.cameraBodyShot.captureImage()

        # Check if image is exists, else update button text 
        if newimg != False:
            # Clear the palette view in case of previous runs
            self.color_palette.clear_widgets();

            self.button_start.text = "Start"

            # Create the ImageBody object with the taken image
            self.imageBody = ImageBody(newimg)
            # Filter the background colors
            self.imageBody.filterBackground(self.filterColors.colorsBit)
            # Create the palette
            palettePerc = self.imageBody.palette()

            # Create the palette preview
            for (counter, color) in enumerate(palettePerc):
                bgcolor = color + (1,)
                btnText =  "{}".format(self.imageBody.colorPaletteBit[counter])
                bttn = Button(text=btnText, background_color=bgcolor)

                self.color_palette.add_widget(bttn)

            # Clear the temp folder
            self.cameraBodyShot.clearTemp()

            # Set colors for filtering background
            self.potentialFilterColors = self.imageBody.filteredMeanPerc

            # Create the xml
            makeXML(self.imageBody.colorPaletteHEX, self.imageBody.colorPaletteBit)
    
            # Popup done
            popup = Popup(title="Done.", 
                content = Label(text="Druk spatie op laptop 1.."),
                size_hint=(None, None), size=(250, 250))

            popup.open()
        else:
            self.button_start.text = "Start \nMaak eerst een foto met EOS Utility"


    
    def getDetail(self):
        """Create the detail photos"""
        # Run the getPictures function
        enough, images = self.cameraDetail.getPictures()

        # Check if there where enough images, else update button text
        if enough:
            self.images = images
            print images
            self.button_detail.text = "Detail foto's"

            # Popup done
            popup = Popup(title="Done.", 
                content = Label(text="1. Druk op de \"klaar-knop\" \n2. Druk Enter op laptop 1.."),
                size_hint=(None, None), size=(250, 250))

            popup.open()
        else:
            self.button_detail.text = "Detail foto's \nEr zijn nog %s foto's nodig" % images
            print "Need %s more images" % images


    def FConPreEnter(self):
        """Callback for filter colors screen pre_enter
        Generates color button and color filter buttons"""
        # Clear layouts
        self.buttons.clear_widgets()
        self.buttons_filter.clear_widgets()

        # Display the potential filter colors
        for color in self.potentialFilterColors:
            print "\nColor:"
            print color
            bgcolor = color[0] + (1,)
            print bgcolor

            btnText =  "{}".format(color[1])
            bttn = Button(text=btnText, background_color=bgcolor)
            bttn.bind(on_press=self.filterColor)
            self.buttons.add_widget(bttn)
            
        print "\nColorsperc:"
        print self.filterColors.colorsPerc
        # Display the filter colors
        for color in self.filterColors.colorsPerc:
            bgcolor = color[0] + (1,)

            btnText =  "{}".format(color[1])
            print color[1]
            bttn = Button(text=btnText, background_color=bgcolor)
            bttn.bind(on_press=self.removeFilterColor)
            self.buttons_filter.add_widget(bttn)
        


class VisualProfileApp(App):
    def build(self):
        mainLayout = MainLayout()
        return mainLayout


if __name__ == '__main__':
    visualProfileApp = VisualProfileApp()
    VisualProfileApp.run(visualProfileApp)


