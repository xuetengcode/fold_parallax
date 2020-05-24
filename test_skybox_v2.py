from psychopy import visual, event, core
import pyglet.gl as GL

def main():
    hmd = visual.Rift(samples=16, color=(0, 0, 0), waitBlanking=False, winType='glfw')    

    right_img = r'.\images\cube_right.png'
    left_img = r'.\images\cube_left.png'
    up_img = r'.\images\cube_ceiling.png'
    down_img = r'.\images\cube_floor.png'
    back_img = r'.\images\cube_back.png'
    front_img = r'.\images\cube_front.png'
    sky = visual.SceneSkybox(hmd, (right_img, left_img, up_img, down_img, back_img, front_img), ori=0.0, axis=(0, 1, 0))

    while 1:
         absTime = hmd.getPredictedDisplayTime()
         ts = hmd.getTrackingState(absTime)
         headPose = ts.headPose.thePose
    
         hmd.calcEyePoses(headPose)
         for eye in ('left', 'right'):
             hmd.setBuffer(eye)
             hmd.setRiftView()
             #hmd.setDefaultView()
             
             GL.glColor3f(0.5, 0.5, 0.5)
             sky.draw()
             
             
         hmd.flip()
         
         if event.getKeys('q') or hmd.shouldQuit:
             break
    
    hmd.close()
    core.quit()


if __name__ == "__main__":
    main()