# fold_parallax

## Dependencies

0 - Download everything into your computer.

1 - Go to this website to download Anaconda installer for python 3.7: https://www.anaconda.com/products/individual#windows

2 - Create a python 3.6 enviroment. Windows Search "Anaconda Prompt", type:

```conda create -n psychxr python=3.6```

3 - Each time when you run the experiment, you would need to activate the above enviroment by typing:

```conda activate psychxr ```

4 - type:

```conda install swig ```

5 - Install other dependencies, go inside "fold_parallax" folder:

```cd <your path (e.g. d/OneDrive/fold_parallax)> ```

When you are at the location, type "ls", you should be able to see a file named "requirements.txt".

6 - type:

```pip install -r requirements.txt```

7 - run fold_parallax_v...py file, you could do it using Spyder:

```Spyder```

8 - F5 to run the script, a dialogue will pop up:

	- Put your name or initial in Participant Info;

	- Vary the "Stereo Condition" and "Motion Condition" (both binary choices), you will have 4 experiments in total.

9 - You might need to re-draw the guardian to visualize the stimuli properly, the instructions is in "gardian.pdf".

10 - Only right hand controller is used.
 
	- Button "B" is for next step;

	- Button "A": When you want to exit, use button "B" to proceed to the next available scene and then press "A" to terminate.

11 - Keyboard control:

	- n: next step when blackout;

	- q: next step when scene is presented;

	- x: terminate when scene is presented

12 - Participants are required to stand at the bar on the ground plane. If the scene is dimmed, it means the participant is out of 
the sagittal range (front-back restriction).

13 - For Motion Condition - "motion", participants are reuqired to do parallax motion (with the metronome audio) from left to right
 at about 30 cm. The next scene is only activated by a full left-right movement (indicated by red boundary lighes, button B won't work).

14 - For Motion Condition - "static", scene is activated by button B. Participants are required to stand still at the bar and make sure
 neither of the boundary light is on.

15 - When a scene is presented, a fold will be presented, participants are required to adjust the angle of the fold until it's orthogonal
 using the thumb stick. When the adjustment is final, press button "B" to proceed.

16 - After you are done with all 4 experiments, zip the "output" folder and email me your data.
