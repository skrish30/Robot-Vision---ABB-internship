import numpy as np
import cv2
from matplotlib import pyplot as plt
from scipy.spatial import distance as dist
from show_plot import show_imageplot

GRID_SIZE = 25

def calibrate(frame):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((6*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
    # print(objp)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    img = frame
    cv2.waitKey(0)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)
        imgpoints = imgpoints[0]
        i = 0
        j = 8
        a= (imgpoints[i][0][0], imgpoints[i][0][1])
        b = (imgpoints[j][0][0], imgpoints[j][0][1])
        distance = dist.euclidean(a, b)
        pxPerMetric = distance/ (8 * GRID_SIZE)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (9,6), corners2,ret)
        show_imageplot(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        status = "calibration success"
        print(status)
        return ret, pxPerMetric, status
    else:
        status = "calibration failed"
        print(status)
        return ret, None, status

    cv2.destroyAllWindows()

