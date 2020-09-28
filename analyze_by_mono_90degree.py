import numpy as np
import matplotlib.pyplot as plt
# In[]
d = 1.4
f = 1.3
ipd = 0.064
parallax_gain = 2
parallax_perceived = 1
p = np.arange(-0.15,0.15,0.001)
# In[]
#slope y=ax+b
ar = (d+1)/(1-p*parallax_gain-ipd/2)
am = d/(p*parallax_gain+ipd/2)
al = (d+1)/(-1-p*parallax_gain+ipd/2)
#passing (p+ipd/2,0), 0=a*(p+ipd/2)+b
br=-ar*(p+ipd/2)
bm=-am*(p+ipd/2)
bl=-al*(p+ipd/2)
#intersect at z = f, f=a*x+b, x = (f-b)/a
xr = (f-br)/ar
xm = (f-bm)/am
xl = (f-bl)/al
# In[] same slope
shift = (parallax_gain-1)*p
d_perceived_r = ar*(1-p*parallax_perceived-shift-ipd/2)
d_perceived_m = am*(p*parallax_perceived+shift+ipd/2)
d_perceived_l = al*(-1-p*parallax_perceived-shift+ipd/2)

# In[]
fig, axs = plt.subplots(1,3, figsize=(20,5))
#for rw in range(3):
axs[0].plot(p, d_perceived_r, linestyle='-', color="r", label="Left side point")
axs[2].plot(p, d_perceived_l, linestyle='-', color="y", label="Right side point")
axs[1].plot(p, d_perceived_m, linestyle='-', color="k", label="Middle point")
axs[0].legend()
axs[1].legend()
axs[2].legend()
axs[0].set(xlabel='Parallax (Meter)')
axs[1].set(xlabel='Parallax (Meter)')
axs[2].set(xlabel='Parallax (Meter)')
axs[0].set(ylabel='Predicted Distance (Meter)')
axs[1].set_ylim(0,2.5)