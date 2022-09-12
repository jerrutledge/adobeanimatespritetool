from tkinter import Canvas


class SketchPad(Canvas):
    def __init__(self, parent, owner, **kwargs):
        super().__init__(parent, **kwargs)
        self.clickCallback = owner if owner else None
        self.bind("<Button-1>", self.save_posn)

    def save_posn(self, event):
        if self.clickCallback:
            canvas = event.widget
            self.clickCallback.selectPosition(
                int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y)))
