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

root = Tk()
root.style = ttk.Style()


root.style.theme_use("clam")

width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.style.configure('TEntry', padding=(10, 5, 10, 5), font=('Arial', 12))
root.style.configure('TButton', padding=(10, 5, 10, 5), font=('Arial', 12))

root.style.map('Hover.TButton',
          foreground=[('active', 'red')],
          background=[('active', 'green')])

W = str(width)
H = str(height)
root.configure(width=W, height=H, bg="red")
root.title("Boundary Parcel Delination")
v = StringVar()
left_frame = Frame(root, width=400, height=1000, bg='green')
left_frame.grid(row=0, column=0, padx=10, pady=5)
right_frame = Frame(root, width=750, height=500, bg='lightgrey')
right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew", )

fig = Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=right_frame)

tool_bar = Frame(left_frame, width=180, height=185)
toolbar = Frame(left_frame, width=180, height=185)
tool_bar.grid(row=2, column=0, padx=5, pady=5)
toolbar.grid(row=10, column=0, padx=5, pady=20)

label_filename = ttk.Label(tool_bar, text="     Select shape file(.shp)")
label_filename.grid(row=0, column=0, padx=5, pady=3, ipadx=10)
e1 = ttk.Entry(tool_bar, textvariable=v)
e1.grid(row=1, column=0)

button_browse = ttk.Button(tool_bar, text="Open", command=set_select_file)
button_browse.grid(row=2, column=0, padx=5, pady=5)
button_browse.bind("<Enter>", on_hover)
button_browse.bind("<Leave>", on_leave)

label_parcel_number = ttk.Label(tool_bar, text="     Parcel Number ")
label_parcel_number.grid(row=3, column=0, padx=5, pady=3, ipadx=10)
e2 = ttk.Entry(tool_bar)
e2.grid(row=4, column=0)

button_show = ttk.Button(tool_bar, text="Show", command=show_result, style='TButton')
button_show.grid(row=5, column=0, pady=4, ipadx=10)
button_show.bind("<Enter>", on_hover)
button_show.bind("<Leave>", on_leave)

button_quit = ttk.Button(tool_bar, text="Quit", command=root.quit)
button_quit.grid(row=6, column=0, pady=4, ipadx=10)
button_quit.bind("<Enter>", on_hover)
button_quit.bind("<Leave>", on_leave)

button_display_parcel = ttk.Button(toolbar, text="Show Parcel Direction", command=get_ewns_parcel)
button_display_parcel.grid(row=6, column=0, pady=4, ipadx=10)
button_display_parcel.bind("<Enter>", on_hover)
button_display_parcel.bind("<Leave>", on_leave)

label_output = ttk.Label(toolbar, text="Output")
label_output.grid(row=0, column=0, padx=5, pady=5)

root.mainloop()