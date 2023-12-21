from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import shapefile
from shapely.geometry import shape, polygon
import matplotlib.pyplot as plt
import geopandas as gpd
from tkinter import ttk 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import Slider
import math
import subprocess
from PIL import ImageTk


'''
# Create a new style for the GUI
style = ttk.Style()
style.theme_create("custom_style", parent="clam", settings={
    "TButton": {
        "configure": {"background": "#3498db", "foreground": "white", "font": ('Arial', 12)},
        "map": {"background": [("active", "#2980b9")]}
    },
    "TEntry": {
        "configure": {"font": ('Arial', 12)}
    },
    "TLabel": {
        "configure": {"font": ('Arial', 12)}
    }
})
style.theme_use("custom_style")

root = Tk()

W = str(root.winfo_screenwidth())
H = str(root.winfo_screenheight())
root.configure(width=W, height=H, bg="#2ecc71")  # Background color changed to a green shade
root.title("Modified Boundary Parcel Delination")

v = StringVar()

left_frame = Frame(root, width=400, height=1000, bg='#3498db')  # Background color changed to a blue shade
left_frame.grid(row=0, column=0, padx=10, pady=5)

self.right_frame = Frame(root, width=750, height=500, bg='#ecf0f1')  # Background color changed to a light gray shade
right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

fig = Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=right_frame)

tool_bar = Frame(left_frame, width=180, height=185)
toolbar = Frame(left_frame, width=180, height=185)
tool_bar.grid(row=2, column=0, padx=5, pady=5)
toolbar.grid(row=10, column=0, padx=5, pady=20)

label_filename = ttk.Label(tool_bar, text="Select shape file(.shp)")
label_filename.grid(row=0, column=0, padx=5, pady=3, ipadx=10)

e1 = ttk.Entry(tool_bar, textvariable=v)
e1.grid(row=1, column=0)

button_browse = ttk.Button(tool_bar, text="Browse", command=set_select_file, style='TButton')
button_browse.grid(row=2, column=0, padx=5, pady=5)
button_browse.bind("<Enter>", on_hover)
button_browse.bind("<Leave>", on_leave)

label_parcel_number = ttk.Label(tool_bar, text="Parcel Number")
label_parcel_number.grid(row=3, column=0, padx=5, pady=3, ipadx=10)

e2 = ttk.Entry(tool_bar)
e2.grid(row=4, column=0)

button_show = ttk.Button(tool_bar, text="Show", style='TButton')
button_show.grid(row=5, column=0, pady=4, ipadx=10)
button_show.bind("<Enter>", on_hover)
button_show.bind("<Leave>", on_leave)

button_quit = ttk.Button(tool_bar, text="Quit", command=root.quit, style='TButton')
button_quit.grid(row=6, column=0, pady=4, ipadx=10)
button_quit.bind("<Enter>", on_hover)
button_quit.bind("<Leave>", on_leave)

button_display_parcel = ttk.Button(toolbar, text="Show Parcel Direction", command=get_ewns_parcel, style='TButton')
button_display_parcel.grid(row=6, column=0, pady=4, ipadx=10)
button_display_parcel.bind("<Enter>", on_hover)
button_display_parcel.bind("<Leave>", on_leave)

label_output = ttk.Label(toolbar, text="Output")
label_output.grid(row=0, column=0, padx=5, pady=5)

root.mainloop()
'''

import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog as fd 
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Modified Boundary Parcel Delination")
        self.geometry(f"{1100}x{580}")

        self.shpFile = ''
        self.parcelNumber = 0

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

          
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Boundary Detx", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_file, text="Browse File")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_input_dialog_event, text="Enter Parcel Number")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_result, text="Show Parcel")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Quit")
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Show parcel direction")
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)
        


        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))

       # create textbox
        # self.textbox = customtkinter.CTkTextbox(self, width=250)
        # self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

       # create canvas 
        self.right_frame = customtkinter.CTkCanvas(
            self, width = 250, bg="lightblue")
        # self.right_frame.grid_columnconfigure(0, weight=1)
        
        self.right_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

       
        self.appearance_mode_optionemenu.set("Light")
        self.scaling_optionemenu.set("100%")
       
        # self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
       
    def open_file(self):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename ( 
            title='Open a file',
            initialdir='/',
            filetypes=filetypes
        )

        self.shpFile = filename
        # print(filename)

    

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        self.parcelNumber=int(dialog.get_input())
        # print("parcelNumber: ", self.parcelNumber)
        # print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


    def get_screen_resolution():
        try:
            # Run the xrandr command and capture the output
            result = subprocess.run(['xrandr'], stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8')

            # Find the line that contains information about the primary display
            primary_display_line = next(line for line in output.splitlines() if ' primary ' in line)

            # Extract the resolution from the primary display line
            resolution = primary_display_line.split()[0]

            return resolution
        except Exception as e:
            print(f"Error: {e}")
            return None



    def angle_between(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        c = math.atan2((x2 - x1), (y2 - y1))
        d = math.degrees(c)
        if d < 0:
            d = d + 360
        return d

    def get_object_id_from_parcel_no(self, parcel_no, rec_dict):
        return_id = 1
        for record in rec_dict.values():
            if record.record[2] == parcel_no:
                return_id = record.record[0]
        return return_id

    

    def delete_list_boxes(self):
        self.show_box_list = list()
        self.scroll_bar_list = list()
        for lists in self.show_box_list:
            lists.pack_forget()
        for sbar in self.scroll_bar_list:
            sbar.pack_forget()

    def get_ewns_parcel(self):
        east = []
        west = []
        north = []
        south = []

        self.delete_list_boxes()

        sbar1 = Scrollbar(self.right_frame)
        sbar2 = Scrollbar(self.right_frame)
        sbar3 = Scrollbar(self.right_frame)
        sbar4 = Scrollbar(self.right_frame)

        listbox1 = Listbox(master=self.right_frame, yscrollcommand=sbar1.set)
        listbox2 = Listbox(master=self.right_frame, yscrollcommand=sbar2.set)
        listbox3 = Listbox(master=self.right_frame, yscrollcommand=sbar3.set)
        listbox4 = Listbox(master=self.right_frame, yscrollcommand=sbar4.set)

        self.show_box_list.append(listbox1)
        self.show_box_list.append(listbox2)
        self.show_box_list.append(listbox3)
        self.show_box_list.append(listbox4)

        self.scroll_bar_list.append(sbar1)
        self.scroll_bar_list.append(sbar2)
        self.scroll_bar_list.append(sbar3)
        self.scroll_bar_list.append(sbar4)

        dk = list(self.centroid_dict.keys())
        # print(self.centroid_dict.keys())
        # print(dk)
        dv = list(self.centroid_dict.values())
        input_parcel = int(self.parcelNumber)

        for i in dv:
            origin_parcel_centroid = self.centroid_dict[input_parcel]
            angle = self.angle_between(origin_parcel_centroid, i)
            if self.centroid_dict[input_parcel] == i:
                pass
            elif (angle >= 45 and angle < 135):
                east.append(dk[dv.index(i)])
            elif (angle >= 135 and angle < 215):
                south.append(dk[dv.index(i)])
            elif (angle >= 215 and angle < 315):
                west.append(dk[dv.index(i)])
            else:
                north.append(dk[dv.index(i)])

        listbox1.insert(END, "East")
        listbox1.insert(END, " ")
        for i in east:
            listbox1.insert(END, str(i))

        listbox2.insert(END, "West")
        listbox2.insert(END, " ")
        for i in west:
            listbox2.insert(END, str(i))

        listbox3.insert(END, "North")
        listbox3.insert(END, " ")
        for i in north:
            listbox3.insert(END, str(i))

        listbox4.insert(END, "South")
        listbox4.insert(END, " ")
        for i in south:
            listbox4.insert(END, str(i))

        listbox1.pack(side=LEFT, fill=BOTH)
        sbar1.pack(side=LEFT, fill=Y)
        listbox2.pack(side=LEFT, fill=BOTH)
        sbar2.pack(side=LEFT, fill=Y)
        listbox3.pack(side=LEFT, fill=BOTH)
        sbar3.pack(side=LEFT, fill=Y)
        listbox4.pack(side=LEFT, fill=BOTH)
        sbar4.pack(side=LEFT, fill=Y)

        sbar1.config(command=listbox1.yview)
        sbar2.config(command=listbox2.yview)
        sbar3.config(command=listbox3.yview)
        sbar4.config(command=listbox4.yview)

    
    def update_zoom(self, val):
                        
            x_min = min(centroid[0] for centroid in self.centroid_dict.values())
            x_max = max(centroid[0] for centroid in self.centroid_dict.values())
            y_min = min(centroid[1] for centroid in self.centroid_dict.values())
            y_max = max(centroid[1] for centroid in self.centroid_dict.values())

            zoom_factor = 1/val  
            self.ax.set_xlim((x_min + x_max) / 2 - zoom_factor * (x_max - x_min) / 2,
                        (x_min + x_max) / 2 + zoom_factor * (x_max - x_min) / 2)
            self.ax.set_ylim((y_min + y_max) / 2 - zoom_factor * (y_max - y_min) / 2,
                        (y_min + y_max) / 2 + zoom_factor * (y_max - y_min) / 2)
            self.toolbar.update()
            self.fig.canvas.draw_idle()

    def show_result(self):
        try:
            file_path = self.shpFile
            sf = shapefile.Reader(file_path)
        except shapefile.ShapefileException as e:
            messagebox.showerror("Error", str(e))
            return

        input_parcel = self.parcelNumber
        

        self.delete_list_boxes()

        self.centroid_dict = dict()
        self.canvas_id = 0


        record_dict = dict()
        parcel_plot = dict()
        input_test_list = list()
        for rec in sf.shapeRecords():
            input_test_list.append(rec.record[2])

        if input_parcel not in input_test_list:
            messagebox.showinfo("Error", "Invalid Parcel Number")

        for rec in sf.shapeRecords():
            record_dict[rec.record[0]] = rec

        # print("get_object_id_from_parcel_no: ", input_parcel, record_dict )
        k = self.get_object_id_from_parcel_no(input_parcel, record_dict)


        my_record = record_dict[k]
        parcel_plot[k] = my_record.shape.points

        objects_touching_this = []  # list of object ids

        for other_key in list(record_dict.keys()):
            if other_key == k:
                continue

            other_rec = record_dict[other_key]

            my_shape = shape(my_record.shape.__geo_interface__)
            other_shape = shape(other_rec.shape.__geo_interface__)
            if my_shape.intersects(other_shape):
                parcel_plot[other_key] = other_rec.shape.points
                objects_touching_this.append(other_rec.record[2])

        coord_collection = {}
        points_collection = []
        for obj in parcel_plot.keys():
            for rec in record_dict.keys():
                if obj == rec:
                    required_record = record_dict[obj]
                    req_rec_parcel = record_dict[obj].record[2]
                    coord_collection[req_rec_parcel] = polygon.Polygon(required_record.shape.points)
                    points_collection.append(required_record.shape.points)

        boundary = gpd.GeoSeries(coord_collection)

        # Create a new figure with subplot
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        plt.ylabel("Northing", fontsize=14)
        plt.xlabel("Easting", fontsize=14)

        for each_shape in points_collection:
            x_s = [tup[0] for tup in each_shape]
            y_s = [tup[1] for tup in each_shape]
            self.ax.plot(x_s, y_s)

        for i, geo in boundary.centroid.items():
            self.ax.annotate(xy=(geo.x, geo.y), color="black", text=str(i))
            self.centroid_dict[i] = (geo.x, geo.y)

        x_min = min(centroid[0] for centroid in self.centroid_dict.values())
        x_max = max(centroid[0] for centroid in self.centroid_dict.values())
        y_min = min(centroid[1] for centroid in self.centroid_dict.values())
        y_max = max(centroid[1] for centroid in self.centroid_dict.values())

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        self.zoom_slider_ax = plt.axes([0.15, 0.01, 0.7, 0.03], facecolor='lightgoldenrodyellow')
        self.zoom_slider = Slider(self.zoom_slider_ax, 'Zoom', 0.1, 5)

        

        # Attach the update function to the slider
        self.zoom_slider.on_changed(self.update_zoom)
        canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(canvas, self.right_frame)
        self.toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def on_hover(event):
        event.widget.config(style="Hover.TButton")

    def on_leave(event):
        event.widget.config(style="TButton")

    def set_select_file():
        filename = askopenfilename()
        e1.insert(0, filename)

    def on_hover(event):
        event.widget.config(style="Hover.TButton")

    def on_leave(event):
        event.widget.config(style="TButton")


if __name__ == "__main__":
    app = App()
    app.mainloop()
