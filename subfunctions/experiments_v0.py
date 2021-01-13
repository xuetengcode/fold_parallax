# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 14:24:05 2020

@author: Xue
"""
from random import random
from psychopy.tools import arraytools
from psychopy.tools import gltools, mathtools
import pyglet.gl as GL
import numpy as np
import math
# In[]

def render_plane(stim, hmd, voro, trianglePose):
    sc = mathtools.scaleMatrix((1., 1., 1.0))
    offset_mtx = mathtools.concatenate(
        [sc, trianglePose.getModelMatrix()], dtype=np.float32)

    offset_mtx = arraytools.array2pointer(offset_mtx)
    # to hmd
    hmd = render2hmd(stim, hmd, voro, offset_mtx)    
    return hmd

def gen_offset_mtx(input_ang, trianglePose):
    # rotation mtx for two folds, need to call render2hmd separately
    rotation = mathtools.rotationMatrix(input_ang * 180 / math.pi, [0., 1., 0.]) # <<<<< rotation
    offset_mtx = mathtools.concatenate(
                    [rotation, trianglePose.getModelMatrix()], dtype=np.float32)
    offset_mtx = arraytools.array2pointer(offset_mtx)
    # call render2hmd later
    return offset_mtx

def render2hmd(stim, hmd, voro, offset_mtx):    
    hmd.draw3d = True
    GL.glPushMatrix()
    GL.glMultTransposeMatrixf(offset_mtx)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, voro.name)

    gltools.drawVAO(stim, GL.GL_TRIANGLES)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glDisable(GL.GL_TEXTURE_2D)
    GL.glPopMatrix()
    hmd.draw3d = False    
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

def create_central_line(xs=-0.001, xe=0.001):    
    x_range = np.linspace(xs, xe, 2)
    y_range = np.linspace(2, -2, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.array([0, 0]), (2, 1))
        
    vao = mtx2vao(x, y, z)
    return vao

def create_floor(z_far=-10.0, z_close=3):
# =============================================================================
#     z_range = np.linspace(-1.0, 3.0, 3)
# =============================================================================
    x_range = np.linspace(-6.5, 6.5, 3)
    z_range = np.linspace(z_far, z_close, 3)
    x, z = np.meshgrid(x_range, z_range)    
    y = np.tile(np.array([0, 0, 0])-2.2, (3, 1))
    vao = mtx2vao(x, y, z)
    return vao

def create_origin(y0=-2.15,z0=0): 
    x_range = np.linspace(-0.3, 0.3, 2)
    #z = np.linspace(1.55, 1.7, 3)
    z_range = np.linspace(z0-0.05, z0+0.05, 2)
    x, z = np.meshgrid(x_range, z_range)
    
    y = np.tile(np.array([y0, y0]), (2, 1))
    vao = mtx2vao(x, y, z)

    return vao

def create_half_fold(width, shape='left'):
    
    if shape in ['left']:
        x_range = np.linspace(-1.0*width, 0.0, 2)
        y_range = np.linspace(2, -2, 2)
        x, y = np.meshgrid(x_range, y_range)
        z = np.tile(np.array([-1.0*width, 0]), (2, 1))
    else:
        x_range = np.linspace(0.0, 1.0*width, 2)
        y_range = np.linspace(2, -2, 2)
        x, y = np.meshgrid(x_range, y_range)
        z = np.tile(np.array([0, -1.0*width]), (2, 1))
        
    vao = mtx2vao(x, y, z)
    return vao

def create_aperture(y0=-0.35,y1=-2.8):
    x_range = np.linspace(-3.0, 3.0, 2)
    y_range = np.linspace(y0, y1, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.array([-0.8, -0.8]), (2, 1))

    vao = mtx2vao(x, y, z)

    return vao

def create_shutter(y0=-2.19,y1=10):
    x_range = np.linspace(-10.0, 10.0, 2)
    y_range = np.linspace(y0, y1, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.array([-0.6, -0.6]), (2, 1))

    vao = mtx2vao(x, y, z)

    return vao

def creat_pole(y_st=-2.79, y_ed=0.2, center=[0,0], radius=0.025):
    
    # x_range, z_range = make_circle(1, [0,0])
    # x, z = np.meshgrid(x_range, z_range)
    # y = np.tile(np.ones(len(x_range)), (len(x_range), 1))
    
    x_range, z_range = make_circle(radius, center)
    y_range = np.linspace(y_st, y_ed, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.squeeze(z_range), (2, 1))
    vao = mtx2vao(x, y, z)
    
    return vao

def make_circle(r, origin):
    
    ang_shift = -np.pi/2
    t = np.arange(ang_shift, ang_shift + np.pi * 2.1, 0.1)
    t = t.reshape((len(t), 1))
    x =  origin[0] + r * np.cos(t)
    y =  origin[1] + r * np.sin(t)
    return x, y

# In[]
def dim_scene(hmd, head_pos, eye, stim_shutter): # fr=-0.12, bk=0.05
    #blacklight.setOpacity(0.8)
    
    if eye == 'right':
        stim_shutter.pos = (head_pos.pos[0], head_pos.pos[1])
        stim_shutter.draw(hmd)
    elif eye == 'left':
        stim_shutter.pos = (head_pos.pos[0], head_pos.pos[1])
        stim_shutter.draw(hmd)

    return hmd, stim_shutter

def distance_restriction(hmd, head_pos, eye, stim_shutter, fr=-0.09-0.05, bk=-0.09+0.05): # fr=-0.12, bk=0.05
    # OFF_SET = -1, fr=-1.25, bk=-1.15
    # OFF_SET = 0, -0.09
# =============================================================================
#     print(head_pos.pos)
#     print(bk)
# =============================================================================
    #print(head_pos.pos[2] < fr)
    if head_pos.pos[2] > bk or head_pos.pos[2] < fr:
        if eye == 'right':
            stim_shutter.pos = (head_pos.pos[0], head_pos.pos[1])
            stim_shutter.draw(hmd)
        elif eye == 'left':
            stim_shutter.pos = (head_pos.pos[0], head_pos.pos[1])
            stim_shutter.draw(hmd)
        dimming = True
    else:
        dimming = False
    return hmd, stim_shutter, dimming

def red_activate(hmd, head_pos, eye, redlight, hit_left, hit_right, red_cnt_l=0, red_cnt_r=0):
    light_shift = 0.9
    parallax_thr = 0.1
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
    parallax_thr = 0.1
    if head_pos.pos[0] > parallax_thr and eye == 'right':
        redlight.pos = (light_shift, 0.)
        redlight.draw(hmd)
    elif head_pos.pos[0] < -parallax_thr and eye == 'left':
        redlight.pos = (-light_shift, 0.)
        redlight.draw(hmd)
            
    return hmd

def positive_or_negative():
    if random() < 0.5:
        return 1
    else:
        return -1    

# In[]
if __name__ == '__main__':
    
    #creat_cylinder()
    x_range, z_range = make_circle(1, [0,0])
    y_range = np.linspace(-1, 1, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.squeeze(z_range), (2, 1))
    
    
    x_range = np.linspace(-3.0, 3.0, 2)
    y_range = np.linspace(-1, 1, 2)
    x, y = np.meshgrid(x_range, y_range)
    z = np.tile(np.array([-0.8, -0.8]), (2, 1))
    
    #---------------------------
    x_range = np.linspace(-0.3, 0.3, 2)
    #z = np.linspace(1.55, 1.7, 3)
    z_range = np.linspace(-0.05, 0.05, 2)
    x, z = np.meshgrid(x_range, z_range)
    
    y = np.tile(np.array([11, 12]), (2, 1))