import cv2
from matplotlib import pyplot as pltt
import numpy as np
from imutils import perspective

def capture_image(src, res = 480, debug = True):
    # Capture Image
    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
    if res == 1080:
        ret = cap.set(3, 1920)
        ret = cap.set(4, 1080)
    elif res == 480:
        ret = cap.set(3, 640)
        ret = cap.set(4, 480)
    width = cap.get(3)
    height = cap.get(4)
    print(f'{width} x {height}')
    frame = grab_frame(cap)
    if debug:
        show_image(frame)
        cv2.waitKey(0)
    cap.release()
    return frame

def midpoint(ptA, ptB):
    return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5


def find_center(tl, w, h):
    return int((2*tl[0]+w)/2), int((2*tl[1]+h)/2)


def binary_search(item_list, item):
    first = 0
    last = len(item_list) - 2
    while first <= last:
        mid = (first + last) // 2
        # if(mid == len(item_list)-1):
        #     return 99
        if item_list[mid] < item < item_list[mid + 1]:
            return mid
        else:
            if item < item_list[mid]:
                last = mid - 1
            else:
                first = mid + 1
    return 99


def grab_frame(cap):
    ret, frame = cap.read()
    return frame


def show_image(frame):
    pltt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    pltt.show()


def draw_zone(frame, zones):
    grid_size = len(zones) - 1
    for row in range(grid_size):
        for col in range(grid_size):
            zones[row][col].display(frame)

def find_zone(zones, c):
    cx = c[0]
    cy = c[1]
    ran = []
    for col in range(len(zones)):
        ran = ran + [zones[0][col].start[0]]
    midx = binary_search(ran, cx)
    ran = []
    for row in range(len(zones)):
        if ran is None:
            ran = []
        # print(zones[j]['start'])
        ran = ran + [zones[row][0].start[1]]
    midy = binary_search(ran, cy)
    return midx, midy


def display_zone(frame, zone, res = 480):
    x = zone[0]
    y = zone[1]
    if res == 1080:
        cv2.rectangle(frame, (0, 0), (350, 200), (0, 0, 0), -1)
        cv2.putText(frame, f'zone{y, x}',
                    (100, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 255, 255), 5)
    elif res == 480:
        cv2.rectangle(frame, (0, 0), (250, 60), (0, 0, 0), -1)
        cv2.putText(frame, f'zone{y, x}',
                    (40, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)


def create_zone(grid_size, ZONE_PITCH, pixelsPerMetric, Start):
    grid_size = grid_size + 1
    tmp = np.zeros((grid_size, grid_size), dtype=object)
    for row in range(grid_size):
        for col in range(grid_size):
            pStart = (int(Start[0] + col * ZONE_PITCH * pixelsPerMetric), int(Start[1] + row * ZONE_PITCH * pixelsPerMetric))
            tmp[row][col] = zone(pStart, ZONE_PITCH*pixelsPerMetric)
    return tmp


class zone:
    def __init__(self, start, pitch):
        self.start = start
        self.center = None
        self.ZONE_PITCH = pitch
        self.wall = 0

    def get_center(self):
        self.center = (int((2*self.start[0] + self.ZONE_PITCH) / 2), int((2*self.start[1] + self.ZONE_PITCH) / 2))

    def display(self, frame):
        green = (0, 255, 0)
        red = (0, 0, 255)
        white = (255, 255, 255)
        self.get_center()
        cv2.circle(frame, self.center, 2, white, -1)
        if self.wall == 0:
            cv2.rectangle(frame, (self.start[0], self.start[1]),
                          (int(self.start[0] + self.ZONE_PITCH), int(self.start[1] + self.ZONE_PITCH)), green, 2)
        elif self.wall ==1:
            # roi = img1[self.start[0]:int(self.start[0] + self.ZONE_PITCH), self.start[1]:int(self.start[1] + self.ZONE_PITCH)]
            # cv2.rectangle(frame, (self.start[0], self.start[1]),
            #               (int(self.start[0] + self.ZONE_PITCH), int(self.start[1] + self.ZONE_PITCH)), red, -1)
            cv2.rectangle(frame, (self.start[0], self.start[1]),
                          (int(self.start[0] + self.ZONE_PITCH), int(self.start[1] + self.ZONE_PITCH)), red, 3)


class Box:
    def __init__(self, x, y, w, h, index=0):
        self.name = "object" + str(index)
        self.tl = (x, y)
        self.tr = (x + w, y)
        self.bl = (x, y + h)
        self.br = (x+w, y+h)
        self.center = int((2 * x + w) / 2), int((2 * y + h) / 2)
        self.vertices = []

    def display(self, frame):
        cv2.rectangle(frame, self.tl, self.br,
                      (0, 255, 0), 2)
        cv2.putText(frame, self.name, (self.tl[0], self.tl[1]-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.circle(frame, self.center, 5, (0, 0, 255), -1)

    def find_vertices(self, frame, zones):
        pos = ["tl", "tr", "bl", "br"]
        for p in pos:
            point = getattr(self, p)
            cv2.circle(frame, point, 4, (0, 0, 0), -1)
            v = find_zone(zones, point)
            self.vertices.append(v)
        print(self.vertices)

    def gen_wall(self, zones):
        tl = self.vertices[0]
        br = self.vertices[3]
        if 99 in tl or 99 in br:
            return False
        for j in range(tl[1], br[1] + 1):
            for i in range(tl[0], br[0] + 1):
                zones[j][i].wall = 1
        return True









