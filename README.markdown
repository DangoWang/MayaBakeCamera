# Description
This tool is to bake maya cam to a new/pure one, no matter how it's parented or constrained or connected.
# How to use
Download this tool to a place you want to use, then run:

```python
#!/usr/bin/python2
import MayaBakeCamera
reload(MayaBakeCamera)
win = MayaBakeCamera.BakeCamDialog()
win.setupUi(win)
win.show()
```
Make sure that this tool is in your PYTHONPATH, if not, please add these lines on the top of the code above:
```python
#!/usr/bin/python2
import sys
sys.path.append('path/to/your/location/to/install'
```
