import json
from PIL import Image
from pathlib import Path
from collections import namedtuple
from blessings import Terminal

Vector2 = namedtuple('Vector2', ['x', 'y'])

TouchVector2 = namedtuple('TouchVector2', ['x', 'y', 'duration'])

PixelVector2 = namedtuple('PixelVector2', ['position', 'color'])

def getPixelHex(image, position : Vector2):
    irgb = image.getpixel(position)
    hexString = intRGBToHexString(irgb)
    return hexString

def intRGBToHexString(irgb : tuple):
    hexString = f'#{irgb[0]:02x}{irgb[1]:02x}{irgb[2]:02x}'
    return hexString

def convertResources(fileName : str = 'views.json'):
    jsonData = json.loads(Path(fileName).read_text())
    viewData = jsonData['views']
    for viewID in viewData:
        view = viewData[viewID]
        viewIm = Image.frombytes('RGBA', (1920, 1080), Path(view['reference']).read_bytes())
        print(f'File {view["name"]}')
        viewIm.save(view['reference'].replace('dump', 'png'), 'PNG')
        viewIm.close()
    return True

def collectNewPixelValues(fileName : str = 'views.json', save : bool = False):
    jsonData = json.loads(Path(fileName).read_text())
    viewData = jsonData['views']
    for viewID in viewData:
        view = viewData[viewID]
        viewIm = Image.frombytes('RGBA', (1920, 1080), Path(view['reference']).read_bytes())
        print(f'File {view["name"]}')
        searchPixels = view['searchPixels']
        for pixelID in searchPixels:
            pixel = searchPixels[pixelID]
            irgb = viewIm.getpixel((pixel[0], pixel[1]))
            hexString = f'#{irgb[0]:02x}{irgb[1]:02x}{irgb[2]:02x}'
            if hexString != pixel[2]:
                print(f'For pixel ({pixel[0]}, {pixel[1]}) found {hexString} expected {pixel[2]}')
            jsonData['views'][viewID]["searchPixels"][pixelID][2] = hexString
        viewIm.close()
        print('OK')
    if save:
        with open(fileName, 'w') as newFile:
            newFile.write(json.dumps(jsonData))
    return jsonData

class RunConsole(object):

    def __init__(self, header : str = 'EVABot v0.1.1'):
        self.icho = Terminal()
        self.lastMessage = ''
        self.lastPercentage = 0
        self.width = 40
        self.header = f'{self.icho.bold}{self.icho.cyan}{header.center(self.width)}{self.icho.normal}'
        self.bar = f'[{self.icho.bold}{self.icho.yellow}%s{self.icho.nomal}{self.icho.red}%s{self.icho.normal}]'

    def update(self, percent : int = 0, message : str = ''):
        print(self.header)
        n = (self.width-10) * percent
        print(f'{self.icho.bold}{self.icho.yellow}'
              f'{("[" + ("="*n) + "-"*(self.width - 10 - n) + "]").center(self.width)}'
              f'{self.icho.normal}')
        print((f'{message.center(self.width)}'))

    def clear(self):
        print(f'{self.icho.clear_bol}{self.icho.move_up}'
              f'{self.icho.clear_eol}{self.icho.move_up}'
              f'{self.icho.clear_eol}{self.icho.move_up}'
              f'{self.icho.clear_eol}{self.icho.move_up}')

    def print(self, message : str = None, percentage : int = -1):
        if message is None:
            message = self.lastMessage
        if percentage < 0:
            percentage = self.lastPercentage
        self.clear()
        self.update(percentage, message)
        self.lastMessage = message
        self.lastPercentage = percentage

#console = RunConsole()