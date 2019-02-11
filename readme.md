# pandastim
<img style="float: right;width: 180px;" src=".\images\omr_sin_example.png ">

Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/). Created in Eva Naumann's lab (https://www.naumannlab.org/).  While the stimulus set reflects our fishy interests, this package is flexible enough to do visual psychophysics in any species.

### Installation
Note this assumes you are using anaconda and Python 3.X.

**Create environment**    
`conda create --name pstim`

**Install packages**    
Requires `panda3d`, `numpy`, `scipy`.
To install panda3d, use `pip` not `conda install`. I would recommend installing the SDK, as it comes with lots of great examples.

**Test it**
- Run simple experiment with four trials
  - drifting_sinusoid_experiment.py (shows drifting binocular sinusoids)
- Run one simple Stimuli
  - binocular_omr_grating.py  (black and white grating)
  - binocular_omr_sin.py  (single drifting sinusoid)

## Organization of modules
- stimuli.py : contains classes and functions for stimulus control
- experiments.py : contains classes and functions for experimental design
- examples.py : contains examples of stimuli and experiments

### Stimuli
- Arbitrary matrix (just give it a numpy array)
- Full field monochromatic stimulus
- Fish attractor
- Full field drifting sinusoid
- Double half sinusoid fixed fish  
- Double half sinusoid freely moving fish

### To do (right now)
- Finish stimuli, refactor, clean up code
- Add contrast to sine

### To do (short term)
- Set up stimulus class so you don't keep repeating sin, grating, etc.
- Set up `Experiment` class for this and get it to work.

### To do (longer term)
- Switch from `aspect2d` to `pixel2d` rooted scenegraph for finer control over stimuli.
- Add some simple gui controls for troubleshooting?
