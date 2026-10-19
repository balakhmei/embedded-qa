from pathlib import Path
import argparse
import cv2
from picamera2 import Picamera2
from time import sleep

ROI = (555, 315, 595, 355)  # x1, y1, x2, y2


def detect_color(image):
    x1, y1, x2, y2 = ROI
    roi = image[y1:y2, x1:x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)

    valid = (s > 100) & (v > 150)

    red = int((valid & ((h <= 39) | (h >= 170))).sum())
    green = int((valid & (h >= 60) & (h <= 99)).sum())

    if red > green and red >= 20:
        color = "RED"
    elif green > red and green >= 20:
        color = "GREEN"
    else:
        color = "UNKNOWN"

    return color, red, green


def capture_image():
    camera = Picamera2()
    camera.configure(
        camera.create_still_configuration(
            main={"size": (1280, 720)}
        )
    )
    camera.set_controls({
        "ExposureTime": 1000,
        "AnalogueGain": 1.0,
    })

    try:
        camera.start()
        sleep(2)
        return camera.capture_array()
    finally:
        camera.stop()
        camera.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="Existing image path")
    parser.add_argument("--save", help="Save captured image to path")
    args = parser.parse_args()

    if args.image:
        image = cv2.imread(args.image)
        if image is None:
            parser.error("Cannot read image")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image = capture_image()

    if args.save:
        output = Path(args.save).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output), cv2.cvtColor(image, cv2.COLOR_RGB2BGR)):
            raise RuntimeError(f"Failed to save image: {output}")
        print(f"IMAGE_SAVED={output}")

    color, red, green = detect_color(image)
    print(f"LED_COLOR={color} RED_PIXELS={red} GREEN_PIXELS={green}")
