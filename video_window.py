from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import imutils
import cv2
import time
from imutils.video import VideoStream
from util import Box, draw_zone
from imutils.video import FPS
import os


class PhotoBoothApp:
	def __init__(self, bboxes, zones, vs=None):
		# store the video stream object and output path, then initialize
		# the most recently read frame, thread for reading frames, and
		# the thread stop event
		# self.vs = vs
		self.zones = zones
		self.vs = VideoStream(src=1, resolution=(640,480), framerate=60).start()
		time.sleep(2)
		self.frame = None
		self.thread = None
		self.stopEvent = None
		self.initBB = None
		self.multiTracker = cv2.MultiTracker_create()
		self.bboxes = bboxes
		# initialize the root window and image panel
		self.root = tki.Tk()
		self.panel = None
		self.fps = FPS().start()
		self.tracker = 'csrt'
		self.track_objects = []


		# create a button, that when pressed, will take the current
		# frame and save it to file
		btn = tki.Button(self.root, text="Start Tracking",
			command=self.takeSnapshot)
		btn.pack(side="bottom", fill="both", expand="yes", padx=10,
			pady=10)

		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PyImageSearch PhotoBooth")
		# self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		# self.root.wm_protocol("WM_DELETE_WINDOW", self.closemessage)
		time.sleep(1)

	def closemessage(self):
		print("why did you close me")

	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():
				# grab the frame from the video stream and resize it to
				# have a maximum width of 300 pixels
				self.frame = self.vs.read()
				(H, W) = self.frame.shape[:2]
				self.fps.update()
				# self.frame = imutils.resize(self.frame, width=300)
				self.frame = imutils.resize(self.frame)
				if self.bboxes is not None:
					# get updated location of objects in subsequent frames
					success, boxes = self.multiTracker.update(self.frame)
					# if success:
					# 	for box in boxes:
					# 		(x, y, w, h) = [int(v) for v in box]
					# 		cv2.rectangle(self.frame, (x, y), (x + w, y + h),
					# 					  (0, 255, 0), 2)
					if success:
						for i, box in enumerate(boxes):
							obj = Box(*(int(v) for v in box), i)
							obj.display(self.frame)
							obj.find_vertices(self.frame, self.zones)
							ret = obj.gen_wall(self.zones)
							if ret:
								self.track_objects.append(obj)
					self.fps.stop()
					info = [
						("Tracker", self.tracker),
						("Success", "Yes" if success else "No"),
						# ("FPS", "{:.2f}".format(self.fps.fps())),
						("FPS", "0")
					]

					# loop over the info tuples and draw them on our frame
					for (i, (k, v)) in enumerate(info):
						text = "{}: {}".format(k, v)
						cv2.putText(self.frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

				# OpenCV represents images in BGR order; however PIL
				# represents images in RGB order, so we need to swap
				# the channels, then convert to PIL and ImageTk format
				draw_zone(self.frame, self.zones)
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)
		
				# if the panel is not None, we need to initialize it
				if self.panel is None:
					self.panel = tki.Label(image=image)
					self.panel.image = image
					self.panel.pack(side="left", padx=10, pady=10)
		
				# otherwise, simply update the panel
				else:
					self.panel.configure(image=image)
					self.panel.image = image
		except RuntimeError:
			print("caught a RuntimeError")

	def takeSnapshot(self):
		del self.multiTracker
		self.multiTracker = cv2.MultiTracker_create()
		for bbox in self.bboxes:
			self.multiTracker.add(self.init_tracker(self.tracker), self.frame, bbox)
		# fps = FPS().start()
		# cv2.destroyAllWindows()

	def init_tracker(self, tracker_model):
		if tracker_model == 'csrt':
			print('CSRT selected')
			return cv2.TrackerCSRT_create()
		elif tracker_model == 'kcf':
			return cv2.TrackerKCF_create()
		elif tracker_model == 'boosting':
			return cv2.TrackerBoosting_create()
		elif tracker_model == 'mil':
			return cv2.TrackerMIL_create()
		elif tracker_model == 'tld':
			return cv2.TrackerTLD_create()
		elif tracker_model == 'medianflow':
			return cv2.TrackerMedianFlow_create()
		elif tracker_model == 'mosse':
			return cv2.TrackerMOSSE_create()