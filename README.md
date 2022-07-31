# fold_parallax

## Dependencies & Instructions


0 - If everything is already installed, follow the items in "Instructions.pdf" every time you run the experiment.

1 - Go to this website to download latest Anaconda installer for python then install it: https://www.anaconda.com/products/individual#windows

2 - Create a python 3.8 enviroment. After installation, Windows Search "Anaconda Prompt", then type in the prompt:

```conda create -n psychxr python=3.8```

3 - Before you run the experiment, the above enviroment needs to be activated by typing:

```conda activate psychxr ```

4 - Install Psychopy:

```conda install -c conda-forge psychopy```

5 - Install Psychxr and other supporting packages:

```pip install psychxr==0.2.4rc3.post glfw==2.5.4 psychtoolbox soundfile```

6 - Install Spyder:

```conda install spyder```

7 - Run Oculus App, draw the guardian as a 16.5 * 16.5 ground marks (the little crossings in VR) square, to make it 3 m by 3 m in reality.
	See Calibration_v14.pdf for graphical demonstrations.

8 - Go back to Anaconda Prompt, with the psychxr enviroment activated, run Spyder by typing:

```Spyder```

9 - Download everything into your computer. In Spyder, open the "fold_parallax_v_number.py". F5 to run the script, a dialogue will pop up:

	- Put your name or initial in Participant Info;

	- Vary the "Stereo Condition", you will have 4 experiments in total;
	
	- Position yourself at the desired location where you want to do the experiment, then press the "OK" button on the dialogue panel.

10 - To visualize the scene, participants are reuqired to do parallax motion from left to right at about 20 cm (aligned with the metronome audio). The scene is activated by a full left-right movement(indicated by red boundary lights).

11 - When a scene is presented, a ground plane will appear, together with a white bar on it.
	Participants are required to stand on top of the bar while facing the voronoi fold stimuli.

12 - Calibrate the scene in VR if needed.
	
	Walk to the desired position then calibrate while facing the desired orientation
	or while looking at the existing ground bar (to bring it closer). See "calibration_v14.pdf" for graphical demonstrations.
	
	When the scene is presented:
	
	- Left hand controller - button "X";
	
	- Keyboard - "c" to calibrate.
	
13 - If the scene is dimmed, it means the participant is out of the sagittal range (front-back restriction). Move along the sagittal axis to disable the dimming.

14 - Participants are required to maintain motion parallax while judging if the visual scene presents more or less motion than one would expect in the real world.
	 If perceived more, press top button "B", otherwise bottom button "A"
 
15 - Keyboard control:

	- c: calibrate the scene according to your orientation/position;
	
	- r: return to the last trial when a mis-input on the thumbstick was conducted;

	- n: next step when blackout;

	- q: next step when scene is presented - input the current adjustment and proceed to blackout;

	- x: terminate the entire experiment when scene is presented.

16 - Hand controllers:
 
	- Button "X" (left hand): to calibrate based on your current position and orientation;
	
	- Button "A", "B" (right hand): to input data and proceed.

17 - After you are done with both blocks, zip the "output" folder and email me your data.
