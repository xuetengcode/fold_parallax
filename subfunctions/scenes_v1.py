# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 15:51:54 2020

@author: Administrator
"""

import pyglet.gl as GL

from subfunctions.experiments import (
    render_plane, render2hmd, gen_offset_mtx,
    red, black,
    distance_restriction, dim_scene
    )

# In[]
def fold_scene(
        hmd, bino, headPose, redlight, stim_shutter,
        adju_ang, 
        WhiteTexture, BlackoutTexture, FloorTexture, 
        trianglePose0, trianglePose,
        stim_origin, stim_aperture_low, stim_aperture_high, stim_floor, stim_left, stim_right, stim_line,
        skydark, sky, voro, 
        dim_flag, dim_cnt, first_scene, 
        dark_cnt, dark_flag,
        plane_dict={}
        ):
    
    dimming = False
    for i in ('left', 'right'):
        if i == 'left' and not bino:
            hmd.setBuffer(i)
            hmd.setRiftView()
            if dim_flag:
                dim_cnt += 1
            #----------------------------------
            hmd.setDefaultView()
            hmd = red(hmd, headPose, i, redlight)
            
            GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
        else:
                
            hmd.setBuffer(i)
            if dim_flag:
                
                dim_ed = 0.7
                total_time = 32*5
                stim_shutter.opacity = dim_cnt/(total_time)
                #blacklight.setOpacity( 1.0 )
                
                #hmd, stim_shutter = dim_scene(hmd, headPose, i, stim_shutter)
                
                if dim_cnt > total_time*dim_ed:
                    # change back
                    stim_shutter.opacity = 0.8
                    dark_flag = True
                    dim_flag = False
                    
                # if dim_cnt > total_time*dim_ed/2:
                #     dimming = True
                # else:
                #     dimming = False
                
                dim_cnt += 1
            elif dark_flag:
                
                if dark_cnt > 320:
                    first_scene = False
                
                dark_cnt += 1
            else:
                dimming = distance_restriction(headPose)
            #hmd, blacklight, dimming = black(hmd, headPose, i, blacklight)
            
            if not dark_flag:
                hmd.setRiftView()
                #--------------- origin
                hmd = render_plane(stim_origin, hmd, WhiteTexture, trianglePose0)
                #--------------- aperture
                hmd = render_plane(stim_aperture_low, hmd, BlackoutTexture, trianglePose0)
                hmd = render_plane(stim_aperture_high, hmd, BlackoutTexture, trianglePose0)
                #--------------- floor
                hmd = render_plane(stim_floor, hmd, FloorTexture, trianglePose0)
                #-------------- the left half prism
                offset_mtx = gen_offset_mtx(adju_ang, trianglePose)
                hmd = render2hmd(stim_left, hmd, voro, offset_mtx)
                #-------------- the right half prism
                offset_mtx = gen_offset_mtx(-adju_ang, trianglePose)
                hmd = render2hmd(stim_right, hmd, voro, offset_mtx)
                #--------- central line
                hmd = render_plane(stim_line, hmd, BlackoutTexture, trianglePose)
                sky.draw()
                if dimming or dim_flag:
                    stim_shutter.draw()
                
            #----------------------------------
            hmd.setDefaultView()
            hmd = red(hmd, headPose, i, redlight)
            
            GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
            
    hmd.flip()
    
    
    return hmd, first_scene, dim_cnt, dim_flag, dark_cnt, dark_flag

# ===============================
def fold_scene_stim(
        hmd, bino, headPose, redlight, blacklight,
        adju_ang, 
        WhiteTexture, BlackoutTexture, FloorTexture, 
        trianglePose0, trianglePose,
        stim_origin, stim_aperture_low, stim_aperture_high, stim_floor, stim_left, stim_right, stim_line,
        skydark, sky, voro, 
        dim_flag, dim_cnt, first_scene,
        dark_cnt, dark_flag
        ):
    
    for i in ('left', 'right'):
        if i == 'left' and not bino:
            hmd.setBuffer(i)
            hmd.setRiftView()
            if dim_flag:
                dim_cnt += 1
            #----------------------------------
            hmd.setDefaultView()
            hmd = red(hmd, headPose, i, redlight)
            
            GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
        else:
                
            hmd.setBuffer(i)
            if dim_flag:
                
                
                dim_ed = 0.5
                total_time = 320*2
                blacklight.setOpacity( 1-dim_cnt/(total_time) )
                #blacklight.setOpacity( 1.0 )
                
                #hmd, blacklight = dim_scene(hmd, headPose, i, blacklight)
                
                if dim_cnt > total_time*dim_ed:
                    # change back
                    blacklight.setOpacity(0.8)
                    dark_flag = True
                    dim_flag = False
                    
                if dim_cnt > total_time*dim_ed/2:
                    dimming = True
                else:
                    dimming = False
                
                dim_cnt += 1
            elif dark_flag:
                if dark_cnt > 320:
                    first_scene = False
                    
                dark_cnt += 1
                
            else:
                hmd, blacklight, dimming = black(hmd, headPose, i, blacklight)
            
            if not dark_flag:
                #hmd, blacklight, dimming = black(hmd, headPose, i, blacklight)
                hmd.setRiftView()
                #--------------- origin
                hmd = render_plane(stim_origin, hmd, WhiteTexture, trianglePose0)
                #--------------- aperture
                hmd = render_plane(stim_aperture_low, hmd, BlackoutTexture, trianglePose0)
                hmd = render_plane(stim_aperture_high, hmd, BlackoutTexture, trianglePose0)
                #--------------- floor
                hmd = render_plane(stim_floor, hmd, FloorTexture, trianglePose0)
                #-------------- the left half prism
                offset_mtx = gen_offset_mtx(adju_ang, trianglePose)
                hmd = render2hmd(stim_left, hmd, voro, offset_mtx)
                
                if dim_flag:
                    hmd, blacklight = dim_scene(hmd, headPose, i, blacklight)
                #-------------- the right half prism
                offset_mtx = gen_offset_mtx(-adju_ang, trianglePose)
                hmd = render2hmd(stim_right, hmd, voro, offset_mtx)
                #--------- central line
                hmd = render_plane(stim_line, hmd, BlackoutTexture, trianglePose)
                
                if dimming:
                    skydark.draw()
                else:
                    sky.draw()
            
            
            #----------------------------------
            hmd.setDefaultView()
            
            
            hmd = red(hmd, headPose, i, redlight)
            
            GL.glColor3f(1.0, 1.0, 1.0)  # <<< reset the color manually
            
    hmd.flip()
    
    
    return hmd, first_scene, dim_cnt, dim_flag, dark_cnt, dark_flag