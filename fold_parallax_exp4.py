"""
crashes when starting a new round
https://www.psychopy.org/general/units.html

Change notes: 
    - Jul 2022, gain perception experiments
    - Jul 2022, from v25_v4
    - Aug 2023, fold_parallax_exp4.py
"""
import time
from psychopy import gui
from psychopy import visual, event, core
from psychopy.tools import rifttools
from psychopy.tools import gltools
from psychopy.sound import Sound
import psychxr.libovr as libovr
import numpy as np

from random import random, shuffle
import math
import os

from subfunctions.general import (
    write2file25, init_output, log2file, expand_data
    )
from subfunctions.objects import (
    create_half_fold, red_activate, positive_or_negative, 
    create_floor, create_aperture, create_origin, create_central_line
    )
from subfunctions.scenes import fold_scene

# In[]


def blackscene(beep, hmd, redlight, metronome, play_sound, timediff, lasttime, auto=False):
    
    red_cnt_l = 0
    red_cnt_r = 0
    
    hit_left = True
    hit_right = False
    activate_cnt = 1
    total_time = 32*3 #===================================== change here
    auto_cnt = 0
# =============================================================================
#     if play_sound:
#              metronome.stop(reset=True)
#              metronome.play()
# =============================================================================
    while 1:
         currenttime = hmd.getPredictedDisplayTime()
         
# =============================================================================
#          if play_sound:
#              if abs(currenttime - lasttime - timediff) < 0.01 and currenttime-lasttime > 0.1 or abs(currenttime - lasttime - timediff) >10:
#                 metronome.stop(reset=True)
#                 metronome.play()
#                 lasttime = currenttime
# =============================================================================
                
         state = hmd.getTrackingState(currenttime)
         headPose = state.headPose.thePose    
         hmd.calcEyePoses(headPose)
         
         
         for eye in ('left', 'right'):
             hmd.setBuffer(eye)
             hmd.setDefaultView(clearDepth=True)
             hmd, hit_left, hit_right, red_cnt_l, red_cnt_r = red_activate(hmd, headPose, eye, redlight, hit_left, hit_right, red_cnt_l, red_cnt_r)    
         hmd.flip()
         
         if auto:
             if auto_cnt > total_time:
                 break
             auto_cnt += 1
             
         if red_cnt_l >= activate_cnt and red_cnt_r >= activate_cnt and play_sound:
             break
         
         if event.getKeys('n') or hmd.shouldQuit:
             break
         
         if not play_sound and hmd.getButtons('A', 'Touch', 'falling')[0] and not auto:
             beep.stop(reset=True)
             beep.play()
         #if hmd.getButtons('A', 'Touch', 'falling')[0]:
             break
         if event.getKeys('r'): # get rid of multiple triggering
             continue
    
    
    return lasttime

# In[]
def run_exp(metronome, hmd, bino, SEL,
            TOTAL_EXP=45, play_sound=True, stopApp=False, scene_head_pose0=[0,0,0]):
    
    results = []
    IMG_PATH = r'.\images'
    img_path2 = r'.\images'
    OFFSET = 0
    all_logs = []
    
    all_exp = np.arange(TOTAL_EXP)
    shuffle(all_exp)
    selected_exp = all_exp[:SEL]
        
    if ok_data[3] in ["motion"]:
        all_gain = [1/2, 2/3, 4/5, 1, 5/4, 3/2, 2]
        #all_gain = [1/2, 2]
    else:
        all_gain = [1]
    all_distance = [-1.5]
    
    if ok_data[5] in ["constant"]: # always take idx 0
        all_width = [1., 1., 1.]
    else:
        all_width = [1., 1.125, 1.25]
    
    total = len(all_gain) * 1 * ok_data[1]
    # ----------------------- set exp conditions
    exp_conditions = []
    for _ in range(ok_data[1]): # repeat exp
        for i_g in range(len(all_gain)):
            for i_d in range (len(all_distance)):
                voro_distance = voros[i_d]
                voro_width = widths[0]
                voro_str = voro_distance + '_' + voro_width + ".png"
                voro = gltools.createTexImage2dFromFile(r'{}'.format(os.path.join(IMG_PATH, voro_str)))
                left = create_half_fold(all_width[0]*abs(all_distance[i_d])/1.5,'left')
                right = create_half_fold(all_width[0]*abs(all_distance[i_d])/1.5,'right')                
                exp_conditions.append([all_distance[i_d], all_gain[i_g], all_width[0], left, right, voro])
                
    shuffle(exp_conditions)
    
    #play_sound = True
    #depth_restriction = False
    timediff = 1
    #MAX_EXP = 30
    #---------------------- set world parameters
    floor_far = -8.5
    floor_close = 1.5
    origin_line = 0
    #--------------------------
    
    #hmd.ambientLight = [0.5, 0.5, 0.5]
    # https://www.psychopy.org/api/visual/lightsource.html#psychopy.visual.LightSource
    #dirLight = LightSource(hmd, pos=(0., 1., 0.), ambientColor=(0.0, 1.0, 0.0), lightType='point')
    #hmd.lights = dirLight    
    redlight = visual.GratingStim(hmd, mask='gauss', size=3.0, tex=None, color='red', contrast=0.5, units='norm')
    redlight.setOpacity(1) # 0.5
    
    shutter_dict = {
        #         Postion,    direction axis, rotation (degree) 
        'front': [(0, 5, -0.9), (1, 0, 0), 0.0],
        'back': [(0, 5, 9.1), (1, 0, 0), -180.0],
        'top': [(0, 10, 4.1), (1, 0, 0), 90.0],
        'bottom': [(0, 0, 4.1), (1, 0, 0), -90.0],
        'left': [(-5, 5, 4.1), (0, 1, 0), 90.0],
        'right': [(5, 5, 4.1), (0, 1, 0), -90.0]
        }
    shutter_dict_pole = {
        #         Postion,    direction axis, rotation (degree) 
        'front': [(0, 5, -0.45), (1, 0, 0), 0.0],
        'back': [(0, 5, 9.55), (1, 0, 0), -180.0],
        'top': [(0, 10, 4.55), (1, 0, 0), 90.0],
        'bottom': [(0, 0, 4.55), (1, 0, 0), -90.0],
        'left': [(-5, 5, 4.55), (0, 1, 0), 90.0],
        'right': [(5, 5, 4.55), (0, 1, 0), -90.0]
        }
    
    stim_shutter = visual.PlaneStim(hmd, size=(10, 10), pos=shutter_dict['front'][0], 
                                    color=(-1, -1, -1), opacity=0.5)
    stim_shutter.thePose.setOriAxisAngle(shutter_dict['front'][1], shutter_dict['front'][2])
    
    
    stim_floor_big = create_floor(z_far=floor_far, z_close=floor_close)
    stim_floor_small = create_floor(z_far=-1, z_close=5)
    stim_aperture_low = create_aperture()
    stim_aperture_high = create_aperture(y0=10, y1=0.3)
    stim_aperture_left = create_aperture(x0=-3,x1=-0.3,y0=10, y1=-2.8)
    stim_aperture_right = create_aperture(x0=0.3,x1=3,y0=10, y1=-2.8)
    stim_origin = create_origin(z0=origin_line)
    stim_line = create_central_line()
    
    
    FloorTexture = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'diffuse.png')))
    WhiteTexture = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'White.png')))
    BlackoutTexture = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'blackout.png')))
    
    right_img = r'{}'.format(os.path.join(img_path2, 'cube_right.png'))
    left_img = r'{}'.format(os.path.join(img_path2, 'cube_left.png'))
    up_img = r'{}'.format(os.path.join(img_path2, 'cube_ceiling.png'))
    down_img = r'{}'.format(os.path.join(img_path2, 'cube_floor.png'))
    back_img = r'{}'.format(os.path.join(img_path2, 'cube_back.png'))
    front_img = r'{}'.format(os.path.join(img_path2, 'cube_front.png'))
    
    right_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_right.png'))
    left_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_left.png'))
    up_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_ceiling.png'))
    down_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_floor.png'))
    back_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_back.png'))
    front_img_dimmed = r'{}'.format(os.path.join(img_path2, 'dimmed_front.png'))
    sky = visual.SceneSkybox(hmd, (right_img, left_img, up_img, down_img, 
                                   back_img, front_img))    
    skydark = visual.SceneSkybox(hmd, (right_img_dimmed, left_img_dimmed, up_img_dimmed, down_img_dimmed, 
                                   back_img_dimmed, front_img_dimmed))
    
    
# =============================================================================
#     metronome = Sound(r'.\audio\output.wav')
# =============================================================================
    
    if play_sound:
        metronome.stop(reset=True)
        metronome.play()
    
    beep = Sound('C')
    nextRound = False
    
    #exp_id = 0
    print('==> Starting a new round')        
    #while not nextRound and not stopApp and exp_id <= MAX_EXP:
    
    lasttime = hmd.getPredictedDisplayTime()
    i_exp = 0
    updated = False
    skip_black = False

    haptics_time = 3

    while i_exp < len(exp_conditions):
    #for i_exp in range(len(exp_conditions)):
        local_log = []
        if i_exp in selected_exp:
            RECORD_LOG = True
        else:
            RECORD_LOG = False
            
        print('[debug info] Exp %s/%i: [distance, gain, width] = [%s, %s, %s]' % (
                i_exp, total, *exp_conditions[i_exp][:3]))
        
        stim_left = exp_conditions[i_exp][3]
        stim_right = exp_conditions[i_exp][4]
        voro = exp_conditions[i_exp][5]
        
        
        if stopApp:
            break
  
        #exp_id += 1
        #rand_ang = math.pi * (15 + random()*25)/180 * positive_or_negative()
        rand_ang = math.pi * (random()*5)/180 * positive_or_negative()
        
        # initialize object locaiton
        trianglePosition0 = (
            scene_head_pose0[0], hmd.eyeHeight, scene_head_pose0[-1] + OFFSET
            )
        trianglePosition = (
            scene_head_pose0[0], hmd.eyeHeight, scene_head_pose0[-1] + OFFSET + exp_conditions[i_exp][0]
            )
        
        trianglePose0 = rifttools.LibOVRPose(trianglePosition0)     # for origin and everything
        trianglePose = rifttools.LibOVRPose(trianglePosition)       # for fold
        
        
        
        # initialize thumbstick value
        adju_ang = rand_ang
        stopCurr = False
        
        cnt=0
        first_scene = True
        dim_flag = False
        scene_cnt = 0
        dim_cnt = 0
        dark_cnt = 0 # second view: normal => dim => dark => pole 
        dark_flag = False # second view: normal => dim => dark => pole 
        
        if not skip_black or play_sound:
            lasttime = blackscene(beep, hmd, redlight, metronome, play_sound, timediff, lasttime)
        
        lasttime = hmd.getPredictedDisplayTime()

        red_cnt_l = 0
        red_cnt_r = 0
        hit_left = True
        hit_right = False
        activate_cnt = 1

        last_l = 0
        last_r = 0
        target_side = -1
        flag_haptics = False

        while not stopCurr:            
            i_exp,results,stopCurr = check_rerun(i_exp,results,exp_conditions,stopCurr) # ===============> check rerun
            cnt += 1
                
            currenttime = hmd.getPredictedDisplayTime()
            state = hmd.getTrackingState(currenttime)
            headPose = state.headPose.thePose
            scene_head_pose = libovr.LibOVRPose(*headPose.posOri)
            if first_scene: # only has gain in the first scene
                scene_head_pose.pos[0] *= exp_conditions[i_exp][1]#-------gain
                
            hmd.calcEyePoses(scene_head_pose)
            
            
            if RECORD_LOG:
                local_log.append([headPose.pos[0], headPose.pos[1], headPose.pos[2]])
            
            
            # first scene
            
            hmd, first_scene, dim_cnt, dim_flag, dark_cnt, dark_flag, hit_left, hit_right, red_cnt_l, red_cnt_r = fold_scene(
                hmd, bino, headPose, redlight, stim_shutter,
                adju_ang, 
                WhiteTexture, BlackoutTexture, FloorTexture, trianglePose0, trianglePose,
                stim_origin, stim_aperture_low, stim_aperture_high, stim_aperture_left, stim_aperture_right,
                stim_floor_small, stim_left, stim_right, stim_line,
                skydark, sky, voro,
                dim_flag, dim_cnt, first_scene,
                dark_cnt, dark_flag,
                hit_left, hit_right, red_cnt_l, red_cnt_r,
                shutter_dict
                )
            
            
            if red_cnt_l == last_l and red_cnt_r == last_r:
                #print('[checking] {}'.format(currenttime - lasttime))
                if currenttime - lasttime > haptics_time:
                    flag_haptics = True
            
            if red_cnt_l > last_l:
                target_side = 0
                lasttime = currenttime
            elif red_cnt_r > last_r:
                target_side = 1
                lasttime = currenttime

            if target_side == 0 and red_cnt_r == last_r:
                if currenttime - lasttime > haptics_time:
                    flag_haptics = True
            if target_side == 1 and red_cnt_l == last_l:
                if currenttime - lasttime > haptics_time:
                    flag_haptics = True

            if flag_haptics:
                print('haptics')
                # add haptics
                hmd.startHaptics('RightTouch')
                flag_haptics = False
                lasttime = currenttime

            last_l = red_cnt_l
            last_r = red_cnt_r

            if event.getKeys('x') or hmd.shouldQuit or hmd.getButtons('Y', 'Touch', 'released')[0]:
                print(' ==> program stoped or finished')
                results.append([
                    abs(exp_conditions[i_exp][0]), exp_conditions[i_exp][1], exp_conditions[i_exp][2],
                    rand_ang, 0, 0
                    ])
                
                stopApp = True
                stopCurr = True
                
                if RECORD_LOG:
                    all_logs.append([i_exp, local_log])

            if red_cnt_l < activate_cnt and red_cnt_r < activate_cnt:
                continue
            # =============== event handling ==================
            if event.getKeys('q') or hmd.shouldQuit or hmd.getButtons('A', 'Touch', 'released')[0]:
                if play_sound:
                    stopCurr = True
                    metronome.stop(reset=True)
                    metronome.play()
                
                beep.stop(reset=True)
                beep.play()
                
                print('scene cnt %i' % scene_cnt)
                
                results.append([
                    abs(exp_conditions[i_exp][0]), exp_conditions[i_exp][1], exp_conditions[i_exp][2],
                    rand_ang, 0, 1 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    ])
                
                if RECORD_LOG:
                    all_logs.append([i_exp, local_log])
                
                skip_black = True
                first_scene = True
                i_exp += 1
                scene_cnt += 1

            elif event.getKeys('a') or hmd.shouldQuit or hmd.getButtons('B', 'Touch', 'released')[0]:
                if play_sound:
                    stopCurr = True
                    metronome.stop(reset=True)
                    metronome.play()
                
                beep.stop(reset=True)
                beep.play()
                
                print('scene cnt %i' % scene_cnt)
                
                results.append([
                    abs(exp_conditions[i_exp][0]), exp_conditions[i_exp][1], exp_conditions[i_exp][2],
                    rand_ang, 1, 0 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    ])
                
                if RECORD_LOG:
                    all_logs.append([i_exp, local_log])
                
                skip_black = True
                first_scene = True
                i_exp += 1
                scene_cnt += 1
                
            elif event.getKeys('c') or hmd.shouldRecenter or hmd.getButtons('X', 'Touch', 'released')[0]:
                #if not updated:
                        
                    pos0,ori0 = headPose.posOri
                    #ori0[-1]=1
                    
                    updated=libovr.LibOVRPose([0,0,0], ori=ori0)
                    libovr.specifyTrackingOrigin(updated)
                    #pos0.setIdentity()
                    
                    updated = True
                
            
    if stopApp:# and play_sound:
        metronome.stop(reset=True)
    
    print('Selected: %s' % selected_exp)
    
    return stopApp,results,metronome,all_logs

def check_rerun(i_exp,results,exp_conditions,stopCurr):
    if event.getKeys('r'): # ===========> rerun last experiment                
        if len(results)>=1:
            del results[-1]
            print('[warning] opt to rerun last experiment %s: [distance, gain, width] = [%s, %s, %s]' % (i_exp-1, *exp_conditions[i_exp-1][:3]))
            i_exp -= 1
            stopCurr = True
        else:
            print('[warning] cannot rerun at %s' % i_exp)
        
    return i_exp,results,stopCurr

#-------------------------


if __name__ == "__main__":
    
    #OUTPUT_FILE = r'output'
    #OUTPUT_PATH = r'.\output'
    #bino = False
    #n_repeat = 3
    TOTAL_EXP = 45
    
    myDlg = gui.Dlg(title="Fold Parallax")
    myDlg.addText('Participant info')
    # 0
    myDlg.addField('Name:', 'default')
    # 1
    myDlg.addField('# of Rounds:', 20)
    # 2
    myDlg.addText('Conditions')
    myDlg.addField('Stereo Condition:', choices=["bino", "mono"])
    # 3
    myDlg.addField('Motion Condition:', choices=["motion", "static"])
    # 4
    myDlg.addField('Texture Condition:', choices=["scaled", "constant"])
    # 5
    myDlg.addField('Width Condition:', choices=["scaled", "constant"])
    # 6
    myDlg.addText('Data')
    myDlg.addField('Output directory:', './output')
    # 7
    myDlg.addField('# of log:', 45)
    
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    
    if myDlg.OK:  # or if ok_data is not None
        stopApp = False
# =============================================================================
#         hmd = visual.Rift(samples=32, color=(-1, -1, -1), waitBlanking=False, 
#                           winType='glfw', #unit='norm',
#                           useLights=True)
# =============================================================================
        
        hmd = visual.Rift(samples=32, color=(-1, -1, -1), waitBlanking=False, 
                                  winType='glfw', #unit='norm',useLights=True
                                  )
        # currenttime0 = hmd.getPredictedDisplayTime()
        # state0 = hmd.getTrackingState(currenttime0)
        # headPose0 = state0.headPose.thePose
        # scene_head_pose0 = libovr.LibOVRPose(*headPose0.posOri).pos
        # print(scene_head_pose0)
        #shift_z = scene_head_pose[-1]
# =============================================================================
#         updated=libovr.LibOVRPose([0.4,0,-3.2])
#         libovr.specifyTrackingOrigin(updated)
# =============================================================================
        
        OUTPUT_FILE = r'{}'.format(ok_data[0])
        OUTPUT_PATH = r'{}'.format(ok_data[6])
        repeat = ok_data[1]
        
        ok_data[3] = "motion"
        if ok_data[2] in ["bino"]:
            bino = True
        else:
            bino = False
        
        if ok_data[3] in ["motion"]:
            play_sound = True
            
        else:
            play_sound = False
        
        if ok_data[4] in["constant"]:
            voros = ["voronoi_10","voronoi_10","voronoi_10"]
        else:
            voros = ["voronoi_10","voronoi_10","voronoi_10"]
        if ok_data[5] in["constant"]:
            widths = ["wide","wide","wide"]
        else:
            widths = ["narrow","middle","wide"]
        log_max = ok_data[7]
        
        #log_hdl = init_log(OUTPUT_PATH, OUTPUT_FILE, ok_data)

        metronome = Sound(r'.\audio\metronome.wav')
        stopApp, exp_results, metronome, all_logs = run_exp(metronome, hmd, bino, log_max,
                                                            TOTAL_EXP, play_sound, stopApp)
        
        year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
        time_str = '-'.join([str(year), expand_data(str(month)), expand_data(str(day)), expand_data(str(hour)), expand_data(str(minutes))])
        csv_hdl = init_output(time_str, OUTPUT_PATH, OUTPUT_FILE, ok_data)
        write2file25(csv_hdl, exp_results)
        log2file(time_str, all_logs,OUTPUT_PATH, OUTPUT_FILE, ok_data)
        
        
        metronome.stop(reset=True)
        hmd.close()
        core.quit()
        
    else:
        
        print('user cancelled')
        
    
