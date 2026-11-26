import numpy as np
from pathlib import Path
from guiding_simulator import save_figs as sf
import matplotlib.pyplot as plt

path = '/Users/enisgerxhaljia/Library/CloudStorage/OneDrive-UniversityofCambridge/phd/PythonProjects/guiding_simulator/data/raw/harps3_cics_tiptilt_cameraa_observation_raw32_20261123T140425.876Z.raw32'
img = np.fromfile(path, dtype='<u4').reshape(1024, 1280)

# --- plot figure & save figure -----------------------------------------------------------------------------
plt.imshow(img, cmap='gray')
sf.save_figure(plt.gcf(), "raw_camera_frame.png")
plt.show()
