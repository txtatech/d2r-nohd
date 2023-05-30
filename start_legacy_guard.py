import time
import ctypes
import pynvml
from pynvml import nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates
from pynvml import NVMLError, nvmlInit, nvmlShutdown
from pynput import keyboard
import psutil

def send_keypress():
    # Simulate the G key press event at the OS level
    ctypes.windll.user32.keybd_event(0x47, 0, 0, 0)  # 0x47 is the virtual key code for 'G'
    ctypes.windll.user32.keybd_event(0x47, 0, 2, 0)  # Release the G key

def on_key_press(key):
    if key == keyboard.Key.space:
        global pause
        pause = not pause
        if pause:
            print("Monitoring paused")
        else:
            print("Monitoring resumed")

def get_d2r_processes():
    # Get all processes with the name "D2R.exe"
    return [proc for proc in psutil.process_iter(['name']) if proc.info['name'] == 'D2R.exe']

def get_gpu_usage(process):
    try:
        # Get the process's device handle
        devices = pynvml.nvmlDeviceGetCount()
        for i in range(devices):
            handle = nvmlDeviceGetHandleByIndex(i)
            info = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
            for proc in info:
                if proc.pid == process.pid:
                    gpu_handle = handle
                    gpu_utilization = nvmlDeviceGetUtilizationRates(gpu_handle).gpu
                    return gpu_utilization
    except (NVMLError, psutil.NoSuchProcess, psutil.AccessDenied):
        return 0

def check_gpu_usage():
    interval = 6  # Time interval in seconds
    gpu_threshold = 40  # GPU usage threshold in percentage
    window_title = 'Legacy Guard'  # Title for the window

    # Set the window title
    ctypes.windll.kernel32.SetConsoleTitleW(window_title)

    # Initialize NVML
    nvmlInit()

    global pause
    pause = False  # Variable to track the pause state

    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    while True:
        try:
            if not pause:
                # Get the number of NVIDIA GPUs
                num_gpus = nvmlDeviceGetCount()

                for gpu_idx in range(num_gpus):
                    # Get GPU handle
                    gpu_handle = nvmlDeviceGetHandleByIndex(gpu_idx)

                    # Get GPU utilization
                    gpu_utilization = nvmlDeviceGetUtilizationRates(gpu_handle).gpu

                    if gpu_utilization >= gpu_threshold:
                        # Send the G key
                        send_keypress()

                d2r_processes = get_d2r_processes()
                for process in d2r_processes:
                    gpu_usage = get_gpu_usage(process)
                    print(f"D2R.exe (PID: {process.pid}) - GPU Usage: {gpu_usage}%")

        except NVMLError as error:
            print(f"NVML Error: {error}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        time.sleep(interval)  # Wait for the specified interval before checking again

    # Close NVML
    nvmlShutdown()

check_gpu_usage()
