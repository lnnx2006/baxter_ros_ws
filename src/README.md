display baxter trajectory with numpy files
==============


## building : change to your python3 path
```
     catkin config -DPYTHON_EXECUTABLE=/usr/bin/python3 -DPYTHON_INCLUDE_DIR=/usr/include/python3.8 -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.8.so 
```

## commands : run from 3 different terminals
```
     roscore
     roslaunch baxter_description display_baxter_from_npy.launch
     rosrun display_baxter_trajectory display_left_arm_npy.py
```