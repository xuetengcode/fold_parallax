# fold_parallax

## Dependencies

0 - Download everything into your computer.

1 - Go to this website to download Anaconda installer for python 3.7 then install it: https://www.anaconda.com/products/individual#windows

2 - Create a python 3.6 enviroment. After installation, Windows Search "Anaconda Prompt", then type in the prompt:

```conda create -n psychxr python=3.6```

3 - Before you run the experiment, the above enviroment needs to be activated by typing:

```conda activate psychxr ```

4 - Install dependency pywinhook:

```conda install -c conda-forge pywinhook ```

5 - Install Spyder:

```pip install spyder ```

6 - Install Psychxr and Psychopy:

```pip install psychxr psychopy```

7 - Run Oculus App, draw the guardian as a 3 m-by-3 m square.

8 - Go back to Anaconda Prompt, with the psychxr enviroment activated, run Spyder by typing:

```Spyder```

9 - In Spyder, open the "fold_parallax_v_number.py". F5 to run the script, a dialogue will pop up:

	- Put your name or initial in Participant Info;

	- Vary the "Stereo Condition" and "Motion Condition" (both binary choices), you will have 4 experiments in total;
	
	- Position yourself at the desired location where you want to do the experiment, then press the "OK" button on the dialogue panel.

10 - To visualize the scene:
	
	- For Motion Condition "motion": participants are reuqired to do parallax motion from left to right at about
					30 cm (aligned with the metronome audio). The scene is activated by a full left-right
					movement(indicated by red boundary lights).
	
	- For Motion Condition "static": scene is activated by button "A" on right hand controller or "n" on the keyboard.
					Participants are required to stand still at the ground bar and make sure neither 
					boundary light is on.

11 - When a scene is presented, a ground plane will appear, together with a white bar on it.
	Participants are required to stand on top of the bar while facing the voronoi fold stimuli.

12 - Calibrate the scene in VR if needed.
	
	Walk to the desired position then calibrate while you are looking at the existing ground bar
	or while facing the desired orientation. See "calibration_v14.pdf" for graphic demonstrations.
	
	When the scene is presented:
	
	- Left hand controller - button "X";
	
	- Keyboard - "c" to calibrate.
	
13 - If the scene is dimmed, it means the participant is out of the sagittal range (front-back restriction). Move along the sagittal axis to disable the dimming.

14 - Participants are required to maintain the motion condition while adjusting the angle of the fold using the thumb stick until the fold is orthogonal. When the adjustment is final, press button "A" to proceed.
 
15 - Keyboard control:

	- c: calibrate the scene according to your orientation/position;
	
	- r: return to the last trial when a mis-input on the thumbstick was conducted;

	- n: next step when blackout;

	- q: next step when scene is presented - input the current adjustment and proceed to blackout;

	- x: terminate the entire experiment when scene is presented.

16 - Hand controllers:
 
	- Button "X" (left hand): calibration based on your current position and orientation;
	
	- Button "A" (right hand): next step - visualize the scene when blackout (static), 
				or enter data and go blackout when the scene is presented);

	- Button "B" (right hand): terminate the entire experiment when the scene is presented.

17 - After you are done with all 4 experiments, zip the "output" folder and email me your data.
