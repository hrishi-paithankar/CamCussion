import csv
from dataclasses import dataclass
import time

import matplotlib.pyplot as plt

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


def plot_eye_coordinates(left_eye, right_eye):
    # Create a new figure and axis
    fig, ax = plt.subplots()

    # Plot the coordinates as points on the axis
    ax.plot(left_eye[0], left_eye[1], 'ro', label='Eye 1')
    ax.plot(right_eye[0], right_eye[1], 'bo', label='Eye 2')

    # Set the axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Add a legend
    ax.legend()

    # Show the plot
    plt.show()

def read_row(row):
    # Extract the coordinates from the row
    left_pupil = Pupil(*[float(i) for i in row[:2]])
    right_pupil = Pupil(*[float(i) for i in row[2:4]])
    left_eye = Eye(*[float(i) for i in row[4:8]])
    right_eye = Eye(*[float(i) for i in row[8:12]])

    return left_pupil, right_pupil, left_eye, right_eye



def read_and_plot_coordinates(file_path):
    # Read the CSV file
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        # Create a new figure and axis
        fig, ax = plt.subplots()

        # Add a legend
        ax.legend(['Eye 1', 'Eye 2'])

        # Initialize lists to store the coordinates
        left_pupil_x, left_pupil_y = [], []
        right_pupil_x, right_pupil_y = [], []

        # Iterate over each line in the CSV file
        for row in reader:
            # Append new coordinates to the lists
            left_pupil, right_pupil, left_eye, right_eye = read_row(row)
            #breakpoint()
            left_pupil_x.append(left_pupil.x)
            left_pupil_y.append(left_pupil.y)
            right_pupil_x.append(right_pupil.x)
            right_pupil_y.append(right_pupil.y)

            # Clear the previous plot
            ax.clear()

            # Plot the trajectories
            ax.plot(left_pupil_x, left_pupil_y, 'r-', label='Left Eye')  # 'r-' creates a red line
            ax.plot(right_pupil_x, right_pupil_y, 'b-', label='Right Eye')  # 'b-' creates a blue line
            
            # Set the axis limits
            ax.set_xlim(min(left_pupil_x+right_pupil_x)-10, max(left_pupil_x+right_pupil_x)+10)
            ax.set_ylim(min(left_pupil_y+right_pupil_y)-10, max(left_pupil_y+right_pupil_y)+10)

            # Show the plot with a delay of 0.05 seconds
            plt.show(block=False)
            plt.pause(0.05)
            plt.draw()

        # Show the final plot
        plt.show()


if __name__ == '__main__':
    # Define the file path
    file_path = 'pupil_coordinates.csv'

    # Read and plot the coordinates from the CSV file
    read_and_plot_coordinates(file_path)