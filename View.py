from PIL import Image
from pathlib import Path
from utils import Vector2, TouchVector2, PixelVector2, getPixelHex

class View(object):
    """Class corresponding to a view

    A view can be considered a page within the application.
    Each view will have a name, a set of Pixels to compare to the image, and an array of inputs to perform if the
    image is recognized as the view.

    touchDelay corresponds to the wait time in ms between each input in the case there are several.
    """
    VIEW_ID = 'views'
    NAME_ID = 'name'
    REFERENCE_ID = 'reference'
    DELAY_ID = 'delay'
    TOUCH_ID = 'touches'
    LONG_TOUCH_ID = 'longtouches'
    SEARCH_PIXEL_ID = 'searchPixels'

    def __init__(self, name : str ='NoName View', referenceImage : str = 'screen.dump'):
        self.name = name
        self.referenceImage = Path(referenceImage)
        self.searchPixelArray = ()
        self.longTouchArray = ()
        self.touchArray = ()
        self.touchDelay = 100

    def addSearchPixel(self, position : Vector2, hexRGB : str):
        searchArray = list(self.searchPixelArray)
        searchArray.append(PixelVector2(position, hexRGB))
        self.searchPixelArray = tuple(searchArray)

    def addTouch(self, position : Vector2):
        touchArray = list(self.touchArray)
        touchArray.append(position)
        self.touchArray = tuple(touchArray)

    def addLongTouch(self, timedPosition : TouchVector2):
        touchArray = list(self.longTouchArray)
        touchArray.append(timedPosition)
        self.longTouchArray = tuple(touchArray)

    def isView(self, image : Image):
        for pixel in self.searchPixelArray:
            im_pixel = getPixelHex(image, pixel.position)
            if im_pixel != pixel.color:
                return False
        return True

    @staticmethod
    def loadFromDict(viewDict):
        view = View(viewDict[View.NAME_ID], viewDict[View.REFERENCE_ID])
        searchPixels = viewDict[View.SEARCH_PIXEL_ID]
        for pixelID in searchPixels:
            view.addSearchPixel(Vector2(searchPixels[pixelID][0], searchPixels[pixelID][1]), searchPixels[pixelID][2])
        if View.TOUCH_ID in viewDict:
            touches = viewDict[View.TOUCH_ID]
            for touchID in touches:
                view.addTouch(Vector2(touches[touchID][0], touches[touchID][1]))
        if View.LONG_TOUCH_ID in viewDict:
            longTouches = viewDict[View.LONG_TOUCH_ID]
            for touchID in longTouches:
                view.addLongTouch(TouchVector2(
                        longTouches[touchID][0],
                        longTouches[touchID][1],
                        longTouches[touchID][2]
                ))
        if View.DELAY_ID in viewDict:
            view.touchDelay = viewDict[View.DELAY_ID]
        return view
