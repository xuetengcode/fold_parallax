"""

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
def red_wait(hmd, head_pos, eye, redlight, hit_left, hit_right, shake_cnt_l=0, shake_cnt_r=0):
    light_shift = 0.9
    shake_thr = 0.05
    if head_pos.pos[0] > shake_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
        if hit_left:
            shake_cnt_r += 1
            hit_right = True
            hit_left = False
    elif head_pos.pos[0] < -shake_thr and eye == 'left':
        redlight.pos = (-light_shift, 0.)
        redlight.draw(hmd)
        if hit_right:
            shake_cnt_l += 1
            hit_left = True
            hit_right = False
    return hmd, hit_left, hit_right, shake_cnt_l, shake_cnt_r

def red(hmd, head_pos, eye, redlight):
    light_shift = 0.9
    shake_thr = 0.05
    if head_pos.pos[0] > shake_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
    elif head_pos.pos[0] < -shake_thr and eye == 'left':
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

def render_plane(stim, hmd, textureDesc, trianglePose):
    sc = mathtools.scaleMatrix((1., 1., 1.0))
    rotation_mtx = mathtools.concatenate(
        [sc, trianglePose.getModelMatrix()], dtype=np.float32)

    rotation_mtx = arraytools.array2pointer(rotation_mtx)    
    hmd = render2hmd(stim, hmd, textureDesc, rotation_mtx)    
    return hmd

def render2hmd(stim, hmd, textureDesc, rotation_mtx):    
    hmd.draw3d = True
    GL.glPushMatrix()
    GL.glMultTransposeMatrixf(rotation_mtx)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, textureDesc.name)

    gltools.drawVAO(stim, GL.GL_TRIANGLES)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glDisable(GL.GL_TEXTURE_2D)
    GL.glPopMatrix()
    hmd.draw3d = False    
    return hmd

def create_aperture(y0=-0.3,y1=-3.):
    x = np.linspace(-3.0, 3.0, 3)
    y = np.linspace(y0, y1, 3)
    xx, yy = np.meshgrid(x, y)
    zz = np.tile(np.array([0.5, 0.5, 0.5]), (3, 1))

    vao = mtx2vao(xx, yy, zz)

    return vao

def create_floor():
    x = np.linspace(-2.0, 2.0, 3)
    z = np.linspace(-5.0, 3.0, 3)
    xx, zz = np.meshgrid(x, z)    
    yy = np.tile(np.array([0, 0, 0])-3, (3, 1))
    vao = mtx2vao(xx, yy, zz)
    return vao

def create_origin(yy0=-2.8): 
    x = np.linspace(-0.3, 0.3, 3)
    #z = np.linspace(1.55, 1.7, 3)
    z = np.linspace(1.55, 1.7, 3)
    xx, zz = np.meshgrid(x, z)
    
    yy = np.tile(np.array([yy0, yy0, yy0]), (3, 1))
    vao = mtx2vao(xx, yy, zz)

    return vao

def create_half_fold(shape='left'):
    if shape in ['left']:
        x = np.linspace(-1.0, 0.0, 2)
        y = np.linspace(1.0, -1.0, 2)
        xx, yy = np.meshgrid(x, y)
        zz = np.tile(np.array([-1, 0]), (2, 1))
    else:
        x = np.linspace(0.0, 1.0, 2)
        y = np.linspace(1.0, -1.0, 2)
        xx, yy = np.meshgrid(x, y)
        zz = np.tile(np.array([0, -1]), (2, 1))
        
    vao = mtx2vao(xx, yy, zz)
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
        
    return hmd, blacklight



# In[]
def gen_rotation_mtx(thumbVal, trianglePose):
    rotation = mathtools.rotationMatrix(thumbVal * 180 / math.pi, [0., 1., 0.]) # <<<<< rotation
    rotation_mtx = mathtools.concatenate(
                    [rotation, trianglePose.getModelMatrix()], dtype=np.float32)
    rotation_mtx = arraytools.array2pointer(rotation_mtx)
    
    return rotation_mtx

def check_dir(folder):
    if not os.path.isdir('output'):
        os.mkdir(folder)
    return

def init_output(OUTPUT_PATH, outfile_base, play_sound=True, additional=True):
    check_dir(OUTPUT_PATH)
    if additional:
        year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
        time_str = '-'.join([str(year), str(month), str(day), str(hour), str(minutes)])
    else:
        time_str = ''
    
    time_str += '_' + ok_data[2] + '_' + ok_data[3]
        
    output_file = '_'.join([outfile_base, time_str, os.path.basename(sys.argv[0])]) + r'.csv'
    csv_hdl = open(os.path.join(OUTPUT_PATH, output_file),'w')
    
    return csv_hdl

def wait4next(hmd, redlight, metronome, play_sound, timediff, lasttime):
    
    shake_cnt_l = 0
    shake_cnt_r = 0
    
    hit_left = True
    hit_right = False
    pass_cnt = 2
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
             hmd, hit_left, hit_right, shake_cnt_l, shake_cnt_r = red_wait(hmd, headPose, eye, redlight, hit_left, hit_right, shake_cnt_l, shake_cnt_r)    
         hmd.flip()
         
         if shake_cnt_l >= pass_cnt and shake_cnt_r >= pass_cnt:
             break
         
         if event.getKeys('q') or hmd.shouldQuit:
             break
         
         if not play_sound and hmd.getButtons('A', 'Touch', 'falling')[0]:
             break
 
    return lasttime
# In[]
def run_exp(hmd, csv_hdl, bino, play_sound=True, stopApp = False):
    
    IMG_PATH = r'.\images'
    img_path2 = r'.\images'
    
    
    all_gain = [1/2, 2/3, 4/5, 1, 5/4, 3/2, 2]
    all_distance = [1.3, 1.4, 1.5]
    #play_sound = True
    #depth_restriction = False
    timediff = 1
    #MAX_EXP = 30
    #-------- constant
    min_rotation = 0.005
    shuffle(all_gain)
    shuffle(all_distance)
    
    
    #--------------------------
    
    
    
    hmd.ambientLight = [0.5, 0.5, 0.5]
    # https://www.psychopy.org/api/visual/lightsource.html#psychopy.visual.LightSource
    #dirLight = LightSource(hmd, pos=(0., 1., 0.), ambientColor=(0.0, 1.0, 0.0), lightType='point')
    #hmd.lights = dirLight    
    redlight = visual.GratingStim(hmd, mask='gauss', size=2.0, tex=None, color='red', contrast=0.8, units='norm')
    redlight.setOpacity(1) # 0.5
    blacklight = visual.GratingStim(hmd, mask='gauss', size=3.0, tex=None, color=(0,0,0), contrast=0.8, units='norm')
    blacklight.setOpacity(0.8)
    
    stim_left = create_half_fold('left')
    stim_right = create_half_fold('right')
    stim_floor = create_floor()
    stim_aperture_low = create_aperture()
    stim_aperture_high = create_aperture(11.3, 0.3)
    stim_origin = create_origin()    

    textureDesc = gltools.createTexImage2dFromFile(
        r'{}'.format(os.path.join(IMG_PATH, 'voronoi_50.png')))
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
    sky = visual.SceneSkybox(hmd, (right_img, left_img, up_img, down_img, 
                                   back_img, front_img))    
    metronome = Sound(r'.\audio\output.wav')
    beep = Sound('C')
    nextRound = False
    
    exp_id = 0    
    print('==> Starting Experiment')        
    #while not nextRound and not stopApp and exp_id <= MAX_EXP:
        
        
    lasttime = hmd.getPredictedDisplayTime()
    for rand_pos in all_distance:
        # generate random position
        #rand_pos = -1*(random()*0.7+1.3)
        
        trianglePosition = (0., hmd.eyeHeight, rand_pos)
        trianglePose = rifttools.LibOVRPose(trianglePosition)    
        
        for gain in all_gain:
            if stopApp:
                break
            
            exp_id += 1
            rand_ang = math.pi * (15 + random()*25)/180 * positive_or_negative()
            print('==> New trial started')
            # thumbstick value
            thumbVal = rand_ang
            stopCurr = False
            adjustment_cnt = 0
            
            
            lasttime = wait4next(hmd, redlight, metronome, play_sound, timediff, lasttime)
            
            
            
            while not stopCurr:
                
                currenttime = hmd.getPredictedDisplayTime()
                state = hmd.getTrackingState(currenttime)
                headPose = state.headPose.thePose
                scene_head_pose = libovr.LibOVRPose(*headPose.posOri)
                scene_head_pose.pos[0] *= gain
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
                        hmd, blacklight = black(hmd, headPose, i, blacklight)
                        hmd.setRiftView()
                        #--------------- origin
                        hmd = render_plane(stim_origin, hmd, WhiteTexture, trianglePose)
                        #--------------- aperture
                        hmd = render_plane(stim_aperture_low, hmd, BlackoutTexture, trianglePose)
                        hmd = render_plane(stim_aperture_high, hmd, BlackoutTexture, trianglePose)
                        #--------------- floor
                        hmd = render_plane(stim_floor, hmd, FloorTexture, trianglePose)
                        #-------------- the left half prism
                        rotation_mtx = gen_rotation_mtx(thumbVal, trianglePose)
                        hmd = render2hmd(stim_left, hmd, textureDesc, rotation_mtx)
                        #-------------- the right half prism
                        rotation_mtx = gen_rotation_mtx(-thumbVal, trianglePose)
                        hmd = render2hmd(stim_right, hmd, textureDesc, rotation_mtx)
                        sky.draw()
                        #----------------------------------
                        hmd.setDefaultView()
                        hmd = red(hmd, headPose, i, redlight)
                        
                        GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
                hmd.flip()
                rawVal = hmd.getThumbstickValues(r'Touch', deadzone=True)[1]
                if rawVal[0] > 0.25:
                    thumbVal += min_rotation
                    adjustment_cnt += 1
                    
                elif rawVal[0] < -0.25:
                    thumbVal -= min_rotation
                    adjustment_cnt -= 1
                    
                if event.getKeys('q') or hmd.shouldQuit or hmd.getButtons('A', 'Touch', 'released')[0]:
                    print(' (Key stop by q)')
                    print('[log] Trial {}; Position: {}, rand_ang: {} (RAD), minimu rotation: {}, adjustment: {}, gain: {}'.format(
                            exp_id, rand_pos, rand_ang, min_rotation,
                            adjustment_cnt, gain
                            ))
                    
                    csv_hdl.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
                        exp_id, rand_pos, rand_ang, min_rotation,
                        adjustment_cnt, gain, bino
                        ))
                    
                    
                    stopCurr = True                                
                    
                    beep.stop(reset=True)
                    beep.play()
                elif event.getKeys('x') or hmd.shouldQuit or hmd.getButtons('B', 'Touch', 'released')[0]:
                    print(' program stop by x')
                    print('[log] Trial {}; Position: {}, rand_ang: {} (RAD), minimu rotation: {}, adjustment: {}, gain: {}'.format(
                            exp_id, rand_pos, rand_ang, min_rotation,
                            adjustment_cnt, gain
                            ))
                    
                    csv_hdl.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
                        exp_id, rand_pos, rand_ang, min_rotation,
                        adjustment_cnt, gain, bino
                        ))
                    
                    stopApp = True
                    stopCurr = True
                elif event.getKeys('r') or hmd.shouldRecenter:
                    hmd.recenterTrackingOrigin()
    
    return stopApp
    
if __name__ == "__main__":
    
    #OUTPUT_FILE = r'output'
    #OUTPUT_PATH = r'.\output'
    #bino = False
    #n_repeat = 3
        
    myDlg = gui.Dlg(title="Fold Parallax")
    myDlg.addText('Subject info')
    # 0
    myDlg.addField('Name:', 'default')
    # 1
    myDlg.addField('Total Session:', 3)
    # 2
    myDlg.addText('Conditions')
    myDlg.addField('Viewing Condition:', choices=["bino", "mono"])
    # 3
    myDlg.addField('Motion Condition:', choices=["motion", "static"])
    # 4
    myDlg.addText('Data')
    myDlg.addField('Output directory:', './output')
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    
    if myDlg.OK:  # or if ok_data is not None
        stopApp = False
        hmd = visual.Rift(samples=16, color=(-1, -1, -1), waitBlanking=False, 
                          winType='glfw', #unit='norm',
                          useLights=True)
        OUTPUT_FILE = r'{}'.format(ok_data[0])
        OUTPUT_PATH = r'{}'.format(ok_data[4])
        
        if ok_data[2] in ["bino"]:
            bino = True
        else:
            bino = False
        
        if ok_data[3] in ["motion"]:
            play_sound = True
        else:
            play_sound = False
        
        csv_hdl = init_output(OUTPUT_PATH, OUTPUT_FILE, ok_data)
        
        for i_repeat in range(ok_data[1]):
            if stopApp:
                break
            stopApp = run_exp(hmd, csv_hdl, bino, play_sound, stopApp)
        
        csv_hdl.close()
        hmd.close()
        core.quit()
        
    else:
        
        print('user cancelled')
        
    
    
        
    