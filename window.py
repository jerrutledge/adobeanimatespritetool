from cgitb import handler
from lib2to3.pgen2.token import NAME
from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from SketchPad import SketchPad
from ProcessGIF import ProcessGIF
from crop import Crop


class Window():
    def __init__(self):
        # Variables
        self.fileName = ""
        self.myImage = None
        # Window
        self.root = Tk()
        self.content = ttk.Frame(self.root, padding=(3, 3, 12, 12))
        frame = ttk.Frame(self.content, borderwidth=3,
                          relief="ridge", width=200, height=100)
        self.gif = None
        self.loadingThread = None
        self.crops = []

        # canvas
        h = ttk.Scrollbar(frame, orient=HORIZONTAL)
        v = ttk.Scrollbar(frame, orient=VERTICAL)

        self.canvas = SketchPad(frame, owner=self, scrollregion=(
            0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
        h['command'] = self.canvas.xview
        v['command'] = self.canvas.yview
        self.canvas.grid(column=0, row=0, sticky=(N, W, E, S))
        h.grid(column=0, row=1, sticky=(W, E))
        v.grid(column=1, row=0, sticky=(N, S))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Settings
        self.fileName = ttk.Button(
            self.content, text="Select File", command=lambda: Window.fileNameHandler(self))
        self.fileNameLabel = ttk.Label(
            self.content, text="No file selected...")
        self.statusLabel = ttk.Label(self.content, text="Ready.")

        self.okButton = ttk.Button(
            self.content, text="Save Files", command=lambda: Window.okButtonHandler(self))
        self.clearButton = ttk.Button(
            self.content, text="Clear", command=lambda: Window.clearButtonHandler(self))

        # grid layout definitions
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        frame.grid(column=0, row=0, columnspan=3,
                   rowspan=4, sticky=(N, S, E, W))
        self.fileName.grid(column=3, row=0, columnspan=2,
                           sticky=(N, E, W), pady=5, padx=5)
        self.fileNameLabel.grid(
            column=3, row=1, columnspan=2, sticky=(N, W), padx=5)
        self.statusLabel.grid(
            column=3, row=2, columnspan=2, sticky=(N, W), padx=5)
        self.okButton.grid(column=3, row=3)
        self.clearButton.grid(column=4, row=3)

        # resizing options
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=3)
        self.content.columnconfigure(2, weight=3)
        self.content.columnconfigure(3, weight=1)
        self.content.columnconfigure(4, weight=1)
        self.content.rowconfigure(1, weight=1)

    # Button Handlers
    def fileNameHandler(self):
        newFileName = filedialog.askopenfilename(title="Select A File")
        if len(newFileName):
            self.fileName = newFileName
            self.fileNameLabel.config(text="Loading GIF... \n"+self.fileName)
            self.gif = ProcessGIF()
            self.loadingThread = Thread(
                target=lambda: ProcessGIF.loadFrames(self.gif, self.fileName, self))
            self.loadingThread.start()
            self.fileNameLabel.config(text="Loading GIF... \n"+self.fileName)

    def okButtonHandler(self):
        if not self.gif:
            self.statusLabel.config(text="No image loaded!")
            return
        # TODO: filename dialogue
        filename = filedialog.asksaveasfilename()
        if not filename:
            # the user cancalled the file dialog
            return
        # save the files
        removeInvalidFrames = True
        # TODO: invalid frames checkbox?
        if len(self.crops):
            # last element?
            x, y, w, h = self.crops[len(self.crops) - 1].getCrop()
            self.gif.saveFrames(filename, x, y, w, h, removeInvalidFrames)
        else:
            self.gif.saveFrames(filename, crop=False)

    def clearButtonHandler(self):
        self.fileName = ""
        self.fileNameLabel.config(text="No file selected...")
        self.myImage = None
        self.canvas.delete('all')
        self.crops.clear()

    def runloop(self):
        self.root.mainloop()

    def selectPosition(self, x, y):
        print("clicked on position", x, y)
        if self.loadingThread and self.loadingThread.is_alive():
            print("we're busy")
            return
        if self.gif is None:
            return
        self.loadingThread = Thread(
            target=lambda: self.gif.autoCrop(x, y, callback=self))
        self.loadingThread.start()
        self.statusLabel.config(text="Working on crop...")

    # work done handlers
    def imageLoadedHandler(self, success=True):
        if not success:
            self.fileNameLabel.config(text="Image Load failed??? Check log?")
            return
        self.fileNameLabel.config(text="Selected GIF: \n" + self.fileName)
        self.myImage = PhotoImage(file=self.fileName)
        self.canvas.create_image(0, 0, image=self.myImage, anchor='nw')

    def cropDone(self, x, y, w, h):
        # TODO: clear old rectangle
        print("cropdone", x, y, w, h)
        cropName = self.canvas.create_rectangle(x, y, x+w, y+h, outline='blue')
        self.statusLabel.config(text="Crop done!")
        self.crops.append(Crop(x, y, w, h, name=cropName))


if __name__ == "__main__":
    W = Window()
    W.runloop()
