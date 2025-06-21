"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
import time
import os

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

fps = 60
frame_height = 720
frame_width = 1280
webcam.set(cv2.CAP_PROP_FPS, fps)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width) #1280
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height) #720

# Before your loop, create a resizable window
cv2.namedWindow("Demo", cv2.WINDOW_NORMAL)

# Optionally, resize the window to fit your screen or set it to a specific size
# For Full HD, you can use 1920x1080, or choose a size that fits your screen
cv2.resizeWindow("Demo", 1920, 1080)

none_count = 0 
frame_count = 0
myFps = "0"
start_time = time.time()
calibration_time = time.time()

# Clear the file once at the beginning of the program
with open("pupil_coordinates.csv", "w") as f:
    pass  # Opening in 'w' mode and closing the file clears it.
with open("pupil_coordinates_relative_to_eye.csv", "w") as f:
    pass  # Opening in 'w' mode and closing the file clears it.
with open("pupil_coordinates_relative_to_face.csv", "w") as f:
    pass  # Opening in 'w' mode and closing the file clears it.
with open("pupil_coordinates_relative_to_lm27.csv", "w") as f:
    pass  # Opening in 'w' mode and closing the file clears it.

def pupil_position_relative_to_eye_bbox(gaze):
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    left_eye = gaze.eye_left
    right_eye = gaze.eye_right
    #breakpoint()

    left_pupil_x = left_pupil[0] - left_eye.origin[0] - 0.5 * left_eye.width
    left_pupil_y = left_pupil[1] - left_eye.origin[1] - 0.5 * left_eye.height
    right_pupil_x = right_pupil[0] - right_eye.origin[0] - 0.5 * right_eye.width
    right_pupil_y = right_pupil[1] - right_eye.origin[1] - 0.5 * right_eye.height

    return left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y

def pupil_position_relative_to_face_bbox(gaze):
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    face = gaze.face
    #breakpoint()

    left_pupil_x = left_pupil[0] - face.dcenter().x
    left_pupil_y = left_pupil[1] - face.dcenter().y
    right_pupil_x = right_pupil[0] - face.dcenter().x
    right_pupil_y = right_pupil[1] - face.dcenter().y

    return left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y

def pupil_position_relative_to_lm27(gaze, previous_positions):
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    lm27 = gaze.face_landmarks.part(27)

    left_pupil_x = left_pupil[0] - lm27.x
    left_pupil_y = left_pupil[1] - lm27.y
    right_pupil_x = right_pupil[0] - lm27.x
    right_pupil_y = right_pupil[1] - lm27.y

    previous_positions.append((left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y))
    if len(previous_positions) > 3:
        previous_positions.pop(0)

    mean_left_pupil_x = sum([pos[0] for pos in previous_positions]) / len(previous_positions)
    mean_left_pupil_y = sum([pos[1] for pos in previous_positions]) / len(previous_positions)
    mean_right_pupil_x = sum([pos[2] for pos in previous_positions]) / len(previous_positions)
    mean_right_pupil_y = sum([pos[3] for pos in previous_positions]) / len(previous_positions)

    return mean_left_pupil_x, mean_left_pupil_y, mean_right_pupil_x, mean_right_pupil_y

previous_positions = []

# Replace the webcam capture with video file capture
#video_file = "30fps_high_res.mp4"
#webcam = cv2.VideoCapture(video_file)

# Set the directory where your images are stored
image_directory = 'outs'
image_files = [img for img in os.listdir(image_directory) if img.endswith(".jpg")]

# Optionally, sort the files if they are named in a sequential order
image_files.sort()

for image_file in image_files:
    # We get a new frame from the video file
    #_, frame = webcam.read()

    image_path = os.path.join(image_directory, image_file)
    frame = cv2.imread(image_path)
    
    # Rest of the code remains the same
    #frame = cv2.flip(frame, 1)
    frame_count += 1

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""
    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    if left_pupil is None and right_pupil is None:
        none_count += 1

    elapsed_time = time.time() - start_time

    if elapsed_time >= 1:  # Check if 1 second has passed
        myFps = str(f"FPS: {frame_count / elapsed_time:.2f}")  # Print the FPS
        ratio = none_count / frame_count
        print(f"\rFPS: {myFps}, None/Frame Ratio: {ratio:.2f}, Image Size: {frame.shape}", end="")
        frame_count = 0  # Reset frame count
        none_count = 0
        start_time = time.time()  # Reset the start time

    #cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
    #cv2.putText(frame, myFps, (90, 130), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 200), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    if gaze.face is not None:
        x, y, w, h = (gaze.face.left(), gaze.face.top(), gaze.face.width(), gaze.face.height())
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        left_eye_x, left_eye_y, left_eye_w, left_eye_h = (gaze.eye_left.origin[0], gaze.eye_left.origin[1], gaze.eye_left.width, gaze.eye_left.height)
        #cv2.rectangle(frame, (left_eye_x, left_eye_y), (left_eye_x + left_eye_w, left_eye_y + left_eye_h), (0, 0, 0), 2)
        #cv2.circle(frame, (int(left_eye_x + 0.5 * left_eye_w), int(left_eye_y + 0.5 * left_eye_h)), 2, (0, 0, 255), 2)
        right_eye_x, right_eye_y, right_eye_w, right_eye_h = (gaze.eye_right.origin[0], gaze.eye_right.origin[1], gaze.eye_right.width, gaze.eye_right.height)
        #cv2.rectangle(frame, (right_eye_x, right_eye_y), (right_eye_x + right_eye_w, right_eye_y + right_eye_h), (0, 0, 0), 2)
        #cv2.circle(frame, (int(right_eye_x + 0.5 * right_eye_w), int(right_eye_y + 0.5 * right_eye_h)), 2, (0, 0, 255), 2)
        for landmark in gaze.face_landmarks.parts():
            #pass
            cv2.circle(frame, (landmark.x, landmark.y), 1, (0, 0, 0), -1)
    
    if time.time() - calibration_time >= 5:
        if left_pupil is not None and right_pupil is not None and gaze.face is not None:
            with open("pupil_coordinates.csv", "a") as f:
                f.write(f"{left_pupil[0]},{frame_height - left_pupil[1]},{right_pupil[0]},{frame_height - right_pupil[1]},")
                f.write(f"{left_eye_x},{frame_height - left_eye_y},{left_eye_w},{frame_height - left_eye_h},")
                f.write(f"{right_eye_x},{frame_height - right_eye_y},{right_eye_w},{frame_height - right_eye_h}\n")
            with open("pupil_coordinates_relative_to_eye.csv", "a") as f:
                left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y = pupil_position_relative_to_eye_bbox(gaze)
                f.write(f"{left_pupil_x},{left_pupil_y},{right_pupil_x},{right_pupil_y}\n")
            with open("pupil_coordinates_relative_to_face.csv", "a") as f:
                left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y = pupil_position_relative_to_face_bbox(gaze)
                f.write(f"{left_pupil_x},{left_pupil_y},{right_pupil_x},{right_pupil_y}\n")
            with open("pupil_coordinates_relative_to_lm27.csv", "a") as f:
                left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y = pupil_position_relative_to_lm27(gaze, previous_positions)
                f.write(f"{left_pupil_x},{left_pupil_y},{right_pupil_x},{right_pupil_y}\n")

    analyzed_directory = 'analyzed_images'
    analyzed_path = os.path.join(analyzed_directory, image_file)
    cv2.imwrite(analyzed_path, frame)
    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()
