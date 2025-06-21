import cv2
import os
from dataclasses import dataclass

from GazeTracking.gaze_tracking import GazeTracking
from led_point.point import Point

@dataclass
class Eye:
    x: float
    y: float
    w: float
    h: float

@dataclass
class Pupil:    
    x: float
    y: float

@dataclass
class Landmark:
    x: float
    y: float    

class SingleImageProcessor:
    def __init__(self, data_file_path):
        self.gaze = GazeTracking()
        self.data_file_path = data_file_path
        self.previous_positions = []
        self.img_height = None
        self.img_width = None
        self.calib_left = None
        self.calib_right = None
        # Create an empty data file
        with open(data_file_path, 'w') as file:
            file.write("left_pupil_x,left_pupil_y,right_pupil_x,right_pupil_y,valid,led_x,led_y\n")

    def set_calibration(self, left_x, left_y, right_x, right_y):
        self.calib_left = Pupil(left_x, left_y)
        self.calib_right = Pupil(right_x, right_y)

    def read_image(self, image_path):
        self.image = cv2.imread(image_path)
        self.img_height, self.img_width, _ = self.image.shape

    def process_without_writing(self, image_path, led_point: Point):
        self.read_image(image_path)
        self.gaze.refresh(self.image)
        if self.prediction_is_valid():
            try:
                left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y = self.pupil_position_relative_to_lm27(self.gaze)
                return True, left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y
            except Exception as e:
                print(f"Error processing image: {e}")
        return False, None, None, None, None

    def process(self, image_path, led_point: Point):
        self.read_image(image_path)
        self.gaze.refresh(self.image)
        #breakpoint()
        if self.prediction_is_valid():
            try:
                left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y = self.pupil_position_relative_to_lm27(self.gaze)
                led_point_cart = Point(led_point.x, 1080 - led_point.y)
                with open(self.data_file_path, 'a') as file:
                    file.write(f'{left_pupil_x},{left_pupil_y},{right_pupil_x},{right_pupil_y}, valid,{led_point_cart.x},{led_point_cart.y}\n')
                return True
            except Exception as e:
                print(f"Error processing image: {e}")
        try:
            with open(self.data_file_path, 'a') as file:
                #breakpoint()
                file.write(f'{self.previous_positions[-1][0]},{self.previous_positions[-1][1]},{self.previous_positions[-1][2]},{self.previous_positions[-1][3]}, not_valid, {led_point.x}, {led_point.y}\n')
        except Exception as e:
            print(f"Error processing image: {e}")
        return False

    def prediction_is_valid(self):
        if self.get_pupil_left is not None and self.get_pupil_right is not None and self.get_face is not None:
            return True
        return False


    def show_frame(self):
        frame = self.gaze.annotated_frame()
        cv2.imshow("Demo", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_frame(self):
        return self.gaze.annotated_frame()

    def get_gaze(self):
        return self.gaze

    def get_image(self):
        return self.image

    def get_eyes(self):
        return self.gaze.eyes

    def get_pupil_left(self):
        return self.gaze.pupil_left_coords()

    def get_pupil_right(self):
        return self.gaze.pupil_right_coords()

    def get_landmarks(self, number = None):
        if number:
            return self.gaze.face_landmarks.part(number)
        return self.gaze.face_landmarks

    def get_face(self):
        return self.gaze.face
    
    def pupil_position_relative_to_lm27(self, gaze):
        left_pupil = self.get_pupil_left()
        right_pupil = self.get_pupil_right()
        lm27 = self.get_landmarks(27)

        # convert from image coordinates to cartesian coordinates
        left_pupil = Pupil(left_pupil[0], self.img_height - left_pupil[1])
        right_pupil = Pupil(right_pupil[0], self.img_height - right_pupil[1])
        lm27 = Landmark(lm27.x, self.img_height - lm27.y)

        left_pupil_x = left_pupil.x - lm27.x
        left_pupil_y = left_pupil.y - lm27.y
        right_pupil_x = right_pupil.x - lm27.x
        right_pupil_y = right_pupil.y - lm27.y

        self.previous_positions.append((left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y))
        if len(self.previous_positions) > 3:
            self.previous_positions.pop(0)

        mean_left_pupil_x = sum([pos[0] for pos in self.previous_positions]) / len(self.previous_positions)
        mean_left_pupil_y = sum([pos[1] for pos in self.previous_positions]) / len(self.previous_positions)
        mean_right_pupil_x = sum([pos[2] for pos in self.previous_positions]) / len(self.previous_positions)
        mean_right_pupil_y = sum([pos[3] for pos in self.previous_positions]) / len(self.previous_positions)

        return mean_left_pupil_x, mean_left_pupil_y, mean_right_pupil_x, mean_right_pupil_y
