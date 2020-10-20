
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
gain = 1
parallax = 1#
shift = 0#[-1,1]
p = np.arange(-0.15,0.15,0.001)
eye = p*parallax+ipd/2
# In[original line when eye position is (0,0)]
ar0 = (d+1)/1
#  x = 0
al0 = -(d+1)/1
# In[eye position at (p*parallax+ipd/2,0)], y = ax+b, ar - a for right side point, am - middle, al - left.
#passing(p*parallax+ipd/2,0), and (object point)
#slope
ar = (d+1)/(1-p*gain-ipd/2+p*shift)
am = d/(-p*gain-ipd/2+p*shift)
al = (d+1)/(-1-p*gain-ipd/2+p*shift)
#passing (p*parallax+ipd/2,0), 0=a*p_perceived+b
br=-ar*(p*parallax+ipd/2)
bm=-am*(p*parallax+ipd/2)
bl=-al*(p*parallax+ipd/2)
#focal plane, intersect at z = f, f=a*x+b, x = (f-b)/a
xr = (f-br)/ar
xm = (f-bm)/am
xl = (f-bl)/al
# In[] Intersect of original line and y=a*x+b
#y=y
#x(d+1)=ar*x+br, x=br/(d+1-ar), y=br(d+1)/(d+1-ar)
d_perceived_r = br*(d+1)/(d+1-ar)
d_perceived_m = bm
d_perceived_l = bl*(-d-1)/(-d-1-al)

# In[]
fig, axs = plt.subplots(1,3, figsize=(20,5))
#for rw in range(3):
axs[0].plot(p, d_perceived_l, linestyle='-', color="r", label="Left side point")
axs[2].plot(p, d_perceived_r, linestyle='-', color="y", label="Right side point")
axs[1].plot(p, d_perceived_m, linestyle='-', color="k", label="Middle point")
axs[0].legend()
axs[1].legend()
axs[2].legend()
axs[0].set(title="mean = "+str(np.round(np.mean(d_perceived_l),2)) + " m")
axs[1].set(title="median = "+str(np.round(np.median(d_perceived_m),2)) + " m")
axs[2].set(title="mean = "+str(np.round(np.mean(d_perceived_r),2)) + " m")
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
x_save = np.stack((xr,xm,xl),axis=-1)
write_csv(x_save,"./gain"+str(gain)+"parallax"+str(parallax)+"shift"+str(shift))