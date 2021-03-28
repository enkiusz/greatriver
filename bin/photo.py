#!/usr/bin/env python3

from urllib.request import urlopen
from urllib.parse import urljoin
from tkinter import *
from PIL import Image, ImageTk
import io
import os

url = os.getenv('IP_WEBCAM_URL')

class App(object):
    def __init__(self):

        root = Tk()
        
        frame = Frame(root)
        frame.pack(expand = True, fill=BOTH)
        
        self.images = []

        img = ImageTk.PhotoImage(Image.new('RGB', (100,100)))
        self.lbl = Label(frame, image=img)
        self.lbl.pack(expand=True, fill=BOTH)
         
        root.bind("<KeyPress-S>", self.makeshot)
        root.bind("<KeyPress-s>", self.makeshot)
        root.bind("<KeyPress-F>", self.focus)
        root.bind("<KeyPress-f>", self.focus)
        root.bind("<KeyPress-d>", self.delete)
        root.bind("<KeyPress-D>", self.delete)
        root.bind("<KeyPress-p>", self.publish)
        root.bind("<KeyPress-P>", self.publish)       

        root.mainloop()

    def fetch_image(self):
        with urlopen(urljoin(url,'/shot.jpg')) as req:
            return req.read()

    def showimage(self, content):
        stream = io.BytesIO(content)
        img = ImageTk.PhotoImage(Image.open(stream))
    
        self.lbl.configure(image=img)
        self.lbl.image = img
        self.lbl.pack(expand=True, fill=BOTH)

    def focus(self, event):
        with urlopen(urljoin(url, '/focus')) as req:
            req.read()

    def makeshot(self, event):
        content = self.fetch_image()

        self.images.append(content)
        self.showimage(content)
        
    def delete(self, event):

        self.images.pop()
        if len(self.images) > 0:
            self.showimage(self.images[-1])
        else:
            img = ImageTk.PhotoImage(Image.new('RGB', (100,100)))
            self.lbl.configure(image=img)
            self.lbl.image = img
            self.lbl.pack(expand=True, fill=BOTH)

    def publish(self, event):
        for (i, img) in enumerate(self.images):
            while Path(f"img_{i}.jpg").exists():
                i += 1
            Path(f"img_{i}.jpg").write_bytes(img)

if __name__ == "__main__":
    App()
