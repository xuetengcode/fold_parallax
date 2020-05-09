"""

https://www.psychopy.org/general/units.html

"""
from psychopy import visual, event, core
from psychopy.tools import arraytools, rifttools
from psychopy.tools import gltools, mathtools
from psychopy.sound import Sound
import psychxr.libovr as libovr
import pyglet.gl as GL
import numpy as np

from random import random
import math
import os
from psychopy.visual import LightSource
# In[]
def red(hmd, head_pos, eye, redlight):
    light_shift = 0.9
    parallax_thr = 0.05
    if head_pos.pos[0] > parallax_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
    elif head_pos.pos[0] < -parallax_thr and eye == 'left':
        redlight.pos = (-light_shift, 0.)
        redlight.draw(hmd)
        #print('==> left eye')
    return hmd, redlight
def wait4next(hmd, redlight):
    while 1:
         currenttime = hmd.getPredictedDisplayTime()
         state = hmd.getTrackingState(currenttime)
         headPose = state.headPose.thePose    
         hmd.calcEyePoses(headPose)
             
         for eye in ('left', 'right'):
             hmd.setBuffer(eye)
             hmd.setDefaultView(clearDepth=True)
             hmd, redlight = red(hmd, headPose, eye, redlight)    
         hmd.flip()         
         if event.getKeys('q') or hmd.shouldQuit:
             break
         if hmd.getButtons('A', 'Touch', 'falling')[0]:
             break    
    return

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
    parallax = mathtools.concatenate(
        [sc, trianglePose.getModelMatrix()], dtype=np.float32)

    parallax = arraytools.array2pointer(parallax)    
    hmd = render2hmd(stim, hmd, textureDesc, parallax)    
    return hmd

def render2hmd(stim, hmd, textureDesc, parallax):    
    hmd.draw3d = True
    GL.glPushMatrix()
    GL.glMultTransposeMatrixf(parallax)
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

def black(hmd, head_pos, eye, blacklight, fr=-0.12, bk=0.05):
    #print(head_pos.pos)
    #print(head_pos.pos[2] > bk or head_pos.pos[2] < fr)
    if head_pos.pos[2] > bk or head_pos.pos[2] < fr:
        if eye == 'right':
            blacklight.pos = (head_pos.pos[0], head_pos.pos[1])
            blacklight.draw(hmd)
        elif eye == 'left':
            blacklight.pos = (head_pos.pos[0], head_pos.pos[1])
            blacklight.draw(hmd)
        
    return hmd, blacklight



# In[]
def parallax_matrix(thumbVal, trianglePose):
    rotation = mathtools.rotationMatrix(thumbVal * 180 / math.pi, [0., 1., 0.]) # <<<<< rotation
    parallax = mathtools.concatenate(
                    [rotation, trianglePose.getModelMatrix()], dtype=np.float32)
    parallax = arraytools.array2pointer(parallax)
    
    return parallax


# In[]
def main():
    IMG_PATH = r'./images'
    img_path2 = r'./images'
    mono = False
    gain = 1
    play_sound = True
    depth_restriction = False
    timediff = 1
    hmd = visual.Rift(samples=16, color=(-1, -1, -1), waitBlanking=False, 
                      winType='glfw', unit='norm',
                      useLights=True)
    
    hmd.ambientLight = [0.5, 0.5, 0.5]
    # https://www.psychopy.org/api/visual/lightsource.html#psychopy.visual.LightSource
    dirLight = LightSource(hmd, pos=(0., 1., 0.), ambientColor=(0.0, 1.0, 0.0), lightType='point')
    #hmd.lights = dirLight    
    redlight = visual.GratingStim(hmd, mask='gauss', size=1.0, tex=None, color='red', contrast=0.5, units='norm')
    redlight.setOpacity(0.2) # 0.5
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
    metronome = Sound(r'.\output.wav')    
    nextRound = False
    stopApp = False
    exp_id = 0    
    print('==> Starting Experiment')        
    while not nextRound and not stopApp and exp_id <= 5:
        exp_id += 1
        rand_pos = -1*(random()*0.7+1.3)        
        rand_ang = math.pi * (15 + random()*25)/180 * positive_or_negative()
        print('==> New trial started')
        trianglePosition = (0., hmd.eyeHeight, rand_pos)
        trianglePose = rifttools.LibOVRPose(trianglePosition)    
        # thumbstick value
        thumbVal = rand_ang
        stopCurr = False
        wait4next(hmd, redlight)
        cnt = 0
        lasttime = hmd.getPredictedDisplayTime()
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
                    #print(currenttime)
                    #print('Time diff {0:.5f}'.format(currenttime-lasttime))
                    lasttime = currenttime
                
            for i in ('left', 'right'):
                if i == 'left' and mono:
                    continue
                
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
                parallax = parallax_matrix(thumbVal, trianglePose)
                hmd = render2hmd(stim_left, hmd, textureDesc, parallax)
                #-------------- the right half prism
                parallax = parallax_matrix(-thumbVal, trianglePose)
                hmd = render2hmd(stim_right, hmd, textureDesc, parallax)
                sky.draw()
                #----------------------------------
                hmd.setDefaultView()
                hmd, redlight = red(hmd, headPose, i, redlight)
                
                GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
            hmd.flip()
            rawVal = hmd.getThumbstickValues(r'Touch', deadzone=True)[1]
            if rawVal[0] > 0.25:
                thumbVal += 0.005
                cnt += 1
                
            elif rawVal[0] < -0.25:
                thumbVal -= 0.005
                cnt -= 1
            if event.getKeys('q') or hmd.shouldQuit or hmd.getButtons('A', 'Touch', 'released')[0]:
                print(' (Key stop by q)')
                print('[log] Trial {}; Position: {}, rand_ang: {} (RAD), adjustment: {}'.format(
                        exp_id, rand_pos, rand_ang, cnt
                        ))
                stopCurr = True                                
                metronome.stop(reset=True)
                metronome.play()
            elif event.getKeys('x') or hmd.shouldQuit or hmd.getButtons('B', 'Touch', 'released')[0]:
                print(' program stop by x')
                print('[log] Trial {}; Position: {}, rand_ang: {} (RAD), adjustment: {}'.format(
                        exp_id, rand_pos, rand_ang, cnt
                        ))
                stopApp = True
                stopCurr = True
            elif event.getKeys('r') or hmd.shouldRecenter:
                hmd.recenterTrackingOrigin()
    hmd.close()
    core.quit()
if __name__ == "__main__":
    main()
