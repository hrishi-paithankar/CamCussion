import threading
import time
import cv2
import queue
import signal
import argparse
import glob
import os
import logging
import copy
import pygame

from led_point.display import Display
from GazeTracking.single_image_processor import SingleImageProcessor

# Step 1: Configure logging to write errors to a log file
logging.basicConfig(filename='error_log.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

task_queue = queue.Queue()
data_capture_active = True
shutdown_flag  = False

def signal_handler(sig, frame):
    global shutdown_flag
    global data_capture_active
    print("Signal handler called.")
    shutdown_flag = True
    data_capture_active = False

signal.signal(signal.SIGINT, signal_handler)

def worker():
    global shutdown_flag
    while not shutdown_flag:
        # Get a task from the queue
        task = task_queue.get()
        try:
            task()
        finally:
            # Mark the task as done
            task_queue.task_done()
    # clear the queue
    if shutdown_flag:
        task_queue.queue.clear()
    print("Worker thread stopped.")

def capture_image(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def process_image(frame, image_processor, led_point):
    #print("Other task is running.")
    # Simulate a task that takes some time
    timestamp = time.time()
    cv2.imwrite(f"outs\\frame_{timestamp}.jpg", frame)
    image_processor.process(f"outs\\frame_{timestamp}.jpg", led_point)
    #time.sleep(2)
    #print(f"Other task completed in {(time.time()-timestamp)}s.")

def capture_data(cap, display, image_processor):
    global data_capture_active
    if not data_capture_active:
        print("Data capture has been stopped.")
        return
    start_time = time.time()    
    # Simulate critical task work
    frame = capture_image(cap)
    frame = cv2.flip(frame, 1)
    #breakpoint()
    led_point = copy.deepcopy(display.get_current_position())
    #print(f"LED point position: {led_point}")
    delta = time.time() - start_time
    #print(f"Critical task completed in {delta} seconds.")
    #sprint(f"LED point position: {display.get_current_position()}")
    # After critical task, spawn a new other task
    task_queue.put(lambda: process_image(frame, image_processor, led_point))
    # Schedule the next execution of the critical task
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30
    wait_time = 1/fps - delta
    threading.Timer(wait_time, capture_data, args=(cap,display,image_processor,)).start()

def clear_images():
    files = glob.glob("outs/frame_*.jpg")
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print(f"Error: {e}")

def calibration(cap, display, image_processor):
    display.central_point()
    start_time = time.time()
    left_pupil_x = []
    left_pupil_y = []
    right_pupil_x = []
    right_pupil_y = []
    while time.time() - start_time < 5:
        display.central_point()
        frame = capture_image(cap)
        frame = cv2.flip(frame, 1)
        timestamp = time.time()
        cv2.imwrite(f"outs\\frame_{timestamp}.jpg", frame)
        led_point = display.get_current_position()
        valid, lpx, lpy, rpx, rpy = image_processor.process_without_writing(f"outs\\frame_{timestamp}.jpg", led_point)
        if valid:
            left_pupil_x.append(lpx)
            left_pupil_y.append(lpy)
            right_pupil_x.append(rpx)
            right_pupil_y.append(rpy)
    print(f"{len(left_pupil_x)} samples collected.")
    left_pupil_x = sum(left_pupil_x) / len(left_pupil_x)
    left_pupil_y = sum(left_pupil_y) / len(left_pupil_y)
    right_pupil_x = sum(right_pupil_x) / len(right_pupil_x)
    right_pupil_y = sum(right_pupil_y) / len(right_pupil_y)

    return left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y




def main():
    parser = argparse.ArgumentParser(description="Capture data from a webcam and process it.")
    parser.add_argument('--clear_images', action='store_true', help='If set, deletes all frame_*.jpg files from outs')
    args = parser.parse_args()

    if args.clear_images:
        clear_images()

    output_file_path = "outs/data.csv"
    calibration_file_path = "outs/calibration.csv"

    global data_capture_active
    display = Display()
    print("Display initialized.")

    image_processor = SingleImageProcessor(output_file_path)
    print("Image processor initialized.")
    # Set video capture properties
    width, height = 1280, 720 
    fps = 30

    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)
    print("Video capture object created.")

    # Set video width, height, and FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    threading.Thread(target=worker, daemon=True).start()
    print("Worker thread started.")

    calib = calibration(cap, display, image_processor)
    with open(calibration_file_path, "w") as f:
        f.write(f"{calib[0]},{calib[1]},{calib[2]},{calib[3]}, 1920, 1080\n")
    print("Calibration completed.")
    print(f"Calib: {calib}")

    display.run()
    time.sleep(2)

    # Start the critical task in a separate process
    critical_process = threading.Thread(target=capture_data, args=(cap,display,image_processor))
    critical_process.start()
    print("Critical task started.")

    try: 
        # Main program continues running, doing other work or spawning more tasks
        start_time = time.time()
        iteration_times = []
        while data_capture_active:
            # Example: Main program doing some work
            iteration_time = time.time()
            display.run()
            if time.time() - start_time > 300:
                print("Stopping data capture.")
                print(f"The number of tasks in the queue: {task_queue.qsize()}")
                print(f"Time elapsed: {time.time() - start_time}")
                data_capture_active = False
            iteration_times.append(time.time() - iteration_time)
        avrg = sum(iteration_times) / len(iteration_times)
        print(f"Average iteration time: {avrg}")

        while not task_queue.empty() and not shutdown_flag:
            display.wait_processing()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
        #data_capture_active = False
        
    print("Main program completed.")
    critical_process.join()  # Wait for the critical task to complete
    print("Critical task completed.")
    #task_queue.join()  # Wait for all tasks in the queue to be completed before exiting
    print("All tasks completed.")
    cap.release()  # Release the video capture object
    display.quit()  # Quit the display

if __name__ == "__main__":
    main()