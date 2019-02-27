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

### To do (ongoing)
- Add exception handling (e.g., 0 to 255 etc type stuff)
- Make sure you are following the coding conventions below.
- Keep eye open for rgb vs bgr for color texture.

### To do (short term)
- Finish combining FullFieldDrift and FullFieldStatic classes into one module.
- Get all the examples working.
- Fix automatic handling of data types and formats: not everything will be of type `T_unsigned_byte`. You will have 2 byte, 1 byte, rgb, etc.. You need to deal with this.
- Add experiment for static (save data to file options etc) (e.g., grating)
- Add exp for drifting.
- Add generic experiment class
- Add two experiments to examples.
- Add arbitrary left and right angles and velocities.
- Add varying frequencies to sinusoid experiment.
- Refactor and clean up code
- What is reasonable range of speeds for fish?
- remove references to 'byte' just make that default: name deviants eg 2byte.

### To do (medium term)

- Independent color of middle band.
- Add drifting noise stimulus to drifting_fullfield examples.
- Add expanding or contracting circle or both (very different from drifter! this will be a scaling-based dynamic stimulus)
- Add contrast to sine

### To do (long term)
- Center text for text bit it is right justified.
- check with photodiode at different locations on window: is it identical?
- Ensure it works in real-time with inputs about fish location.
- Optimize
  - do diagnostics: https://www.panda3d.org/manual/?title=Performance_Tuning
  - try compressing textures (https://www.panda3d.org/manual/?title=Texture_Compression) (note need 4x size for tex)
- Add masks (e.g., circles or whatever)
- Currently real tests intead of bare asserts?
- Consider porting to `pixel2d` (basics are in working/).
- Write up instructions on how to add new stimuli (basically make a numpy array, put it in stimuli.py, and then follow the examples whether you want a static, drifting stimulus, or experiment)
- Add some simple gui controls?
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
