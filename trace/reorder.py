import os
from pathlib import Path

dir_name = 'signal_strength_figures/sunny/挂断' 
paths = sorted(Path(dir_name).iterdir(), key = os.path.getmtime)
print(paths)
for (i, path) in enumerate(paths):
    os.rename(path, "{0}/{1}.png".format(dir_name, i))