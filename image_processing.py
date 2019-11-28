import cv2
from imutils import contours
import imutils
import numpy as np
from util import midpoint, draw_zone, display_zone, find_zone
from imutils import perspective
from show_plot import show_imageplot


def detect_contour(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    cx = None
    cy = None
    ran = None

    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    return cnts


def detect_object(zones, cnts, orig, SHAPE_THRESHOLD=500, AREA_THRESHOLD=2500, RESOLUTION=480):
    i = 0
    found = False
    track_box = None
    bboxes = []
    cx = None
    cy = None
    ran = None
    for c in cnts:
        # check contour area
        print(f'area:{cv2.contourArea(c)}, shape:{c.shape[0]}')
        if c.shape[0] > SHAPE_THRESHOLD:
            continue
        if cv2.contourArea(c) < AREA_THRESHOLD:
            continue
        found = True

        # compute the rotated bounding box of the contour
        box = cv2.minAreaRect(c)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        b1x = box[0][0].astype("int") - 5
        b1y = box[0][1].astype("int") - 5
        b2x = box[2][0].astype("int") + 5
        b2y = box[2][1].astype("int") + 5
        track_box = (b1x, b1y, b2x-b1x, b2y-b1y)
        print(track_box)
        bboxes = bboxes + [track_box]

        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 255), 2)


        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)

        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                 (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                 (255, 0, 255), 2)
        #label names
        cv2.putText(orig, f'obj{i}', (int(tl[0]), int(tl[1])-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        M = cv2.moments(c)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

        cv2.circle(orig, (cx, cy), 10, (0, 0, 255), -1)
        draw_zone(orig, zones)

        zx, zy = find_zone(zones,(cx,cy))
        display_zone(orig, (zx, zy), RESOLUTION)

        i += 1
        print(f'number of contours found is {i}')

    show_imageplot(orig)
    return found, bboxes

