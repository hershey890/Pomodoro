# Python Pomodoro
A command line version of the famous Pomodoro method timer. The program plays a ringer at the end of each study interval.  
Interval:
- 25 min study time
- 4 x 25 min study intervals
- 5 minute short break
- 25 minute long break  
The intervals are modifiable in pomodoro.py. I intend to make a separate .json file storing the configs.

## Requirements
- Python 3 (I used 3.12)
- If not on Windows, the `playsound` package is recommended. Without it, a beep at the end of each study/break interval may not occur. To install use `pip install playsound` or `conda install conda-forge::playsound`

## Usage
```Bash
$ python pomodoro.py
Work time (0) | Time Total: 25:00 | Time Elapsed: 00:06
```