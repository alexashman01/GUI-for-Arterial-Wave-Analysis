import tkinter as tk
import matplotlib
from homepage import Homepage
from inputpage import InputPage
from velocityimage import VelocityImage
from diameterimage import DiameterImage
from ptnew import PtNew
from smoothdata import SmoothData
from puadjust import PUAdjust
from puloop import PULoop
from outputpage import OutputPage
from windkessel import Windkessel


# Main file which links all pages of the GUI

class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("1000x700")  # Set windows size for the GUI
        self.resizable(width=False, height=False)  # Disable resizing the window

        # Creates the container which will hold all pages of the GUI. The current page will move to the top, so it is
        # the only one visible to the user.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (
                Homepage, InputPage, VelocityImage, DiameterImage, PtNew, SmoothData, PUAdjust, PULoop, OutputPage,
                Windkessel):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Homepage")

        matplotlib.rcParams.update({'font.size': 12, 'font.family': 'Roboto'})  # Set font for all plots in GUI

    # show_frame() will be called throughout the program to allow switching between frames on a button click.
    def show_frame(self, page_name):
        # This function is called throughout GUI to switch between pages
        frame = self.frames[page_name]
        frame.tkraise()


# Main Tkinter events loop.
if __name__ == "__main__":
    app = Main()
    app.mainloop()
