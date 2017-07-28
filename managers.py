import cv2
import numpy
import time

class CaptureManager(object):
    def __init__(self,capture,previewWindowManager = None,shouldMirrorPreview=False):
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._VideoWriter = None

        self._startTime = None
        self._framesElapsed = long(0)
        self._fpsEstimeate = None

    # @property
    # def channel(self):
    #     return self._channel
    #
    # @channel.setter
    # def channel(self,value):
    #     if self._channel != value:
    #         self._channel = value
    #         self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            self._enteredFrame,self._frame = self._capture.retrieve()
        return self._frame

    @property
    def isWritingImage(self):
        return self._imageFilename is not None

    @property
    def isWritingVideo(self):
        return self._videoFilename is not None

    def enterFrame(self):
        if self._capture is not None:
            self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        if self.frame is None:
            self._enteredFrame = False
            return
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimeate = self._framesElapsed / timeElapsed

        self._framesElapsed += 1
        if self.previewWindowManager is not None:
            if self.shouldMirrorPreview:
                #mirroredFrame = numpy.fliplr(self._frame).copy()
                mirroredFrame = self._frame
                self.previewWindowManager.show(mirroredFrame)
            else:
                self.previewWindowManager.show(self._frame)

        if self.isWritingImage:
            cv2.imwrite(self._imageFilename,self._frame)
            self._imageFilename = None

        self._writeVideoFrame()
        self._frame = None
        self._enteredFrame = False

    def writeImage(self,filename):
        self._imageFilename = filename

    def startWritingVideo(self,filename,encoding = cv2.VideoWriter_fourcc('I','4','2','0')):
        self._videoFilename = filename
        self._videoEncoding = encoding

    def stopWritingVideo(self):
        self._videoFilename = None
        self._videoEncoding = None
        self._VideoWriter = None

    def _writeVideoFrame(self):
        if not self.isWritingVideo:
            return
        if self._VideoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps == 0.0:
                if self._framesElapsed < 20:
                    return
                else:
                    fps = self._fpsEstimeate
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self._VideoWriter = cv2.VideoWriter(self._videoFilename,self._videoEncoding,fps,size)
            self._VideoWriter.write(self.frame)

class WindowManager(object):
    def __init__(self,windowName,keypressCallback=None):
        self.keypressCallback = keypressCallback
        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):
        return self._isWindowCreated

    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True

    def show(self,frame):
        cv2.imshow(self._windowName,frame)

    def destroyWindow(self):
        cv2.destroyAllWindows(self._windowName)
        self._isWindowCreated = False

    def processEvent(self):
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            keycode &= 0xFF
            self.keypressCallback(keycode)