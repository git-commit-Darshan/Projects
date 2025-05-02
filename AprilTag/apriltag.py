from pupil_apriltags import Detector
import cv2
import numpy as np

tag_family = 'tag36h11'
tag_id = 1

detector = Detector(families=tag_family)

tag_size = 200

image = np.zeros((tag_size, tag_size), dtype=np.uint8)

cv2.putText(image, f'Tag ID: {tag_id}', (10, tag_size - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255), 1)

filename = f"apriltag_{tag_family}_{tag_id}.png"

cv2.imwrite(filename, image)

print(f"Apriltag saved as {filename}")
