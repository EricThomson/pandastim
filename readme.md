# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/). Created in [Eva Naumann's lab](https://www.naumannlab.org/). While the stimulus set reflects our fishy interests, pandastim is flexible enough for doing visual psychophysics in any species.

### Installation
Note this assumes you are using anaconda and Python 3.X. Create an environment and install stuff.

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy
    pip install panda3d

I recommend installing the panda3d SDK from the web site, as it comes with useful examples.

**Tests**   
Check out the list of examples in [examples/examples_readme.md](examples/examples_readme.md), and run those that strike your fancy. For instance, `examples/drifting_fullfield_sin.py`

### To do (short term)
- change all 'sin' to sine sa
- fullfield_static_stimulus.py and remove any remnants of drifting class. sa
- Add circle example (just black and white) sa
- Work through examples of color textures. su
  - add flat color example to texture(s) su
  - add arbitrary static color textures su
  - add arbitrary drifting color textures m
- Add automatic handling of data types: not everything will be of type `T_unsigned_byte`. You will have 2 byte, 1 byte, rgb, etc.. You need to deal with this.
- Combine FullFieldDrift and FullFieldStatic classes into one module.
- Add exception handling (e.g., 0 to 255 etc type stuff)
- Make sure you are following the coding convetions below.
- Add experiment for static (save data to file options etc)
- Add exp for grating.
- Add generic experiment.
- Add two exp examples.
- Add arbitrary left and right angles and velocities.
- Add varying frequencies to sinusoid experiment.
- Add contrast to sine
- Refactor and clean up code
- What is reasonable range of speeds for fish?


### To do (medium term)
- Center text for text bit it is right justified.
- how to change color of middle band?
- Add color to stimuli (in particular, red)
- Add expanding or contracting circle or both (very different from drifter! this will be a scaling-based dynamic stimulus)
- Add drifting noise stimulus to drifting_fullfield examples.

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
- Write up instructions on how to add new stimuli (basically make a numpy array, put it in stimuli.py, and then follow the examples whether you want a static, drifting stimulus, or experiment)
- Make the circle edges smooth. Something like: https://yellowsplash.wordpress.com/2009/10/23/fast-antialiased-circles-and-ellipses-from-xiaolin-wus-concepts/

#### Notes
- panda3d doesn't listen to windows scale setting, so 800 is 800.
- It typically looks like textures are drifting vertically or horizontally even when they are not. This is the well-known 'aperture problem'. To convince yourself that the bars are actually moving perpendicular to the angle, just increase the window size until you can see their edges. Question: is this a problem when analyzing fish data?
- Could be useful to disentangle chromatic, orientation, and motion representations using light sheet. Talk to linsday glickfeld. Look at more traditional spatiotemporalchromatic representations.

#### To think about
- Should we start at same position each time, or randomize phase?


#### Conventions
- UpperCamelCase for class names; lower_case_underscore for vars/functions.
- Documentation:
  - Module: path to module/one line description//pandastim blurb
  - Functions/classes :
    - If simple, just one-line description
    - If not simple:
      - one-line description and enumeration of inputs/outputs w/types
      - Example if it will be helpful

#### Acknowledgments
The panda3d developers are a generous bunch, and answered dozens of questions about the basic mechanics of how panda3d works. Special shout-out to rdb.
