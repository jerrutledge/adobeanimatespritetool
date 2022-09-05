from lib2to3.pgen2.token import NAME
from tkinter import *
from tkinter import ttk
from SketchPad import SketchPad

root = Tk()
content = ttk.Frame(root, padding=(3, 3, 12, 12))
frame = ttk.Frame(content, borderwidth=3, relief="ridge", width=200, height=100)

# canvas
h = ttk.Scrollbar(frame, orient=HORIZONTAL)
v = ttk.Scrollbar(frame, orient=VERTICAL)

canvas = SketchPad(frame, scrollregion=(
    0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
h['command'] = canvas.xview
v['command'] = canvas.yview
canvas.grid(column=0, row=0, sticky=(N, W, E, S))
h.grid(column=0, row=1, sticky=(W,E))
v.grid(column=1, row=0, sticky=(N,S))
frame.grid_columnconfigure(0, weight=1)
frame.grid_rowconfigure(0, weight=1)

# Settings
fileName = ttk.Button(content, text="Select File")
fileNameLabel = ttk.Label(content, text="No file selected...")

okButton = ttk.Button(content, text="Save Files")
clearButton = ttk.Button(content, text="Clear")

# grid layout definitions
content.grid(column=0, row=0, sticky=(N, S, E, W))
frame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=(N, S, E, W))
fileName.grid(column=3, row=0, columnspan=2, sticky=(N, E, W), pady=5, padx=5)
fileNameLabel.grid(column=3, row=1, columnspan=2, sticky=(N, W), padx=5)
okButton.grid(column=3, row=2)
clearButton.grid(column=4, row=2)

# resizing options
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=1)
content.columnconfigure(4, weight=1)
content.rowconfigure(1, weight=1)

root.mainloop()
