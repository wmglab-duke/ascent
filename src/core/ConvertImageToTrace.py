import cv2

# Author: Eric Musselman
# Date: July 22, 2019
# General Purpose: Load binary image and output white (ROI such as endoneurium, perineurium, nerve... )
# and black (other medium) boundaries

path = 'D:/Documents/SPARCpy/data/tracefile2.tif'
img = cv2.imread(path, -1)

cv2.utils.dumpInputArray(img)

cnts, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)