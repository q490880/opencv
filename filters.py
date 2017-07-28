import cv2
import numpy
import utils

def strokeEdges(src,dst,blurKsize=7,edgeKsize=5):
    if blurKsize >= 3:
        blurredSrc = cv2.medianBlur(src,blurKsize)
        graySrc = cv2.cvtColor(blurredSrc,cv2.COLOR_BGR2GRAY)
    else:
        graySrc = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    cv2.Laplacian(graySrc,cv2.CV_8U,graySrc,ksize=edgeKsize)
    normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)
    channels = cv2.split(src)
    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha
    cv2.merge(channels,dst)

class VConvolutionFilter(object):
    def __init__(self,kernel):
        self._kernel = kernel

    def apply(self,src,dst):
        cv2.filter2D(src,-1,self._kernel,dst)

"""
卷积核加起来等于1,用于提升图片亮度
如果加起来等于0,则用于检测图片边缘
"""
class SharpenFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[-1,-1,-1],
                              [-1,9,-1],
                              [-1,-1,-1]])
        VConvolutionFilter.__init__(self,kernel)

"""
模糊滤波器,为了达到模糊效果,通常权重和应该为1,而且邻近的像素的权重全为正
"""
class BlurFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04],
                              [0.04,0.04,0.04,0.04,0.04]])
        VConvolutionFilter.__init__(self,kernel)

"""
以下核同时具有模糊(有正的权重)和锐化(有负的权重)的作用。这会产生一种脊状或浮雕的效果
"""
class EmbossFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[-2,-1,0],
                              [-1,1,1],
                              [0,1,2]])
        VConvolutionFilter.__init__(self,kernel)