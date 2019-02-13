# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/). Created in [Eva Naumann's lab](https://www.naumannlab.org/). While the stimulus set reflects our fishy interests, pandastim is flexible enough for doing visual psychophysics in any species.

### Installation
Note this assumes you are using anaconda and Python 3.X. Create an environment and install stuff.

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy
    pip install panda3d

I also recommend installing the panda3d SDK at their web site, as it comes with lots of great examples.

**Test it**   
Try out the following scripts:    
- binocular_omr_grating.py #black and white grating
- drifting_sinusoid_experiment.py #full field sinuosoid trials

### To do (short term)
- Make general class for showing drifting matrix, not one for every stimulus? That will sacrifice readability for "good" design. Talk to people about this.
- Make window size part of code instead of configuration file
- Fix exposed edge problem with drifting sinusoid expt
- Finish stimuli, refactor, clean up code
- Add contrast to sine
- Set up stimulus class so you don't keep repeating sin, grating, etc.
- Set up `Experiment` class for this and get it to work.
- Organize modules (stimuli.py, experiments.py, examples.py)
- Add new stimuli (arbitrary matrix, full-field monochrome, fish attractor,)
- Center text for text bit it is right justified.
- For grating etc use photodiode, and check antialiasing: are the two sides really the same?

### To do (longer term)
- Switch from `aspect2d` to `pixel2d` rooted scenegraph for finer control over stimuli.
- Ensure it works in real-time with inputs about fish location.
- Add some simple gui controls for troubleshooting?
