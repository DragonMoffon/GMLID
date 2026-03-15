from pathlib import Path

from arcade import Window
import matplotlib.pyplot as plt

from GMLID.export import _load_histogram_raw


win = Window()
win.minimize()
histogram = _load_histogram_raw(Path("System6.histogram"))

data = histogram.read()

plt.imshow(data, extent=(-2.0, 2.0, -2.0, 2.0))
plt.show()
