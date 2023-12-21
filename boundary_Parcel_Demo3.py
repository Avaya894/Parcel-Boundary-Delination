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

def set_select_file():
    filename = askopenfilename()
    e1.insert(0, filename)

def angle_between(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    c = math.atan2((x2 - x1), (y2 - y1))
    d = math.degrees(c)
    if d < 0:
        d = d + 360
    return d

def get_object_id_from_parcel_no(parcel_no, rec_dict):
    return_id = 1
    for record in rec_dict.values():
        if record.record[2] == parcel_no:
            return_id = record.record[0]
    return return_id

show_box_list = list()
scroll_bar_list = list()

def delete_list_boxes():
    for lists in show_box_list:
        lists.pack_forget()
    for sbar in scroll_bar_list:
        sbar.pack_forget()

def get_ewns_parcel():
    east = []
    west = []
    north = []
    south = []

    delete_list_boxes()

    sbar1 = Scrollbar(right_frame)
    sbar2 = Scrollbar(right_frame)
    sbar3 = Scrollbar(right_frame)
    sbar4 = Scrollbar(right_frame)

    listbox1 = Listbox(master=right_frame, yscrollcommand=sbar1.set)
    listbox2 = Listbox(master=right_frame, yscrollcommand=sbar2.set)
    listbox3 = Listbox(master=right_frame, yscrollcommand=sbar3.set)
    listbox4 = Listbox(master=right_frame, yscrollcommand=sbar4.set)

    show_box_list.append(listbox1)
    show_box_list.append(listbox2)
    show_box_list.append(listbox3)
    show_box_list.append(listbox4)

    scroll_bar_list.append(sbar1)
    scroll_bar_list.append(sbar2)
    scroll_bar_list.append(sbar3)
    scroll_bar_list.append(sbar4)

    dk = list(centroid_dict.keys())
    print(centroid_dict.keys())
    print(dk)
    dv = list(centroid_dict.values())
    input_parcel = int(e2.get())

    for i in dv:
        origin_parcel_centroid = centroid_dict[input_parcel]
        angle = angle_between(origin_parcel_centroid, i)
        if centroid_dict[input_parcel] == i:
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

centroid_dict = dict()
canvas_id = 0

def show_result():
    try:
        file_path = e1.get()
        sf = shapefile.Reader(file_path)
    except shapefile.ShapefileException as e:
        messagebox.showerror("Error", str(e))
        return

    input_parcel = int(e2.get())
    global centroid_dict

    delete_list_boxes()
    record_dict = dict()
    parcel_plot = dict()
    input_test_list = list()
    for rec in sf.shapeRecords():
        input_test_list.append(rec.record[2])

    if input_parcel not in input_test_list:
        messagebox.showinfo("Error", "Invalid Parcel Number")

    for rec in sf.shapeRecords():
        record_dict[rec.record[0]] = rec

    k = get_object_id_from_parcel_no(input_parcel, record_dict)

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
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.ylabel("Northing", fontsize=14)
    plt.xlabel("Easting", fontsize=14)

    for each_shape in points_collection:
        x_s = [tup[0] for tup in each_shape]
        y_s = [tup[1] for tup in each_shape]
        ax.plot(x_s, y_s)

    for i, geo in boundary.centroid.items():
        ax.annotate(xy=(geo.x, geo.y), color="black", text=str(i))
        centroid_dict[i] = (geo.x, geo.y)

    x_min = min(centroid[0] for centroid in centroid_dict.values())
    x_max = max(centroid[0] for centroid in centroid_dict.values())
    y_min = min(centroid[1] for centroid in centroid_dict.values())
    y_max = max(centroid[1] for centroid in centroid_dict.values())

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    zoom_slider_ax = plt.axes([0.15, 0.01, 0.7, 0.03], facecolor='lightgoldenrodyellow')
    zoom_slider = Slider(zoom_slider_ax, 'Zoom', 0.1, 5)

    def update_zoom(val):
        
        zoom_factor = 1/val  
        ax.set_xlim((x_min + x_max) / 2 - zoom_factor * (x_max - x_min) / 2,
                    (x_min + x_max) / 2 + zoom_factor * (x_max - x_min) / 2)
        ax.set_ylim((y_min + y_max) / 2 - zoom_factor * (y_max - y_min) / 2,
                    (y_min + y_max) / 2 + zoom_factor * (y_max - y_min) / 2)
        toolbar.update()
        fig.canvas.draw_idle()

    # Attach the update function to the slider
    zoom_slider.on_changed(update_zoom)
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, right_frame)
    toolbar.update()
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

right_frame = Frame(root, width=750, height=500, bg='#ecf0f1')  # Background color changed to a light gray shade
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
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{1100}x{580}")

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
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Browse File")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.open_input_dialog_event, text="Enter Parcel Number")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Show Parcel")
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

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        # self.tabview = customtkinter.CTkTabview(self, width=250)
        # self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.tabview.add("CTkTabview")
        # self.tabview.add("Tab 2")
        # self.tabview.add("Tab 3")
        # self.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        # self.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)

        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("CTkTabview"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        # self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("CTkTabview"),
        #                                             values=["Value 1", "Value 2", "Value Long....."])
        # self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        # self.string_input_button = customtkinter.CTkButton(self.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
        #                                                    command=self.open_input_dialog_event)
        # self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        # self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
        # self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # create radiobutton frame
        # self.radiobutton_frame = customtkinter.CTkFrame(self)
        # self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.radio_var = tkinter.IntVar(value=0)
        # self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="CTkRadioButton Group:")
        # self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        # self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0)
        # self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        # self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1)
        # self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        # self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        # self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # create slider and progressbar frame
        # self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        # self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        # self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        # self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        # self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        # self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        # self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        # self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        # self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        # self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="CTkScrollableFrame")
        # self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # self.scrollable_frame_switches = []
        # for i in range(100):
        #     switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
        #     switch.grid(row=i, column=0, padx=10, pady=(0, 20))
        #     self.scrollable_frame_switches.append(switch)

        # # create checkbox and switch frame
        # self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        # self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_3 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

        # set default values
        # self.checkbox_3.configure(state="disabled")
        # self.checkbox_1.select()
        # self.scrollable_frame_switches[0].select()
        # self.scrollable_frame_switches[4].select()
        # self.radio_button_3.configure(state="disabled")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        # self.optionmenu_1.set("CTkOptionmenu")
        # self.combobox_1.set("CTkComboBox")
        # self.slider_1.configure(command=self.progressbar_2.set)
        # self.slider_2.configure(command=self.progressbar_3.set)
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        # self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        # self.seg_button_1.set("Value 2")

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()
