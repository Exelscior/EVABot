import subprocess
from PIL import Image
from pathlib import Path
from time import sleep
from View import View
from utils import Vector2, TouchVector2, console

class EVABot(object):

    def __init__(self, screenSize : tuple = (1920, 1080), ip_address : str = None, runFromDevice : bool = False):
        self.runFromDevice = runFromDevice
        if not ip_address is None:
            if not isinstance(ip_address, str) or (
                    len(ip_address.split('.')) != 4 or len(ip_address.split('.')[-1].split(':')) != 2):
                raise ValueError('EVABot : ip_address variable should respect the "x.x.x.x:y" format, "y" being the '
                                 f'port. Received "{ip_address}" instead.')
            self.runCMD(('adb', 'connect', f'{ip_address}'))
        self.ip_address = ip_address
        self.screenSize = screenSize
        self._tmpImageFileName = 'screen.dump'
        self._tmpImage = None
        self.viewList = []

    def loadConfFile(self, fileName : str):
        import json
        jsonData = Path(fileName).read_text()
        viewData = json.loads(jsonData)[View.VIEW_ID]
        self.viewList = []
        for viewID in viewData:
            self.viewList.append(View.loadFromDict(viewData[viewID]))
        self.viewList = tuple(self.viewList)

    def getScreen(self):
        screenData = subprocess.check_output(('adb', 'shell', 'screencap'))
        self._tmpImage = Image.frombytes('RGBA', self.screenSize, screenData)
        return True

    def checkForView(self):
        try:
            console.print('Capturing screen', 0)
            self.getScreen()
        except ValueError:
            console.print(f'{console.icho.bold}{console.icho.red}'
                          'Error capturing screen'
                          f'{console.icho.normal}', 0)
            return False
        idx = len(self.viewList)
        for view in self.viewList:
            position = (len(self.viewList) - idx) // len(self.viewList)
            console.print(f'View: {view.name}', position)
            idx -= 1
            if view.isView(self._tmpImage):
                console.print(f'View: {view.name} '
                              f'{console.icho.bold}'
                              f'{console.icho.cyan}'
                              f'OK{console.icho.normal}', 1)
                for touch in view.touchArray:
                    self.touchScreen(touch)
                    sleep(view.touchDelay / 1000)
                return True
        console.print('No view found', 1)
        return False

    def touchScreen(self, position : Vector2):
        self.runCMD(('adb', 'shell', 'input', 'touchscreen', 'tap', f'{position.x}', f'{position.y}'))

    def longTouchScreen(self, position : TouchVector2):
        self.runCMD(('adb', 'shell', 'input', 'touchscreen', 'swipe',
                         f'{position.x}', f'{position.y}', f'{position.x}', f'{position.y}',
                         f'{position.duration}'))

    def runCMD(self, command : 'str or list'):
        if isinstance(command, str):
            command_array = command.split(' ')
        elif isinstance(command, (tuple, list)):
            command_array = command
        if self.runFromDevice:
            subprocess.call(command_array[2:])
        else:
            subprocess.call(command_array)

    @staticmethod
    def run(ip_address : str = None, fileName : str = 'views.json', sleepTime : int = 100):
        tmpDaemon = EVABot(ip_address=ip_address)
        tmpDaemon.loadConfFile(fileName)
        idx = 0
        while True:
            if not tmpDaemon.checkForView():
                sleep((sleepTime / 1000) + (idx // 10))
                idx += 1
            else: idx = 0
