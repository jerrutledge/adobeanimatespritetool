import os
import shutil
from PIL import Image
import cv2
import numpy as np

# in order to load in first GIF frame as rbg image and not grayscale
from PIL import GifImagePlugin
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS


class ProcessGIF:
    def __init__(self) -> None:
        self.frames = []

    def emptyAndDeleteFolder(foldername):
        print("Emptying and deleting", foldername, "...")
        for filename in os.listdir(foldername):
            file_path = os.path.join(foldername, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
                raise RuntimeError
        os.rmdir(foldername)

    def autoCrop(self, g_x=0, g_y=0, g_w=1, g_h=1, callback=None):
        # expand from given points every frame until a completely transparent border is reached
        x, y, w, h = g_x, g_y, g_w, g_h

        image_height, image_width = self.frames[0].shape[0], self.frames[0].shape[1]
        # keep expanding in up, down, left & right
        dirs = [True, True, True, True]
        while True in dirs:
            dirs = [True, True, True, True]
            dirs[0] = ProcessGIF.checkRowOrColumn(self, x, x+w, y, y+1)
            dirs[0] = dirs[0] and y > 1
            if dirs[0]:
                y -= 1
                h += 1
            dirs[1] = ProcessGIF.checkRowOrColumn(self, x, x+w, y+h-1, y+h)
            dirs[1] = dirs[1] and h + y < image_height
            h += 1 if dirs[1] else 0
            dirs[2] = ProcessGIF.checkRowOrColumn(self, x, x+1, y, y+h)
            dirs[2] = dirs[2] and x > 1
            if dirs[2]:
                x -= 1
                w += 1
            dirs[3] = ProcessGIF.checkRowOrColumn(self, x+w-1, x+w, y, y+h)
            dirs[3] = dirs[3] and w + x < image_width
            w += 1 if dirs[3] else 0

        if callback is not None:
            callback.cropDone(x, y, w, h)
        return x, y, w, h

    def checkRowOrColumn(self, x1, x2, y1, y2):
        try:
            for frame in self.frames:
                # 3 represents the alpha channel
                if frame[y1:y2, x1:x2, 3].max() > 0:
                    # we've reached an non-blank pixel
                    return True
        except IndexError:
            print('HELP')
            return False
        # everything is transparent
        return False

    def loadFrames(self, inputFileName, caller=None):
        # capture the animated gif using PIL
        self.frames = []
        try:
            with Image.open(inputFileName) as imageObject:
                for frame_num in range(0, imageObject.n_frames):
                    imageObject.seek(frame_num)
                    array = np.array(imageObject)
                    self.frames.append(cv2.cvtColor(array, cv2.COLOR_BGR2RGBA))
        except Exception as e:
            if caller is not None:
                caller.imageLoadedHandler(False)
                raise e
        if caller is not None:
            caller.imageLoadedHandler()

    def getFrame(self, framenum=0):
        return self.frames[framenum]

    # remove duplicate frames & blank frames
    def ValidFrames(self, x=0, y=0, w=-1, h=-1, removeInvalidFrames=True, crop=True):
        prevCropFrame = []
        uniqueFrames = []
        for frame in self.frames:
            # crop
            cropFrame = frame
            if crop:
                cropFrame = frame[y:y+h, x:x+w]
            if len(prevCropFrame) and removeInvalidFrames:
                norm = cv2.norm(prevCropFrame, cropFrame)
                # print(norm / (w*h))
                if norm > 0.07 and cropFrame.max() > 0:
                    uniqueFrames.append(cropFrame)
            else:
                uniqueFrames.append(cropFrame)
            prevCropFrame = cropFrame
        print("Total unique frames:", len(uniqueFrames))
        return uniqueFrames

    def saveFrames(self, outputFileName, x=0, y=0, w=-1, h=-1, removeInvalidFrames=True, crop=True):
        if w == -1:
            w = self.frames[0].shape[0]
        if h == -1:
            h = self.frames[0].shape[1]
        uniqueFrames = self.ValidFrames(
            x, y, w, h, removeInvalidFrames, crop=crop)
        try:
            os.mkdir(outputFileName)
        except FileExistsError as e:
            print(e)
            print("Could not create directory", outputFileName)
            return
        try:
            for i in range(len(uniqueFrames)):
                # output to directory called output filename
                file_name = outputFileName + "/" + \
                    "frame_" + str(i) + ".png"
                cv2.imwrite(file_name, uniqueFrames[i])
        except Exception as err:
            print("ERROR, write failed")
            raise err
        print("Saved image(s) to directory", outputFileName)

    # meant for testing the whole pipeline, not meant to be called outside of this file
    def processGif(self, output_filename, g_x=0, g_y=0, g_w=1000, g_h=1000, replace=False, auto_crop=True):
        if not len(self.frames):
            print("No frames to process! Load image first")
            return

        # determine the correct crop starting from a given crop
        x, y, w, h = g_x, g_y, g_w, g_h
        if auto_crop:
            x, y, w, h = self.autoCrop(g_x, g_y, g_w, g_h)
            print("Autocrop", x, y, w, h)

        if os.path.isdir(output_filename):
            print("Directory", output_filename, "already exists")
            if replace:
                ProcessGIF.emptyAndDeleteFolder(output_filename)
            else:
                return

        self.saveFrames(output_filename, x, y, w, h, removeInvalidFrames=True)


if __name__ == "__main__":

    input_filename = "Character-walk-cycle2.gif"
    output_filename = "Coin"
    # crop
    x, y, w, h = 750, 240, 2, 2

    p = ProcessGIF()
    p.loadFrames(inputFileName=input_filename)
    p.processGif(output_filename=output_filename, g_x=x, g_y=y,
                 g_w=w, g_h=h, replace=True, auto_crop=True)
