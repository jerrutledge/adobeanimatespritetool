import os, shutil
from tabnanny import check
from turtle import width
from PIL import Image
import cv2
import numpy as np

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

def autoCrop(frames, g_x=0, g_y=0, g_w=1, g_h=1):
    # expand from given points every frame until a completely transparent border is reached
    x, y, w, h = g_x, g_y, g_w, g_h
    
    image_width, image_height = frames[0].shape[0], frames[0].shape[1]
    dirs = [True, True, True, True] # keep expanding in up, down, left & right
    while True in dirs:
        dirs = [True, True, True, True]
        dirs[0] = checkRowOrColumn(frames, x, x+w, y, y+1) and y > 1
        y -= 1 if dirs[0] else 0
        dirs[1] = checkRowOrColumn(frames, x, x+w, y+h-1, y+h) and h < image_height - y
        h += 1 if dirs[1] else 0
        dirs[2] = checkRowOrColumn(frames, x, x+1, y, y+h) and x > 1
        x -= 1 if dirs[2] else 0
        dirs[3] = checkRowOrColumn(frames, x+w-1, x+w, y, y+h) and w < image_width - x
        w += 1 if dirs[3] else 0

    return x, y, w, h

def checkRowOrColumn(frames, x1, x2, y1, y2):
    try:
        for frame in frames:
            if frame[x1:x2, y1:y2].max() >= 0:
                # we've reached an non-blank pixel
                return True
    except IndexError:
        print('HELP')
        return False
    # everything is transparent
    return False


def processGif(input_filename, output_filename, g_x=0, g_y=0, g_w=1000, g_h=1000, replace = False, auto_crop=True):
    # capture the animated gif using PIL
    frames = []
    with Image.open(input_filename) as imageObject:
        for frame_num in range(0, imageObject.n_frames):
            imageObject.seek(frame_num)
            frames.append(cv2.cvtColor(np.array(imageObject), cv2.COLOR_BGR2RGBA))

    # determine the correct crop starting from a given crop
    x, y, w, h = g_x, g_y, g_w, g_h
    if auto_crop:
        x, y, w, h = autoCrop(frames, g_x, g_y, g_w, g_h)
        print("Autocrop", x,y,w,h)

    #remove duplicate frames
    prevCropFrame = []
    uniqueFrames = []
    for frame in frames[1:]: # only the frames after the first 
        # crop
        cropFrame = frame[x:x+w, y:y+h]
        if len(prevCropFrame):
            norm = cv2.norm(prevCropFrame, cropFrame)
            # print(norm / (w*h))
            if norm > 0.07 and cropFrame.max() > 0:
                uniqueFrames.append(cropFrame)
        else:
            uniqueFrames.append(cropFrame)
        prevCropFrame = cropFrame

    print(len(uniqueFrames), "unique frames total")
    if os.path.isdir(output_filename):
        print("Directory", output_filename, "already exists")
        if replace:
            emptyAndDeleteFolder(output_filename)
        else:
            return
    
    os.mkdir(output_filename)
    print("Created directory", output_filename)
    try:
        for i in range(len(uniqueFrames)):
            # output to directory called output filename
            file_name = output_filename + "/" + output_filename + "_" + str(i) + ".png"
            cv2.imwrite(file_name, uniqueFrames[i])
        return
    except Exception as err:
        print("ERROR, write failed")
        print(err)
    print("Trying to clean up directory", output_filename, "...")
    os.rmdir(output_filename)
    print("Directory", output_filename, "successfully removed")

if __name__ == "__main__":

    input_filename = "Character-walk-cycle2.gif"
    output_filename = "Character"
    # crop
    x, y, w, h = 50, 50, 60, 60

    processGif(input_filename, output_filename, x, y, w, h, replace=True)