import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
from util import *
from calibrate_pic import calibrate
from image_processing import detect_contour, detect_object
from show_plot import show_imageplot
from imutils.video import FPS
from video_window import PhotoBoothApp
from imutils.video import VideoStream
import time
from test4 import radio_button
from path import Search_path
from server import socket_comm


class App:
    def __init__(self, window, window_title):
        image_path1 = "yumi.jpg"
        image_path2 = "ABB.jpg"
        self.WIDTH = 25
        self.ZONE_PITCH = 30
        self.AREA_THRESHOLD = 750
        self.SHAPE_THRESHOLD = 500

        self.TRACKER = "csrt"
        self.RESOLUTION = 480
        self.GRID_SIZE = 8
        self.start_pos = None
        self.track_box = None
        self.bboxes = None
        self.zones = None
        self.start = (0, 0)
        self.end = (4, 4)
        self.pixelsPerMetric = 1.67619
        self.HOST = '192.168.125.201'  # Standard loopback interface address (localhost)
        self.PORT = 1025  # Port to listen on (non-privileged ports are > 1023)
        self.multiTracker = None
        self.pba = None

        self.window = window
        self.window.configure(background='white')
        self.window.title(window_title)
        self.message_count = 0
        self.setuplabel = tk.Label(self.window, text='Setup', font='TkDefaultFont 15 bold', bg='white',  fg="red")
        self.programlabel = tk.Label(self.window, text='Program', font='TkDefaultFont 15 bold', bg='white', fg="red")
        self.consolelabel = tk.Label(self.window, text='Console', font='TkDefaultFont 15 bold', width=30, bg='white',  fg="red")
        self.btn_calibrate = tk.Button(self.window, text="Calibrate", width=50, command=self.calibrate, bg='white')
        self.btn_select = tk.Button(self.window, text="Select Area", width=50, command=self.select_area, bg='white')
        self.btn_start = tk.Button(self.window, text="Detect object", width=50, command=self.detect, bg='white')
        self.console = []
        self.message = []

        self.message.append("")
        self.btn_start_track = tk.Button(self.window, text="Start Tracking", width=50, command=self.start_tracking, bg='white')
        self.cv_img1 = cv2.cvtColor(cv2.imread(image_path1), cv2.COLOR_BGR2RGB)
        self.height, self.width, no_channels = self.cv_img1.shape
        self.canvas1 = tk.Canvas(window, width = self.width, height = self.height)
        self.cv_img2 = cv2.cvtColor(cv2.imread(image_path2), cv2.COLOR_BGR2RGB)
        self.height, self.width, no_channels = self.cv_img2.shape
        self.canvas2 = tk.Canvas(window, width = self.width, height = self.height)

        self.consolelabel.grid(column = 1, row=0)
        self.setuplabel.grid(row=0)
        self.btn_calibrate.grid(row=1)
        self.btn_select.grid(row=2)
        self.btn_start.grid(row=3)
        self.programlabel.grid(row=4)
        self.btn_start_track.grid(row=5)
        self.canvas1.grid(row =6)
        self.canvas2.grid(column =1, row=6)

        self.photo1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img1))
        self.canvas1.create_image(0, 0, image=self.photo1, anchor=tk.NW)
        self.photo2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img2))
        self.canvas2.create_image(0, 0, image=self.photo2, anchor=tk.NW)
        self.window.mainloop()

    def log(self, message):
        message_count = self.message_count
        print(message_count)
        self.console.append(tk.Label(self.window, text=f'console:{message}', width=50, bg='white'))
        self.console[self.message_count].grid(column=1, row=self.message_count+1, sticky='w')
        self.message_count += 1

    def calibrate(self):
        self.log("Calibration Started")
        frame = capture_image(1, debug=False)
        ret, px, status=calibrate(frame)
        self.log(status)
        self.pixelsPerMetric = px if ret else self.pixelsPerMetric
        self.log(f'px/mm:{self.pixelsPerMetric}')

    def select_area(self):
        frame = capture_image(1, debug=False)
        cv2.namedWindow('select')
        cv2.setMouseCallback('select', self.click_pos, frame)
        while True:
            cv2.imshow('select', frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()

    def click_pos(self, event, x, y, flags, frame):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
            self.start_pos = (x, y)
            print(self.start_pos)
            self.zones = create_zone(self.GRID_SIZE, self.ZONE_PITCH, self.pixelsPerMetric, self.start_pos)
            draw_zone(frame, self.zones)
            self.log(f'Starrting grid at pixels{self.start_pos}')

    def start_tracking(self):
        vs = None
        self.window.destroy()
        self.pba = PhotoBoothApp(self.bboxes, self.zones)
        self.pba.btn_find_path = tk.Button(self.pba.root, text="Find Path")
        self.pba.btn_find_path.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)
        self.pba.btn_find_path.bind("<Button-1>", self.close)
        self.pba.root.mainloop()

    def close(self, event):
        print(self.pba.track_objects)
        self.pba.stopEvent.set()
        self.pba.vs.stop()
        self.pba.root.destroy()
        time.sleep(3)
        self.rad = radio_button(self.GRID_SIZE)
        self.rad.btn_send.bind("<Button-1>", self.closet)
        self.rad.root.mainloop()

    def closet(self, event):
        self.rad.root.destroy()
        # for r in self.rad.radio_group:
        #     print(r.selection)
        self.start = int(self.rad.radio_group[0].selection), int(self.rad.radio_group[1].selection)
        self.end = int(self.rad.radio_group[2].selection), int(self.rad.radio_group[3].selection)
        print(self.start)
        print(self.end)
        path_finder = Search_path(self.start, self.end, self.GRID_SIZE, self.GRID_SIZE)
        path_finder.setup_grid()
        track_objects = self.pba.track_objects
        for obj in track_objects:
            tl = obj.vertices[0]
            br = obj.vertices[3]
            path_finder.gen_wall((tl[1], tl[0]), (br[1], br[0]))
        path_finder.display_plot()
        path = path_finder.astar()
        print(path)
        path_finder.display_plot(path)
        comm = socket_comm(self.HOST, self.PORT)
        comm.send_path(path)


    def detect(self):
        frame = capture_image(1, debug=False)
        frame1 = frame.copy()
        contours = detect_contour(frame)
        cv2.drawContours(frame1, contours, -1, (0, 0, 255), 3)
        show_imageplot(frame1)
        attempt = 0
        while True:
            done, bboxes = detect_object(self.zones, contours, frame1,
                    SHAPE_THRESHOLD=self.SHAPE_THRESHOLD, AREA_THRESHOLD=self.AREA_THRESHOLD)
            break
        print(bboxes)
        self.bboxes = bboxes
        self.log(f'{len(bboxes)} object found')
        self.log(f'Bounding boxes at {bboxes}')


app = App(tk.Tk(), "Tkinter and OpenCV")

