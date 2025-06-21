import csv
from dataclasses import dataclass
import time

import matplotlib.pyplot as plt
import numpy as np

from led_point.point import Point

# Define the eye class
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

class GazeTrackingPlotter:
    def __init__(self): 
        self.previous_left_angle = 0
        self.previous_right_angle = 0
        self.previous_led_angle = 0

    def read_row(self, row):
        # Extract the coordinates from the row
        left_pupil = Pupil(*[float(i) for i in row[:2]])
        right_pupil = Pupil(*[float(i) for i in row[2:4]])
        valid = row[4] == 'valid'
        led_point = Point(*[float(i) for i in row[5:7]])

        return left_pupil, right_pupil, valid, led_point

    def get_num_datapoints(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            return sum(1 for row in reader)

    def get_current_pupil_velocity(self, pupil_x, pupil_y):
        if len(pupil_x) < 2:
            return 0
        else:
            return ((pupil_x[-1] - pupil_x[-2])**2 + (pupil_y[-1] - pupil_y[-2])**2)**0.5
        
    def calculate_angle_diff(self, left_pupil, right_pupil, left_pupil_calibration, right_pupil_calibration, led_point, screen_midpoint):
        left_angle_raw = np.arctan2(left_pupil.y - left_pupil_calibration.y, left_pupil.x - left_pupil_calibration.x)
        right_angle_raw = np.arctan2(right_pupil.y - right_pupil_calibration.y, right_pupil.x - right_pupil_calibration.x)
        led_angle_raw = np.arctan2(led_point.y - screen_midpoint.y, led_point.x - screen_midpoint.x)
        
        # Unwrap each angle manually
        left_angle = self.unwrap_angle(left_angle_raw, self.previous_left_angle)
        right_angle = self.unwrap_angle(right_angle_raw, self.previous_right_angle)
        led_angle = self.unwrap_angle(led_angle_raw, self.previous_led_angle)
        
        # Update previous angles
        self.previous_left_angle = left_angle
        self.previous_right_angle = right_angle
        self.previous_led_angle = led_angle

        left_angle_diff = left_angle - led_angle
        right_angle_diff = right_angle - led_angle

        return left_angle_diff, right_angle_diff    

    def unwrap_angle(self, current_angle, previous_angle):
        # Calculate the difference
        angle_diff = current_angle - previous_angle
        
        # Adjust if the angle jumps
        if angle_diff > np.pi:
            current_angle -= 2 * np.pi
        elif angle_diff < -np.pi:
            current_angle += 2 * np.pi
        
        return current_angle

    def read_and_plot_coordinates(self, file_path, calibration_file_path):
        # Read the CSV file
        with open(calibration_file_path, 'r') as file:
            reader = csv.reader(file)
            row = next(reader)
            left_pupil_calibration = Pupil(*[float(i) for i in row[:2]])
            right_pupil_calibration = Pupil(*[float(i) for i in row[2:4]])
            screen_midpoint = Point(*[float(i)/2 for i in row[4:6]])
        with open(file_path, 'r') as file:
            num_datapoints = self.get_num_datapoints(file_path)
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            plt.style.use('dark_background')
            # Create a new figure and axis
            fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(12.80, 7.20), dpi=100)


            # Initialize numpy arrays to store the coordinates
            left_pupil_x = []
            left_pupil_y = []
            right_pupil_x = []
            right_pupil_y = []
            led_point_x = []
            led_point_y = []
            velocity_left_pupil = []
            velocity_right_pupil = []
            left_angle = []
            right_angle = []

            light_blue = (171/255, 209/255, 215/255)
            mid_blue = (85/255, 177/255, 188/255)
            dark_blue = (69/255, 146/255, 155/255)

            # Initialize plot lines for each dataset
            line_left_eye, = ax1.plot([], [], color=light_blue, label='Left Eye', linewidth=1)
            last_left_eye, = ax1.plot([], [], 'o', color=light_blue, linewidth=1)
            left_eye_calib, = ax1.plot([], [], 'o', color=light_blue, linewidth=1)
            line_right_eye, = ax2.plot([], [], color=mid_blue, label='Right Eye', linewidth=1)
            last_right_eye, = ax2.plot([], [], 'o', color=mid_blue, linewidth=1)
            right_eye_calib, = ax2.plot([], [], 'o', color=mid_blue, linewidth=1)
            line_velocity_left, = ax3.plot([], [], color=light_blue, label='Left Eye Velocity', linewidth=1)
            line_velocity_right, = ax4.plot([], [], color=mid_blue, label='Right Eye Velocity', linewidth=1)
            line_led_point, = ax5.plot([], [], color=dark_blue, label='LED Point', linewidth=1)
            last_led_point, = ax5.plot([], [], "o", color=dark_blue, linewidth=1)
            line_left_angle, = ax6.plot([], [], color=light_blue, label='Left Eye', linewidth=1)
            line_right_angle, = ax6.plot([], [], color=mid_blue, label='Right Eye', linewidth=1)
            ax6.legend(fontsize='small')

            left_eye_calib.set_data(left_pupil_calibration.x, left_pupil_calibration.y)
            right_eye_calib.set_data(right_pupil_calibration.x, right_pupil_calibration.y)

            # Set static properties of the plots
            ax1.set_xlim(0, 1)  # Adjust these limits based on your data
            ax1.set_ylim(0, 1)
            ax1.set_xlabel('x in px')
            ax1.set_ylabel('y in px')
            ax1.set_title('Left Eye Position')
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.set_xlabel('x in px')
            ax2.set_ylabel('y in px')
            ax2.set_title('Right Eye Position')
            ax3.set_xlim(0, num_datapoints)
            ax3.set_xlabel('frame')
            ax3.set_ylabel('v in px/frame')
            ax3.set_title('Left Eye Velocity')
            ax4.set_xlim(0, num_datapoints)
            ax4.set_xlabel('frame')
            ax4.set_ylabel('v in px/frame')
            ax4.set_title('Right Eye Velocity')
            ax5.set_xlim(-100, 2020)
            ax5.set_ylim(-100, 1180)
            ax5.set_xlabel('x in px')
            ax5.set_ylabel('y in px')
            ax5.set_title('LED Point Position')
            ax6.set_xlim(0, num_datapoints)
            ax6.set_ylim(-np.pi, np.pi)
            ax6.set_xlabel('frame')
            ax6.set_ylabel(r'$\Delta\phi$ in rad')
            ax6.set_title('Angle Differences relative to LED Point Position')

            iteration = 0
            # Iterate over each line in the CSV file
            for row in reader:
                # Append new coordinates to the numpy arrays
                start_time = time.time()
                left_pupil, right_pupil, _, led_point = self.read_row(row)
                left_pupil_x.append(left_pupil.x)
                left_pupil_y.append(left_pupil.y)
                right_pupil_x.append(right_pupil.x)
                right_pupil_y.append(right_pupil.y)
                led_point_x.append(led_point.x)
                led_point_y.append(led_point.y)

                # Calculate the angle differences
                left_angle_diff, right_angle_diff = self.calculate_angle_diff(left_pupil, right_pupil, left_pupil_calibration, right_pupil_calibration, led_point, screen_midpoint)
                left_angle.append(left_angle_diff)
                right_angle.append(right_angle_diff)

                velocity_left_pupil.append(self.get_current_pupil_velocity(left_pupil_x, left_pupil_y))
                velocity_right_pupil.append(self.get_current_pupil_velocity(right_pupil_x, right_pupil_y))

                # Update plot data
                line_left_eye.set_data(left_pupil_x, left_pupil_y)
                last_left_eye.set_data(left_pupil.x, left_pupil.y)
                line_right_eye.set_data(right_pupil_x, right_pupil_y)
                last_right_eye.set_data(right_pupil.x, right_pupil.y)
                line_velocity_left.set_data(range(len(velocity_left_pupil)), velocity_left_pupil)
                line_velocity_right.set_data(range(len(velocity_right_pupil)), velocity_right_pupil)
                line_led_point.set_data(led_point_x, led_point_y)
                last_led_point.set_data(led_point.x, led_point.y)
                line_left_angle.set_data(range(len(left_angle)), left_angle)
                line_right_angle.set_data(range(len(right_angle)), right_angle)
                #line_led_angle.set_data(range(len(led_angle)), led_angle)

                
                # Adjust dynamic properties of the plots if necessary
                ax1.set_xlim(np.min(left_pupil_x)-10, np.max(left_pupil_x)+10)
                ax1.set_ylim(np.min(left_pupil_y)-10, np.max(left_pupil_y)+10)
                ax2.set_xlim(np.min(right_pupil_x)-10, np.max(right_pupil_x)+10)
                ax2.set_ylim(np.min(right_pupil_y)-10, np.max(right_pupil_y)+10)
                ax3.set_ylim(0, np.max(velocity_left_pupil)+1)
                ax4.set_ylim(0, np.max(velocity_right_pupil)+1)
                #ax5.set_xlim(np.min(led_point_x)-10, np.max(led_point_x)+10)
                #ax5.set_ylim(np.min(led_point_y)-10, np.max(led_point_y)+10)

                plt.subplots_adjust(wspace=0.4, hspace=1)
                plt.draw()
                #plt.get_current_fig_manager().window.showMaximized()
                #filename = f"plot_img\plot_{iteration}.png"  # Generates filenames like plot_0001.png, plot_0002.png, etc.
                #plt.savefig(filename)
                print(f"Processing time: {time.time() - start_time:.5f} seconds")
                iteration += 1
                process_time = time.time() - start_time
                pause_time = max(0.033 - process_time, 0)
                #breakpoint()
                plt.pause(pause_time)

        # Show the final plots
        plt.show(block=False)
        try:
            # Enter a loop that keeps the program running
            while True:
                plt.pause(1)  # Sleep to prevent this loop from consuming too much CPU
        except KeyboardInterrupt:
            # This block is executed when Ctrl+C is pressed
            print("Program interrupted by user.")
            # Perform any necessary cleanup here

        plt.close()



if __name__ == '__main__':
    # Define the file path
    #file_path = 'pupil_coordinates_relative_to_eye.csv'
    #file_path = 'pupil_coordinates_relative_to_face.csv'
    file_path = r'outs_backup\data.csv'
    calibration_file_path = r'outs_backup\calibration.csv'

    # Initialize the GazeTrackingPlotter object
    gaze_plotter = GazeTrackingPlotter()

    # Read and plot the coordinates from the CSV file
    gaze_plotter.read_and_plot_coordinates(file_path, calibration_file_path)