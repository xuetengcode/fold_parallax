"""
crashes when starting a new round
https://www.psychopy.org/general/units.html

"""
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
import csv
import time
import sys

# In[]
def red_activate(hmd, head_pos, eye, redlight, hit_left, hit_right, red_cnt_l=0, red_cnt_r=0):
    light_shift = 0.9
    parallax_thr = 0.05
    if head_pos.pos[0] > parallax_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
        if hit_left:
            red_cnt_r += 1
            hit_right = True
            hit_left = False
    elif head_pos.pos[0] < -parallax_thr and eye == 'left':
        redlight.pos = (-light_shift, 0.)
        redlight.draw(hmd)
        if hit_right:
            red_cnt_l += 1
            hit_left = True
            hit_right = False
    return hmd, hit_left, hit_right, red_cnt_l, red_cnt_r

def red(hmd, head_pos, eye, redlight):
    light_shift = 0.9
    parallax_thr = 0.05
    if head_pos.pos[0] > parallax_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
    elif head_pos.pos[0] < -parallax_thr and eye == 'left':
        redlight.pos = (-light_shift, 0.)
        redlight.draw(hmd)
            
    return hmd

def mtx2vao(xx, yy, zz):    
    vertices, textureCoords, normals, faces = \
        gltools.createMeshGridFromArrays(xx, yy, zz)
    vertexVBO = gltools.createVBO(vertices)
    texCoordVBO = gltools.createVBO(textureCoords)
    normalsVBO = gltools.createVBO(normals)
    indexBuffer = gltools.createVBO(
        faces.flatten(),
        target=GL.GL_ELEMENT_ARRAY_BUFFER,
        dataType=GL.GL_UNSIGNED_INT)
    vao = gltools.createVAO(
        {GL.GL_VERTEX_ARRAY: vertexVBO,
         GL.GL_TEXTURE_COORD_ARRAY: texCoordVBO,
         GL.GL_NORMAL_ARRAY: normalsVBO},
        indexBuffer=indexBuffer, legacy=True)    
    return vao

def render_plane(stim, hmd, voro, trianglePose):
    sc = mathtools.scaleMatrix((1., 1., 1.0))
    rotation_mtx = mathtools.concatenate(
        [sc, trianglePose.getModelMatrix()], dtype=np.float32)

    rotation_mtx = arraytools.array2pointer(rotation_mtx)    
    hmd = render2hmd(stim, hmd, voro, rotation_mtx)    
    return hmd

def render2hmd(stim, hmd, voro, rotation_mtx):    
    hmd.draw3d = True
    GL.glPushMatrix()
    GL.glMultTransposeMatrixf(rotation_mtx)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, voro.name)

    gltools.drawVAO(stim, GL.GL_TRIANGLES)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glDisable(GL.GL_TEXTURE_2D)
    GL.glPopMatrix()
    hmd.draw3d = False    
    return hmd

def create_aperture(y0=-0.3,y1=-3.):
    x_range = np.linspace(-3.0, 3.0, 3)
    y_range = np.linspace(y0, y1, 3)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.array([0.5, 0.5, 0.5]), (3, 1))

    vao = mtx2vao(x, y, z)

    return vao

def create_floor():
    x_range = np.linspace(-2.0, 2.0, 3)
    z_range = np.linspace(-1.0, 3.0, 3)
    x, z = np.meshgrid(x_range, z_range)    
    y = np.tile(np.array([0, 0, 0])-3, (3, 1))
    vao = mtx2vao(x, y, z)
    return vao

def create_origin(y0=-2.8): 
    x_range = np.linspace(-0.3, 0.3, 3)
    #z = np.linspace(1.55, 1.7, 3)
    z_range = np.linspace(1.55, 1.7, 3)
    x, z = np.meshgrid(x_range, z_range)
    
    y = np.tile(np.array([y0, y0, y0]), (3, 1))
    vao = mtx2vao(x, y, z)

    return vao

def create_half_fold(width, shape='left'):
    
    if shape in ['left']:
        x_range = np.linspace(-1*width, 0.0, 2)
        y_range = np.linspace(1.0, -1.0, 2)
        x, y = np.meshgrid(x_range, y_range)
        z = np.tile(np.array([-1*width, 0]), (2, 1))
    else:
        x_range = np.linspace(0.0, 1*width, 2)
        y_range = np.linspace(1.0, -1.0, 2)
        x, y = np.meshgrid(x_range, y_range)
        z = np.tile(np.array([0, -1*width]), (2, 1))
        
    vao = mtx2vao(x, y, z)
    return vao

def positive_or_negative():
    if random() < 0.5:
        return 1
    else:
        return -1    

def black(hmd, head_pos, eye, blacklight, fr=3., bk=3.1): # fr=-0.12, bk=0.05
    #print(head_pos.pos)
    #print(head_pos.pos[2] > bk)
    #print(head_pos.pos[2] < fr)
    if head_pos.pos[2] > bk or head_pos.pos[2] < fr:
        if eye == 'right':
            blacklight.pos = (head_pos.pos[0], head_pos.pos[1])
            blacklight.draw(hmd)
        elif eye == 'left':
            blacklight.pos = (head_pos.pos[0], head_pos.pos[1])
            blacklight.draw(hmd)
        dimming = True
    else:
        dimming = False
    return hmd, blacklight, dimming



# In[]
def gen_rotation_mtx(input_ang, trianglePose):
    rotation = mathtools.rotationMatrix(input_ang * 180 / math.pi, [0., 1., 0.]) # <<<<< rotation
    rotation_mtx = mathtools.concatenate(
                    [rotation, trianglePose.getModelMatrix()], dtype=np.float32)
    rotation_mtx = arraytools.array2pointer(rotation_mtx)
    
    return rotation_mtx

def check_dir(folder):
    if not os.path.isdir('output'):
        os.mkdir(folder)
    return

def expand_data(invar):
    
    if len(invar)==1:
        invar = '0'+invar
    return invar

def init_output(OUTPUT_PATH, outfile_base, play_sound=True, additional=True):
    check_dir(OUTPUT_PATH)
    if additional:
        year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
        time_str = '-'.join([str(year), expand_data(str(month)), expand_data(str(day)), expand_data(str(hour)), expand_data(str(minutes))])
    else:
        time_str = ''
    
    time_str += '_' + ok_data[2] + '_' + ok_data[3] +  '_' + ok_data[4]+  '_' + ok_data[5]
        
    output_file = '_'.join([outfile_base, time_str, os.path.basename(sys.argv[0])]) + r'.csv'
    csv_hdl = open(os.path.join(OUTPUT_PATH, output_file),'w')
    
    return csv_hdl

def blackscene(hmd, redlight, metronome, play_sound, timediff, lasttime):
    
    red_cnt_l = 0
    red_cnt_r = 0
    
    hit_left = True
    hit_right = False
    activate_cnt = 1
    
    while 1:
         currenttime = hmd.getPredictedDisplayTime()
         if play_sound:
             if abs(currenttime - lasttime - timediff) < 0.01 and currenttime-lasttime > 0.1 or abs(currenttime - lasttime - timediff) >10:
                metronome.stop(reset=True)
                metronome.play()
                lasttime = currenttime
                
         state = hmd.getTrackingState(currenttime)
         headPose = state.headPose.thePose    
         hmd.calcEyePoses(headPose)
         
         
         for eye in ('left', 'right'):
             hmd.setBuffer(eye)
             hmd.setDefaultView(clearDepth=True)
             hmd, hit_left, hit_right, red_cnt_l, red_cnt_r = red_activate(hmd, headPose, eye, redlight, hit_left, hit_right, red_cnt_l, red_cnt_r)    
         hmd.flip()
         
         if red_cnt_l >= activate_cnt and red_cnt_r >= activate_cnt and play_sound:
             break
         
         if event.getKeys('n') or hmd.shouldQuit:
             break
         
         if not play_sound and hmd.getButtons('A', 'Touch', 'falling')[0]:
         #if hmd.getButtons('A', 'Touch', 'falling')[0]:
             break
         if event.getKeys('r'): # get rid of multiple triggering
             continue
    return lasttime
# In[]
def run_exp(hmd, bino, results, play_sound=True, stopApp = False):
    
    IMG_PATH = r'.\images'
    img_path2 = r'.\images'
    
    if ok_data[3] in ["motion"]:
        all_gain = [1/2, 2/3, 4/5, 1, 5/4, 3/2, 2]
    else:
        all_gain = [1, 1, 1, 1, 1, 1, 1]
    if ok_data[5] in ["constant"]:
        all_width_shuffle = [1., 1., 1.]
    else:
        all_width_shuffle = [1., 1.125, 1.25]
    all_distance = [1.3, 1.4, 1.5]
    all_width = [1, 1.125, 1.25]
    exp_conditions = []
    
    for i_g in range(len(all_gain)):
        shuffle(all_width_shuffle)
        for i_d in range (len(all_distance)):
            voro_distance = voros[i_d]
            voro_width = widths[all_width.index(all_width_shuffle[i_d])]
            voro_str = voro_distance + '_' + voro_width + ".png"
            voro = gltools.createTexImage2dFromFile(r'{}'.format(os.path.join(IMG_PATH, voro_str)))            
            left = create_half_fold(all_width_shuffle[i_d],'left')
            right = create_half_fold(all_width_shuffle[i_d],'right')
            exp_conditions.append([all_distance[i_d], all_gain[i_g], all_width_shuffle[i_d], left, right, voro])
    shuffle(exp_conditions)

    #play_sound = True
    #depth_restriction = False
    timediff = 1
    #MAX_EXP = 30
    #-------- constant
    min_rotation = 0.005
    #shuffle(all_gain)
    #shuffle(all_distance)
    
    
    #--------------------------
    
    
    
    #hmd.ambientLight = [0.5, 0.5, 0.5]
    # https://www.psychopy.org/api/visual/lightsource.html#psychopy.visual.LightSource
    #dirLight = LightSource(hmd, pos=(0., 1., 0.), ambientColor=(0.0, 1.0, 0.0), lightType='point')
    #hmd.lights = dirLight    
    redlight = visual.GratingStim(hmd, mask='gauss', size=1.0, tex=None, color='red', contrast=0.5, units='norm')
    redlight.setOpacity(1) # 0.5
    blacklight = visual.GratingStim(hmd, mask='gauss', size=3.0, tex=None, color=(0,0,0), contrast=0.8, units='norm')
    blacklight.setOpacity(0.8)
    
# =============================================================================
#     stim_left = create_half_fold('left')
#     stim_right = create_half_fold('right')
# =============================================================================
    stim_floor = create_floor()
    stim_aperture_low = create_aperture()
    stim_aperture_high = create_aperture(11.3, 0.3)
    stim_origin = create_origin()    

# =============================================================================
#     voro_big = gltools.createTexImage2dFromFile(r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.png')))
#     voro_middle = gltools.createTexImage2dFromFile(
#         r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.1.png')))
#     voro_small = gltools.createTexImage2dFromFile(
#         r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.2.png')))
# =============================================================================
    
    FloorTexture = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'diffus.png')))
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
    metronome = Sound(r'.\audio\output.wav')
    beep = Sound('C')
    nextRound = False
    
    #exp_id = 0    
    print('==> Starting a new round')        
    #while not nextRound and not stopApp and exp_id <= MAX_EXP:
    
        

        
    lasttime = hmd.getPredictedDisplayTime()
    i_exp = 0
    last_angle = 0
    while i_exp < len(exp_conditions):
    #for i_exp in range(len(exp_conditions)):
    
        print('[debug info] %s: [distance, gain, width] = [%s, %s, %s, %s, %s, %s]' % (i_exp, *exp_conditions[i_exp]))
        
        stim_left = exp_conditions[i_exp][3]
        stim_right = exp_conditions[i_exp][4]
        voro = exp_conditions[i_exp][5]
        trianglePosition = (0., hmd.eyeHeight, exp_conditions[i_exp][0])
        trianglePose = rifttools.LibOVRPose(trianglePosition)    
        
        
        if stopApp:
            break
        
        #exp_id += 1
        rand_ang = math.pi * (15 + random()*25)/180 * positive_or_negative()
        
        # thumbstick value
        adju_ang = rand_ang
        stopCurr = False
        adjustment_cnt = 0
        
        
        lasttime = blackscene(hmd, redlight, metronome, play_sound, timediff, lasttime)
        
        
        
        while not stopCurr:
            i_exp,results,stopCurr = check_rerun(i_exp,results,exp_conditions,stopCurr) # ===============> check rerun
            
                
            currenttime = hmd.getPredictedDisplayTime()
            state = hmd.getTrackingState(currenttime)
            headPose = state.headPose.thePose
            scene_head_pose = libovr.LibOVRPose(*headPose.posOri)
            scene_head_pose.pos[0] *= exp_conditions[i_exp][1]
            hmd.calcEyePoses(scene_head_pose)            
            if play_sound:
                #print('Time diff {0:.3f}'.format(currenttime-lasttime))
                if abs(currenttime - lasttime - timediff) < 0.01 and currenttime-lasttime > 0.1:
                    metronome.stop(reset=True)
                    metronome.play()
                    #print('Time diff {0:.5f}'.format(currenttime-lasttime))
                    lasttime = currenttime
                
            for i in ('left', 'right'):
                if i == 'left' and not bino:
                    hmd.setBuffer(i)
                    hmd.setRiftView()
                    
                    #----------------------------------
                    hmd.setDefaultView()
                    hmd = red(hmd, headPose, i, redlight)
                    
                    GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
                else:
                        
                    hmd.setBuffer(i)
                    hmd, blacklight, dimming = black(hmd, headPose, i, blacklight)
                    hmd.setRiftView()
                    #--------------- origin
                    hmd = render_plane(stim_origin, hmd, WhiteTexture, trianglePose)
                    #--------------- aperture
                    hmd = render_plane(stim_aperture_low, hmd, BlackoutTexture, trianglePose)
                    hmd = render_plane(stim_aperture_high, hmd, BlackoutTexture, trianglePose)
                    #--------------- floor
                    hmd = render_plane(stim_floor, hmd, FloorTexture, trianglePose)
                    #-------------- the left half prism
                    rotation_mtx = gen_rotation_mtx(adju_ang, trianglePose)
                    hmd = render2hmd(stim_left, hmd, voro, rotation_mtx)
                    #-------------- the right half prism
                    rotation_mtx = gen_rotation_mtx(-adju_ang, trianglePose)
                    hmd = render2hmd(stim_right, hmd, voro, rotation_mtx)
                    if dimming:
                        skydark.draw()
                    else:
                        sky.draw()
                    #----------------------------------
                    hmd.setDefaultView()
                    hmd = red(hmd, headPose, i, redlight)
                    
                    GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
                    
            hmd.flip()
            rawVal = hmd.getThumbstickValues(r'Touch', deadzone=True)[1]
            if rawVal[0] > 0.25:
                adju_ang += min_rotation
                adjustment_cnt += 1
                
            elif rawVal[0] < -0.25:
                adju_ang -= min_rotation
                adjustment_cnt -= 1
            
            
            if event.getKeys('q') or hmd.shouldQuit or hmd.getButtons('A', 'Touch', 'released')[0]:
                results.append([adju_ang, exp_conditions[i_exp][0], rand_ang, min_rotation,
                    adjustment_cnt, exp_conditions[i_exp][1], exp_conditions[i_exp][2]
                    ])
                
                last_angle = rand_ang
                stopCurr = True
                
                beep.stop(reset=True)
                beep.play()
                
                i_exp += 1
                
            elif event.getKeys('x') or hmd.shouldQuit or hmd.getButtons('B', 'Touch', 'released')[0]:
                print(' ==> program stoped or finished')
                results.append([adju_ang, exp_conditions[i_exp][0], rand_ang, min_rotation,
                    adjustment_cnt, exp_conditions[i_exp][1], exp_conditions[i_exp][2]
                    ])
                
                stopApp = True
                stopCurr = True
                
            elif event.getKeys('c') or hmd.shouldRecenter:
                pos0,ori0 = headPose.posOri
                
                updated=libovr.LibOVRPose(pos=(0,pos0[1],-1), ori=ori0)
                
                libovr.specifyTrackingOrigin(updated)
                #pos0.setIdentity()
            
            
            
            
    return stopApp,results

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

def write2file(csvhdl,data):
    
    for ir in range(len(data)):
        curr_data = data[ir]
        csvhdl.write('{}, {}, {}, {}, {}, {}, {}\n'.format(*curr_data))
    
    csvhdl.close()
    
    return

if __name__ == "__main__":
    
    #OUTPUT_FILE = r'output'
    #OUTPUT_PATH = r'.\output'
    #bino = False
    #n_repeat = 3
        
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
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    
    if myDlg.OK:  # or if ok_data is not None
        stopApp = False
        hmd = visual.Rift(samples=32, color=(-1, -1, -1), waitBlanking=False, 
                          winType='glfw', #unit='norm',
                          useLights=True)
        OUTPUT_FILE = r'{}'.format(ok_data[0])
        OUTPUT_PATH = r'{}'.format(ok_data[6])
        
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
            voros = ["voronoi_50.1","voronoi_50.2","voronoi_50"]
        if ok_data[5] in["constant"]:
            widths = ["wide","wide","wide"]
        else:
            widths = ["narrow","middle","wide"]   
        csv_hdl = init_output(OUTPUT_PATH, OUTPUT_FILE, ok_data)
        
        exp_results = []
        for i_repeat in range(ok_data[1]):
            if stopApp:
                break
            stopApp, exp_results = run_exp(hmd, bino, exp_results, play_sound, stopApp)
        
        write2file(csv_hdl, exp_results)
        hmd.close()
        core.quit()
        
    else:
        
        print('user cancelled')
        
    
