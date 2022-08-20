import os, shutil
import cv2
import numpy as np
import matplotlib.pyplot as plt

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

def processGif(input_filename, output_filename, x=0, y=0, w=1000, h=1000, replace = False):
    # capture the animated gif
    gif = cv2.VideoCapture(input_filename)
    frames = []
    prevGrayFrame = []
    ret, frame = gif.read()  # ret=True if it finds a frame else False.
    while ret:
        # read next frame
        ret, frame = gif.read()
        if not ret:
            break

        # crop
        grayFrame = frame[y:y+h, x:x+w]
        if len(prevGrayFrame):
            norm = cv2.norm(prevGrayFrame, grayFrame)
            print(norm / (w*h))
            if norm > 0.07:
                frames.append(grayFrame)
        else:
            frames.append(frame)
        prevGrayFrame = grayFrame

    print(len(frames))
    if os.path.isdir(output_filename):
        print("Directory", output_filename, "already exists")
        if replace:
            emptyAndDeleteFolder(output_filename)
        else:
            return
    
    os.mkdir(output_filename)
    print("Created directory", output_filename)
    try:
        for i in range(len(frames)):
            # output to directory called output filename
            file_name = output_filename + "/" + output_filename + "_" + str(i) + ".png"
            cv2.imwrite(file_name, frames[i])
            print(file_name)
        return
    except Exception as err:
        print("ERROR, write failed")
        print(err)
    print("Trying to clean up directory", output_filename, "...")
    os.rmdir(output_filename)
    print("Directory", output_filename, "successfully removed")

cv2.destroyAllWindows()

if __name__ == "__main__":

    input_filename = "Character-walk-cycle2.gif"
    output_filename = "Character"
    # crop
    x, y, w, h = 1, 1, 460, 500

    processGif(input_filename, output_filename, x, y, w, h, replace=True)