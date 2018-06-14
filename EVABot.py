import subprocess, tempfile
from PIL import Image
from pathlib import Path
from time import sleep
from View import View
from utils import Vector2, TouchVector2#, console

class EVABot(object):

    ORIENTATION_LANDSCAPE = 1
    ORIENTATION_LANDSCAPE_REVERSED = 3
    ORIENTATION_PORTRAIT = 0
    ORIENTATION_LORTRAIT_REVERSED = 2

    def __init__(self, screenSize : tuple = (1920, 1080), ip_address : str = None, runFromDevice : bool = False):
        self.runFromDevice = runFromDevice
        self.ip_address = ip_address
        if not ip_address is None and not runFromDevice:
            if not isinstance(ip_address, str) or (
                    len(ip_address.split('.')) != 4 or len(ip_address.split('.')[-1].split(':')) != 2):
                raise ValueError('EVABot : ip_address variable should respect the "x.x.x.x:y" format, "y" being the '
                                 f'port. Received "{ip_address}" instead.')
            self.reconnect
        self.screenSize = screenSize
        self._tmpImageFileName = 'screen.dump'
        self._tmpImage = None
        self.viewList = []
        self.deviceOrientation = self.getDeviceOrientation()

    def getDeviceOrientation(self, input : str = None, setValue : bool = False):
        if input is None:
            adb_cmd = ('su', '-c') if self.runFromDevice else ('adb', 'shell')
            output = subprocess.check_output(adb_cmd + ('dumpsys', 'input'))
        else:
            output = input
        orientationStart = output.find(b'SurfaceOrientation')
        orientation = int(output[orientationStart + 20]) - ord('0')
        if setValue:
            self.deviceOrientation = orientation
        return orientation

    def getScreenSize(self, orientationCorrection : bool = True, setValue : bool = False):
        adb_cmd = ('su', '-c') if self.runFromDevice else ('adb', 'shell')
        output = subprocess.check_output(adb_cmd + ('dumpsys', 'input'))
        widthStart = output.find(b'SurfaceWidth')
        heightStart = output.find(b'SurfaceHeight')
        width = int(output[widthStart + 14:widthStart + 18].strip(b'px'))
        height = int(output[heightStart + 15:heightStart + 19].strip(b'px'))
        if orientationCorrection:
            orientation = self.getDeviceOrientation(input=output, setValue=True)
            if orientation in (EVABot.ORIENTATION_LANDSCAPE, EVABot.ORIENTATION_LANDSCAPE_REVERSED):
                width, height = height, width
        if setValue:
            self.screenSize = (width, height)
        return (width, height)

    def loadConfFile(self, fileName : str):
        import json
        jsonData = Path(fileName).read_text()
        viewData = json.loads(jsonData)[View.VIEW_ID]
        del jsonData
        self.viewList = []
        for viewID in viewData:
            self.viewList.append(View.loadFromDict(viewData[viewID]))
        del viewData
        self.viewList = tuple(self.viewList)

    def getScreen(self):
        if self.runFromDevice:
            screenData = subprocess.run(('su', '-c', 'screencap'), stdout=subprocess.PIPE).stdout
        else:
            screenData = subprocess.run(('adb', 'shell', 'screencap'), stdout=subprocess.PIPE).stdout
        if hasattr(self, '_tmpImage'):
            del self._tmpImage
        self._tmpImage = Image.frombytes('RGBA', self.screenSize, screenData)
        del screenData
        return True

    def reconnect(self):
        if self.ip_address is None or self.runFromDevice:
            return
        self.runCMD(('adb', 'disconnect'))
        self.runCMD(('adb', 'connect', f'{self.ip_address}'))

    def checkForView(self):
        try:
 #           console.print('Capturing screen', 0)
            self.getScreen()
        except (ValueError, subprocess.CalledProcessError):
            # console.print(f'{console.icho.bold}{console.icho.red}'
            #               'Error capturing screen'
            #               f'{console.icho.normal}', 0)
            print('Error capturing screen')
            self.reconnect()
            return False
        idx = len(self.viewList)
        for view in self.viewList:
            position = (len(self.viewList) - idx) // len(self.viewList)
#            console.print(f'View: {view.name}', position)
            idx -= 1
            if view.isView(self._tmpImage):
                # console.print(f'View: {view.name} '
                #               f'{console.icho.bold}'
                #               f'{console.icho.cyan}'
                #               f'OK{console.icho.normal}', 1)
                for touch in view.touchArray:
                    self.touchScreen(touch)
                    sleep(view.touchDelay / 1000)
                for longTouch in view.longTouchArray:
                    self.longTouchScreen(longTouch)
                    sleep(view.touchDelay / 1000)
                return True
#        console.print('No view found', 1)
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
            subprocess.call(('su', '-c', ' '.join(command_array[2:])))
        else:
            subprocess.call(command_array)

    @staticmethod
    def run(ip_address : str = None, fileName : str = 'views.json', sleepTime : int = 100,runFromDevice : bool = False):
        tmpDaemon = EVABot(ip_address=ip_address, runFromDevice=runFromDevice)
        tmpDaemon.loadConfFile(fileName)
        idx = 0
        while True:
            if not tmpDaemon.checkForView():
                sleep((sleepTime / 1000) + (idx // 10))
                idx += 1
            else: idx = 0


if __name__=='__main__':
    import platform
    if platform.machine() == 'x86_64':
        EVABot.run(sleepTime=400)
    else:
        EVABot.run(runFromDevice=True, sleepTime=400)
