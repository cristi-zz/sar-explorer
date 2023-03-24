import numpy as np
from pathlib import Path
import cv2

def readmultipage():
    """
    Play with openCV and multipage tiff

    :return:
    """
    base_path = Path("../data/")
    some_image_hardcoded = base_path / "sar-data/tasks/Panama Canal, Panama/4ced9d34-b5da-490b-a564-7454e7d86b71/2023-02-20-14-43-17_UMBRA-05/2023-02-20-14-43-17_UMBRA-05_GEC.tif"

    ok, planes = cv2.imreadmulti(str(some_image_hardcoded))
    assert ok
    print(f"Read {len(planes)} image planes")

    for k in range(len(planes)):
        win_name = f"plane_{k}"
        image = planes[k]
        cv2.namedWindow(win_name, cv2.WINDOW_GUI_NORMAL)
        cv2.imshow(win_name, image)
        print(f"Shown plane {k} with size {image.shape}")

    cv2.waitKey()

if __name__ == "__main__":
    readmultipage()