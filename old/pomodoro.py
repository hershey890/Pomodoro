import time
import tkinter
from PIL import Image, ImageTk # use any library to display an image ex PIL, cv2, qt, matplotlib
import subprocess
import sys 
import os
if sys.platform == "win32":
    import winsound


# User set variables
frequency = 523 # Hz
duration = 700 # ms
work_time = 25 # min
short_break_time = 5 # min, 3-5 min
long_break_time = 25 # min, 15-30 min every 4 pomodoro work sessions 

# Progam variables
num_pomodoro_intervals = 0
sleep_duration = 0.2 # s


def beep(frequency: int, duration: int) -> None:
    if sys.platform == "win32":
        winsound.Beep(frequency, duration)
    else:
        if subprocess.run(["beep", "-f", str(frequency), "-l", str(duration)]):
            print("beep failed")
            sys.exit(1)


# display window    
time0 = time.time() #s
with Image.open("./pomodoro_image.png") as img:
    while 1:
        # Work
        time1 = time.time() - time0
        if time1/60 < work_time:
            time.sleep(sleep_duration)
            sys.stdout.write(("\rWorking time (%i): %02d:%02d" % (num_pomodoro_intervals, time1//60, int(time1-(time1//60)*60))))

        # Break
        else:
            # img.show()
            tk_window = tkinter.Tk()
            tk_window.attributes('-topmost', True)
            tk_image = ImageTk.PhotoImage(img)
            # tk_window.geometry("1000x800")

            # open window
            label = tkinter.Label(tk_window, image=tk_image)
            label.pack()
            tk_window.update()

            # Alert sound
            for i in range(4):
                time.sleep(duration/1000)
                # winsound.Beep(frequency, duration)
                beep(frequency, duration)
                tk_window.update() 

            # Long break
            if num_pomodoro_intervals == 3:
                while (time.time() - time0) / 60 < work_time + long_break_time:
                    time.sleep(sleep_duration)
                    time1 = time.time() - time0 - work_time*60
                    sys.stdout.write(("\rLong break time: %02d:%02d" % (time1//60, int(time1-(time1//60)*60))))
                    tk_window.update()
                num_pomodoro_intervals = 0

            # Short break
            else:
                while (time.time() - time0) / 60 < work_time + short_break_time:
                    time.sleep(sleep_duration)
                    time1 = time.time() - time0 - work_time*60
                    sys.stdout.write(("\rShort break time (%i): %02d:%02d" % (num_pomodoro_intervals, time1//60, int(time1-(time1//60)*60))))
                    tk_window.update()
                num_pomodoro_intervals += 1
            tk_window.destroy()
            time0 = time.time()
            sys.stdout.flush()