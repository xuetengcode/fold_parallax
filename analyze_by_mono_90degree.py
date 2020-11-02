import os 
import glob
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
# In[]
d = 1.4
f = 1.3
ipd = 0.064
gain = 2
parallax = 1# [1,gain]
shift = 1# [0,gain-1]
p = np.arange(-0.15,0.15,0.001)
eye = p*parallax+ipd/2
eye_y = np.zeros(p.shape,dtype = int)
# In[original line when head position is at (0,0), eye at (ipd/2, 0)]
ar0 = (d+1)/(1-ipd/2)
am0 = -2*d/ipd
al0 = -(d+1)/(1+ipd/2)

br0 = -ipd*(d+1)/(2-ipd)
bm0 = d
bl0 = ipd*(d+1)/(2+ipd)
# In[eye position at (p*parallax+ipd/2,0)]
#passing(p*parallax+ipd/2,0), and object point: 1-p*(gain-parallax)+p*shift
#slope
ar = (d+1)/(1-p*gain-ipd/2+p*shift)
am = d/(-p*gain-ipd/2+p*shift)
al = (d+1)/(-1-p*gain-ipd/2+p*shift)
#passing (p*parallax+ipd/2,0), 0=a*p_perceived+b
br=-ar*(p*parallax+ipd/2)
bm=-am*(p*parallax+ipd/2)
bl=-al*(p*parallax+ipd/2)
# In[object points]
object_xr0 = np.tile(1,p.shape)
object_xm0 = np.tile(0,p.shape)
object_xl0 = np.tile(-1,p.shape)
object_xr = object_xr0 -p*(gain-parallax)+p*shift
object_xm = object_xm0 -p*(gain-parallax)+p*shift
object_xl = object_xl0 -p*(gain-parallax)+p*shift
object_yl = np.tile(d+1,p.shape)
object_ym = np.tile(d,p.shape)
object_yr = np.tile(d+1,p.shape)
# In[focal plane]
#intersection at y = f, f=a*x+b, x = (f-b)/a
fxr = (f-br)/ar
fxm = (f-bm)/am
fxl = (f-bl)/al

fr = ar*fxr+br
fm = am*fxm+bm
fl = al*fxl+bl
# In[] Intersect of original line and y=a*x+b
#y=y
#a0*x+b0=a*x+b, x=(b-b0)/(a0-a), y=(b-b0)*a0/(a0-a)+b0
d_perceived_r = (br-br0)*ar0/(ar0-ar)+br0
d_perceived_m = (bm-bm0)*am0/(am0-am)+bm0
d_perceived_l = (bl-bl0)*al0/(al0-al)+bl0

dx_perceived_r = (br-br0)/(ar0-ar)
dx_perceived_m = (bm-bm0)/(am0-am)
dx_perceived_l = (bl-bl0)/(al0-al)
# In[]
fig, axs = plt.subplots(1,3, figsize=(20,5))
#for rw in range(3):
axs[0].plot(p, d_perceived_l, linestyle='-', color="r", label="Left side point")
axs[2].plot(p, d_perceived_r, linestyle='-', color="y", label="Right side point")
axs[1].plot(p, d_perceived_m, linestyle='-', color="k", label="Middle point")
axs[0].legend()
axs[1].legend()
axs[2].legend()
axs[0].set(title="median = "+str(np.round(np.median(d_perceived_l),2)) + " m")
axs[1].set(title="median = "+str(np.round(np.median(d_perceived_m),2)) + " m")
axs[2].set(title="median = "+str(np.round(np.median(d_perceived_r),2)) + " m")
axs[0].set(xlabel='Parallax (Meter)')
axs[1].set(xlabel='Parallax (Meter)')
axs[2].set(xlabel='Parallax (Meter)')
axs[0].set(ylabel='Predicted Distance (Meter)')
#axs[0].set_ylim(-1,3)
axs[0].set_ylim(0,2.5)
axs[1].set_ylim(0,2.5)
axs[2].set_ylim(0,2.5)
# In[]
def write_csv(variable,csv_name):
    csv_file = csv_name + '.csv'
    with open(csv_file, 'w') as f:
        for i1 in range(variable.shape[0]):
            if len(variable.shape)>1:
                for i2 in range(variable.shape[1]):
                    f.write(str(variable[i1,i2]))
                    f.write(',')
            else:
              f.write(str(variable[i1]))  
            f.write('\n')
# =============================================================================
# x_save = np.stack((xr,xm,xl),axis=-1)
# write_csv(x_save,"./gain"+str(gain)+"parallax"+str(parallax)+"shift"+str(shift))
# =============================================================================
object_left = np.stack((object_xl,object_yl),axis=-1)
object_middle = np.stack((object_xm,object_ym),axis=-1)
object_right = np.stack((object_xr,object_yr),axis=-1)
focal_left = np.stack((fxl,fl),axis=-1)
focal_right = np.stack((fxr,fr),axis=-1)
focal_middle = np.stack((fxm,fm),axis=-1)
eye = np.stack((eye,eye_y),axis=-1)
names = [
    "object_left",
    "object_middle",
    "object_right",
    "focal_left",
    "focal_middle",
    "focal_right",
    "eye"
    ]
for i0 in range(len(names)):
    write_csv(vars()[names[i0]],"./"+names[i0]+"_gain"+str(gain)+"_parallax"+str(parallax)+"_shift"+str(shift))
