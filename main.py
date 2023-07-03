import tkinter as tk
import customtkinter as ctk
from ui.plotgui import PlotGUI
from utils.csvhelpers import *

root = ctk.CTk()
plot_gui = PlotGUI(root)
root.mainloop()


#
# num_lines = 5000
# filename = 'data.csv'
# write_to_csv(filename, num_lines)
#
# print(f'{num_lines} lines of data have been written to "{filename}"')
