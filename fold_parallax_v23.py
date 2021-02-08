"""
crashes when starting a new round
https://www.psychopy.org/general/units.html

"""
import psychopy
import time
from psychopy import gui
from psychopy import visual, event, core
from psychopy.tools import arraytools, rifttools
from psychopy.tools import gltools, mathtools
from psychopy.sound import Sound
import psychxr.libovr as libovr
import pyglet.gl as GL
import numpy as np

from random import random, shuffle
import math
import os
from psychopy.visual import LightSource

from subfunctions.general import (
    write2file, init_output, log2file, expand_data
    )
from subfunctions.objects import (
    create_half_fold, red_activate, positive_or_negative, 
    render_plane, render2hmd, gen_offset_mtx,
    create_floor, create_aperture, create_origin, create_central_line, create_shutter, creat_pole,
    red, distance_restriction, dim_scene
    )
from subfunctions.scenes import fold_scene, pole_scene

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

def gen_pole_pos(pole_close, pole_far):#, cond):
    # generate randome position
    rand = random()
    rand_pos = pole_close - (pole_close - pole_far) * rand
    #pole_far = floor_far # floor end
    #pole_close = origin_line - 2
    #rand_pole = pole_far + (pole_ed- pole_far) * random()
# =============================================================================
#     if cond in ['far']:
#         rand_pos = pole_close - 2 * rand
#     else:
#         rand_pos = pole_close - (pole_close - pole_far) * rand
# =============================================================================
    
    return rand_pos
# In[]
def run_exp(metronome, hmd, bino, SEL,
            TOTAL_EXP=63, play_sound=True, stopApp=False, scene_head_pose0=[0,0,0]):
    
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
    else:
        all_gain = [1]
    if ok_data[5] in ["constant"]:
        all_width = [1., 1., 1.]
    else:
        all_width = [1., 1.125, 1.25]
    all_distance = [-1.3, -1.4, -1.5]
    exp_conditions = []
    for i_w in range(ok_data[1]):
        for i_g in range(len(all_gain)):
            #shuffle(all_width_shuffle)
            for i_d in range (len(all_distance)):
                voro_distance = voros[i_d]
                voro_width = widths[i_w]
                voro_str = voro_distance + '_' + voro_width + ".png"
                voro = gltools.createTexImage2dFromFile(r'{}'.format(os.path.join(IMG_PATH, voro_str)))
                left = create_half_fold(all_width[i_w],'left')
                right = create_half_fold(all_width[i_w],'right')                
                exp_conditions.append([all_distance[i_d], all_gain[i_g], all_width[i_w], left, right, voro])
    shuffle(exp_conditions)
    
    texture_pole = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'stripes_pole.jpg'))
        )
    
    #play_sound = True
    #depth_restriction = False
    timediff = 1
    #MAX_EXP = 30
    #-------- constant
    min_rotation = 0.005
    min_move = 0.01
    #shuffle(all_gain)
    #shuffle(all_distance)
    
    #---------------------- set world parameters
    floor_far = -8.5
    floor_close = 1.5
    origin_line = 0
    pole_con1_far = origin_line - 4#floor_far # floor end
    pole_con1_close = origin_line - 2
    
    pole_con2_close = origin_line - 0.5
    pole_con2_far = origin_line - 0.8
    #--------------------------
    
    #hmd.ambientLight = [0.5, 0.5, 0.5]
    # https://www.psychopy.org/api/visual/lightsource.html#psychopy.visual.LightSource
    #dirLight = LightSource(hmd, pos=(0., 1., 0.), ambientColor=(0.0, 1.0, 0.0), lightType='point')
    #hmd.lights = dirLight    
    redlight = visual.GratingStim(hmd, mask='gauss', size=1.0, tex=None, color='red', contrast=0.5, units='norm')
    redlight.setOpacity(1) # 0.5
    
    #blacklight = visual.GratingStim(hmd, size=3.0, tex=None, color=(0,0,0), contrast=0, units='norm')
    #stim_shutter = visual.GratingStim(hmd, mask='gauss', size=3.0, tex=None, color=(0,0,0), contrast=0.8, units='norm')
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
    
    
    #stim_shutter.thePose.setOriAxisAngle((1, 0, 0), -90.0)
    
    #stim_shutter.opacity = 0.8
# =============================================================================
#     wallStim = visual.PlaneStim(hmd, size=(5, 5), pos=(0, 2.5, -4.0),  
#                          useShaders=False, useMaterial=wallMaterial)
# =============================================================================
# =============================================================================
#     stim_left = create_half_fold('left')
#     stim_right = create_half_fold('right')
# =============================================================================
    stim_floor_big = create_floor(z_far=floor_far, z_close=floor_close)
    stim_floor_small = create_floor(z_far=-1, z_close=5)
    stim_aperture_low = create_aperture()
    stim_aperture_high = create_aperture(10, 0.2)
    stim_origin = create_origin(z0=origin_line)
    stim_line = create_central_line()
    
    #stim_pole = create_central_line(-0.05, 0.05)
    stim_pole = creat_pole()
# =============================================================================
#     voro_big = gltools.createTexImage2dFromFile(r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.png')))
#     voro_middle = gltools.createTexImage2dFromFile(
#         r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.1.png')))
#     voro_small = gltools.createTexImage2dFromFile(
#         r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.2.png')))
# =============================================================================
    
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
    last_angle = 0
    last_pole_pos = 0
    updated = False
    skip_black = False
    while i_exp < len(exp_conditions):
    #for i_exp in range(len(exp_conditions)):
        local_log = []
        if i_exp in selected_exp:
            RECORD_LOG = True
        else:
            RECORD_LOG = False
            
        print('[debug info] Exp %s: [distance, gain, width] = [%s, %s, %s]' % (i_exp, *exp_conditions[i_exp][:3]))
        
        stim_left = exp_conditions[i_exp][3]
        stim_right = exp_conditions[i_exp][4]
        voro = exp_conditions[i_exp][5]
        
        
        if stopApp:
            break
  
        #exp_id += 1
        rand_ang = math.pi * (15 + random()*25)/180 * positive_or_negative()
        
        
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
        adjustment_cnt = 0
        adju_pole = 0
        adjustment_cnt_pole = 0
        
        cnt=0
        zero_scene = False
        first_scene = True
        dim_flag = False
        scene_cnt = 0
        dim_cnt = 0
        dark_cnt = 0 # second view: normal => dim => dark => pole 
        dark_flag = False # second view: normal => dim => dark => pole 
        
        if not skip_black or play_sound:
            lasttime = blackscene(beep, hmd, redlight, metronome, play_sound, timediff, lasttime)
            
        while not stopCurr:
            if zero_scene and not play_sound:
                lasttime = blackscene(beep, hmd, redlight, metronome, play_sound, timediff, lasttime, True)
                stopCurr = True
                break
            
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
            if first_scene and not zero_scene:
                
        
                hmd, first_scene, dim_cnt, dim_flag, dark_cnt, dark_flag = fold_scene(
                    hmd, bino, headPose, redlight, stim_shutter,
                    adju_ang, 
                    WhiteTexture, BlackoutTexture, FloorTexture, trianglePose0, trianglePose,
                    stim_origin, stim_aperture_low, stim_aperture_high, 
                    stim_floor_small, stim_left, stim_right, stim_line,
                    skydark, sky, voro,
                    dim_flag, dim_cnt, first_scene,
                    dark_cnt, dark_flag,
                    shutter_dict
                    )
                rawVal = hmd.getThumbstickValues(r'Touch', deadzone=True)[1]
                
                if not first_scene:
                    rand = random()
                    if rand>0.5:
                        rand_pole = gen_pole_pos(pole_con1_close, pole_con1_far)#, 'far')
                    else:
                        rand_pole = gen_pole_pos(pole_con2_close, pole_con2_far)#, 'close')
                    
                    
                if rawVal[0] > 0.25:
                    adju_ang += min_rotation
                    adjustment_cnt += 1
                    
                elif rawVal[0] < -0.25:
                    adju_ang -= min_rotation
                    adjustment_cnt -= 1
            else:
                dim_cnt = 0
                # second scene
                
                #pole_shift = exp_conditions[i_exp][0] + adju_pole
# =============================================================================
#                 print('rand %.3f, all %.3f' % (rand_pole, 
#                                                scene_head_pose0[-1] + OFFSET + rand_pole + adju_pole))
# =============================================================================
                #trianglePosition0 = (
                #    scene_head_pose0[0], hmd.eyeHeight, 
                #    scene_head_pose0[-1] + OFFSET
                #    )
                metronome.stop(reset=True)
        
                trianglePosition_pole = (
                    scene_head_pose0[0], hmd.eyeHeight, 
                    scene_head_pose0[-1] + OFFSET + rand_pole + adju_pole
                    )
                trianglePose_pole = rifttools.LibOVRPose(trianglePosition_pole)       # for pole
                
                hmd = pole_scene(
                    hmd, headPose, redlight,
                    stim_origin, stim_floor_big, stim_pole, stim_shutter,
                    WhiteTexture, FloorTexture, texture_pole, 
                    trianglePose_pole, trianglePose0,
                    sky, dim_flag, shutter_dict_pole
                    )
                        
                hmd.flip()
                rawVal = hmd.getThumbstickValues(r'Touch', deadzone=True)[1]
                if rawVal[1] > 0.25:
                    if scene_head_pose0[-1] + OFFSET + rand_pole + adju_pole > -4:
                        adju_pole -= min_move
                        adjustment_cnt_pole += 1
                    
                elif rawVal[1] < -0.25:
                    if scene_head_pose0[-1] + OFFSET + rand_pole + adju_pole < -0.5:
                        adju_pole += min_move
                        adjustment_cnt_pole -= 1
                
                last_pole_pos = OFFSET + rand_pole + adju_pole
                
            # =============== event handling ==================
            if event.getKeys('q') or hmd.shouldQuit or hmd.getButtons('A', 'Touch', 'released')[0]:
                skip_black = True
                print('scene cnt %i' % scene_cnt)
                if scene_cnt % 2 == 0:
                    #first_scene = False
                    dim_flag = True
                    dim_cnt = 0
                    beep.stop(reset=True)
                    beep.play()
                else:
                    zero_scene = True
                    first_scene = True
                    #
                    
                    if play_sound:
                        stopCurr = True
                        metronome.stop(reset=True)
                        metronome.play()
                    results.append([
                        adju_ang, abs(exp_conditions[i_exp][0]), 
                        rand_ang, min_rotation,
                        adjustment_cnt, exp_conditions[i_exp][1], exp_conditions[i_exp][2],
                        adjustment_cnt_pole, min_move, last_pole_pos
                        ])
                    
                    last_angle = rand_ang
                    
                    beep.stop(reset=True)
                    beep.play()
                    
                    if RECORD_LOG:
                        all_logs.append([i_exp, local_log])
                
                    i_exp += 1
                
                scene_cnt += 1
                
            elif event.getKeys('x') or hmd.shouldQuit or hmd.getButtons('B', 'Touch', 'released')[0]:
                print(' ==> program stoped or finished')
                results.append([
                    adju_ang, abs(exp_conditions[i_exp][0]), 
                    rand_ang, min_rotation,
                    adjustment_cnt, exp_conditions[i_exp][1], exp_conditions[i_exp][2],
                    adjustment_cnt_pole, min_move, last_pole_pos
                    ])
                
                stopApp = True
                stopCurr = True
                
                if RECORD_LOG:
                    all_logs.append([i_exp, local_log])
                    
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
    TOTAL_EXP = 63
    
    myDlg = gui.Dlg(title="Fold Parallax")
    myDlg.addText('Participant info')
    # 0
    myDlg.addField('Name:', 'default')
    # 1
    myDlg.addField('# of Rounds:', 3)
    # 2
    myDlg.addText('Conditions')
    myDlg.addField('Stereo Condition:', choices=["bino", "mono"])
    # 3
    myDlg.addField('Motion Condition:', choices=["static", "motion"])
    # 4
    myDlg.addField('Texture Condition:', choices=["scaled", "constant"])
    # 5
    myDlg.addField('Width Condition:', choices=["scaled", "constant"])
    # 6
    myDlg.addText('Data')
    myDlg.addField('Output directory:', './output')
    # 7
    myDlg.addField('# of log:', 63)
    
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    
    if myDlg.OK:  # or if ok_data is not None
        stopApp = False
        hmd = visual.Rift(samples=32, color=(-1, -1, -1), waitBlanking=False, 
                          winType='glfw', #unit='norm',
                          useLights=True)
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
        if ok_data[2] in ["bino"]:
            bino = True
        else:
            bino = False
        
        if ok_data[3] in ["motion"]:
            play_sound = True
            
        else:
            play_sound = False
        if ok_data[4] in["constant"]:
            voros = ["voronoi_50","voronoi_50","voronoi_50"]
        else:
            voros = ["voronoi_50.2","voronoi_50.1","voronoi_50"]
        if ok_data[5] in["constant"]:
            widths = ["wide","wide","wide"]
        else:
            widths = ["narrow","middle","wide"]
        log_max = ok_data[7]
        
        #log_hdl = init_log(OUTPUT_PATH, OUTPUT_FILE, ok_data)
# =============================================================================
#         for i_repeat in range(ok_data[1]):
# =============================================================================
        metronome = Sound(r'.\audio\metronome.wav')
        stopApp, exp_results, metronome, all_logs = run_exp(metronome, hmd, bino, log_max,
                                                            TOTAL_EXP, play_sound, stopApp)
        
        year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
        time_str = '-'.join([str(year), expand_data(str(month)), expand_data(str(day)), expand_data(str(hour)), expand_data(str(minutes))])
        csv_hdl = init_output(time_str, OUTPUT_PATH, OUTPUT_FILE, ok_data)
        write2file(csv_hdl, exp_results)
        log2file(time_str, all_logs,OUTPUT_PATH, OUTPUT_FILE, ok_data)
        
        
        metronome.stop(reset=True)
        hmd.close()
        core.quit()
        
    else:
        
        print('user cancelled')
        
    
