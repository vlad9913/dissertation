import csv
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from tkinter import filedialog
import numpy as np
from scipy.interpolate import interp1d
from services.ga import GeneticAlgorithm
from threading import Thread
import customtkinter as ctk


class PlotGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Plotting GUI")
        self.master.configure(bg='black')

        self.fig = Figure(figsize=(7, 7), dpi=80,facecolor='grey')
        self.ax = self.fig.add_subplot(111)

        self.spline = None

        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        self.canvas_frame = ctk.CTkFrame(master)
        self.canvas_frame.grid(row=0, column=0, padx=5, pady=5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=1)

        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        self.coordinates = []

        self.function_map = {}
        self.attribute_diff = {}

        self.button_frame1 = ctk.CTkFrame(master)
        self.button_frame1.grid(row=0, column=1, padx=5, pady=5)

        self.button_frame2 = ctk.CTkFrame(master)
        self.button_frame2.grid(row=1, column=0, columnspan=1, padx=5, pady=5)

        self.reset_button = ctk.CTkButton(self.button_frame1, text="Reset", command=self.reset)
        self.reset_button.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

        self.draw_spline_button = ctk.CTkButton(self.button_frame1, text="Draw Spline", command=self.draw_spline)
        self.draw_spline_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.upload_csv_button = ctk.CTkButton(self.button_frame1, text="Upload CSV", command=self.upload_csv)
        self.upload_csv_button.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

        self.attribute_name_label = ctk.CTkLabel(self.button_frame1, text="Attribute Name:")
        self.attribute_name_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        self.attribute_name_entry = ctk.CTkEntry(self.button_frame1)
        self.attribute_name_entry.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

        self.save_spline_button = ctk.CTkButton(self.button_frame1, text="Save Spline", command=self.save_spline)
        self.save_spline_button.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

        self.upload_solutions_button = ctk.CTkButton(self.button_frame2, text="Upload Solutions CSV", command=self.upload_potential_solutions)
        self.upload_solutions_button.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        self.solution_size_label = ctk.CTkLabel(self.button_frame2, text="Solution Size:")
        self.solution_size_label.pack(side=tk.LEFT, padx=5, pady=2)

        self.solution_size_entry = ctk.CTkEntry(self.button_frame2)
        self.solution_size_entry.pack(side=tk.LEFT, padx=5, pady=2)

        self.run_ga_button = ctk.CTkButton(self.button_frame2, text="Run GA", command=self.run_genetic_algorithm)
        self.run_ga_button.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        self.button_frame3 = ctk.CTkFrame(master)
        self.button_frame3.grid(row=3, column=0, columnspan=1, padx=5, pady=5)

        self.chromosome_ids_box = ctk.CTkTextbox(self.button_frame3, height=200, width=800)
        self.chromosome_ids_box.pack(side=tk.LEFT, padx=5, pady=5)


        self.placeholder_label1 = ctk.CTkLabel(self.button_frame1,
        text="1. Reset: Start by clicking the 'Reset' button\n to clear any existing data on the canvas. \n\n "+
             "2. Upload CSV: Click 'Upload CSV' to select\n and load a CSV file containing your data. \nThe data points will be plotted on the canvas.\n\n"+
             "3. Alternatively, click on the graph directly\n to draw the data points on the canvas  \n\n"+
             "4. Enter Attribute Name: Type the attribute name\n associated with the data in the 'Attribute Name' field.\n\n"
             "5. Save Spline: Click 'Save Spline' to save \nthe generated spline for the given attribute name.\n The spline will be plotted in a new window.\n\n"
             "6. Upload Solutions CSV: Use 'Upload Solutions CSV' to load\n a CSV file containing potential solutions.\n\n"
             "7. Enter Solution Size: Enter the solution size\n in the 'Solution Size' field.\n\n"
             "8. Run GA: Finally, click 'Run GA' to start the \nGenetic Algorithm with the given parameters. The best solution will be\n displayed on the bottom, and its attributes will be plotted in a new window.\n\n")
        self.placeholder_label1.pack(side=ctk.BOTTOM, fill=ctk.X, padx=5, pady=5)


    def on_mouse_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            if event.button == 1 and 0 <= event.xdata <= 1:
                x, y = event.xdata, event.ydata
                self.coordinates.append((x, y))
                self.ax.scatter([x], [y], color='b')
                self.canvas.draw()

    def upload_potential_solutions(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                              filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
        if filename:
            # Load the CSV data
            self.potential_solutions = pd.read_csv(filename)
        else:
            messagebox.showerror("Error", "Please upload a CSV file.")

    def reset(self):
        self.ax.cla()
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        self.canvas.draw()
        self.coordinates = []

    def draw_spline(self):
        if self.spline:
            self.spline[0].remove()

        self.coordinates.sort(key=lambda x: x[0])

        x = [coord[0] for coord in self.coordinates]
        y = [coord[1] for coord in self.coordinates]


        f = interp1d(x, y, kind='cubic')

        x_min = min(x)
        x_max = max(x)
        xnew = np.linspace(x_min, x_max, 100)
        ynew = f(xnew)

        self.spline = self.ax.plot(xnew, ynew, 'r-')


        self.spline_data = (xnew, ynew)

        self.canvas.draw()

    def save_spline(self):
        if not self.spline:
            messagebox.showerror("Error", "No spline has been drawn yet.")
            return

        attribute_name = self.attribute_name_entry.get()

        if attribute_name == "":
            messagebox.showerror("Error", "Please enter an attribute name.")
            return

        x = [coord[0] for coord in self.coordinates]
        y = [coord[1] for coord in self.coordinates]
        self.function_map[attribute_name] = interp1d(x, y, kind='cubic', fill_value="extrapolate")

        y = [coord[1] for coord in self.coordinates]
        diff = max(y) - min(y)

        self.attribute_diff[attribute_name] = diff

        self.new_figure_window(attribute_name)

    def new_figure_window(self, attribute_name):
        new_window = tk.Toplevel(self.master)
        new_window.title("Spline for " + attribute_name)
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)

        ax.set_xlim([0, 1])

        ax.set_ylim(self.ax.get_ylim())

        xnew, ynew = self.spline_data
        ax.plot(xnew, ynew, 'r-')

        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def upload_csv(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                              filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))

        if filename:
            with open(filename, 'r') as file:
                lines = file.readlines()

            data_values = []
            for line in lines:
                values = line.strip().split(',')
                data_values.append(values)

            num_divisions_list = [len(row) for row in data_values]

            division_step_list = [(1 / (num_divisions - 1)) if num_divisions > 1 else 1 for num_divisions in
                                  num_divisions_list]

            x_values = [np.round(np.arange(0, 1 + division_step, division_step)[:num_divisions], decimals=2)
                        for division_step, num_divisions in zip(division_step_list, num_divisions_list)]

            xy_dict = {}
            for x_row, y_row in zip(x_values, data_values):
                y_row = pd.to_numeric(y_row)
                for x, y in zip(x_row, y_row):
                    if x in xy_dict:
                        xy_dict[x].append(y)
                    else:
                        xy_dict[x] = [y]

            xy_averages = {x: np.mean(y) for x, y in xy_dict.items()}
            x_values_avg = list(xy_averages.keys())
            y_values_avg = list(xy_averages.values())

            self.ax.scatter(x_values_avg, y_values_avg, color='b')

            self.ax.set_ylim([min(y_values_avg) - 1, max(y_values_avg) + 1])

            print("Values that overlap on the same x-coordinate:")
            for x, y_values in xy_dict.items():
                if len(y_values) > 1:
                    print("X =", x)
                    print("Y values:", y_values, "\n")

            self.coordinates = list(zip(x_values_avg, y_values_avg))

            self.canvas.draw()

    def run_genetic_algorithm(self):
        if not hasattr(self, 'potential_solutions'):
            messagebox.showerror("Error", "Please upload solutions CSV.")
            return

        solution_size = int(self.solution_size_entry.get())

        entities = self.potential_solutions.to_dict('records')

        ga = GeneticAlgorithm(solution_size, 300, 50, entities, self.function_map, self.attribute_diff)

        def run_ga():
            best_chromosome = ga.evolution()
            with open('fitness_values.csv', 'a', newline='') as fitness_file:
                writer = csv.writer(fitness_file)
                writer.writerow([solution_size, best_chromosome.get_fitness()])
            self.update_chromosome_ids(best_chromosome)

            new_window = tk.Toplevel(self.master)
            new_window.title("Best Chromosome Attributes")

            for attribute_name in self.function_map.keys():
                fig = Figure(figsize=(6, 5), dpi=100)
                ax = fig.add_subplot(111)

                chromosome_values = [chromosome[attribute_name] for chromosome in best_chromosome.get_repres()]
                x_values = np.linspace(0, 1, 100)
                y_values = []
                ax.set_ylim([min(chromosome_values), max(chromosome_values)])

                for x in x_values:

                    interp_func = np.interp(x, np.linspace(0, 1, len(chromosome_values)), chromosome_values)
                    y_values.append(interp_func)

                ax.plot(x_values, y_values, 'r-')

                canvas = FigureCanvasTkAgg(fig, master=new_window)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ga_thread = Thread(target=run_ga)
        ga_thread.start()

    def update_chromosome_ids(self, best_chromosome):
        ids_text = "\n".join(f"{i + 1}. {id}" for i, id in enumerate(best_chromosome.get_repres()))
        self.chromosome_ids_box.configure(state=tk.NORMAL)
        self.chromosome_ids_box.delete("1.0", tk.END)
        self.chromosome_ids_box.insert(tk.END, ids_text)
        self.chromosome_ids_box.configure(state=tk.DISABLED)

