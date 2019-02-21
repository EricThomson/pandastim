# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/). Created in [Eva Naumann's lab](https://www.naumannlab.org/). While the stimulus set reflects our fishy interests, pandastim is flexible enough for doing visual psychophysics in any species.

### Installation
Note this assumes you are using anaconda and Python 3.X. Create an environment and install stuff.

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy
    pip install panda3d

It might be a good idea to install the panda3d SDK at their web site, as it comes with lots of great examples.

**Tests**   
Run the following scripts to make sure things are working:    
- binocular_omr_grating.py #binocular black and white grating
- binocular_omr_sinusoid.py  #sinusoid binocular
- drifting_sinusoid_experiment.py #full field sinuosoid trials
- drifting_grating_experiment.py #full field grating trials

### To do (short term)
- Clean up code (main is getting cluttered)
- Add static stimulus examples
  - circle
  - color
- Add experiment for sinusoid drifter.
- Add exp for grating.
- Add generic experiment.
- Add two exp examples.
- Add arbitrary left and right angles and velocities.
- Add varying frequencies to sinusoid experiment.
- Add contrast to sine
- Refactor and clean up code
- What is reasonable range of speeds for fish?

### To do (medium term)
- Make general class for showing drifting matrix, not one for every stimulus? That will sacrifice readability for "good" design. Talk to people about this.
- Set up stimulus class so you don't keep repeating sin, grating, etc.
- Set up `Experiment` class for this and get it to work.
- Organize modules (stimuli.py, experiments.py, examples.py)
- Add new stimuli (arbitrary matrix, full-field monochrome, fish attractor,)
- Center text for text bit it is right justified.
- how to change color of middle band?
- Add color to stimuli (in particular, red)
- Add expanding or contracting circle or both (very different from drifter! this will have scaling)
- Add drifting noise stimulus to examples

### To do (long term)
- check with photodiode at different locations on window: is it identical?
- Ensure it works in real-time with inputs about fish location.
- Add some simple gui controls?
- Optimize
  - do diagnostics: https://www.panda3d.org/manual/?title=Performance_Tuning
  - try compressing textures (https://www.panda3d.org/manual/?title=Texture_Compression) (note need 4x size for tex)
- Add masks (e.g., circles or whatever)
- Currently real tests intead of bare asserts?
- Consider porting to `pixel2d` (basics are in working/).

#### Notes
- panda3d doesn't listen to windows scale setting, so 800 is 800.
- For thinking about how to store parameters/data about a particular object (e.g., a sinusoid) in a struct-like way, this is a very helpful source of ideas: https://stackoverflow.com/questions/35988/c-like-structures-in-python

#### To think about
- Should we start at same position each time, or randomize phase?


#### Formatting
- name/1-line description/link to pandastim/longer description
    https://github.com/EricThomson/pandastim
- Underscore name for vars/instances/methods, camelcase for classes.

#### Acknowledgments
The panda3d developers are a generous bunch, and answered dozens of questions about the basic mechanics of how panda3d works. Special shout-out to rdb.
