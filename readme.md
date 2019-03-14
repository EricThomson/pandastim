# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/).

### Installation
This assumes you are using Anaconda and Python 3. Create an environment and install stuff.

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy
    pip install panda3d

I recommend installing the panda3d SDK from the web site, as it comes with useful examples.

To test the installation, check out the list of examples in [examples/examples_readme.md](examples/examples_readme.md), and run those that strike your fancy. For instance, `examples/drifting_fullfield_sin.py`

### To do (ongoing)
- Add exception handling (e.g., 0 to 255 etc type stuff)
- Make sure you are following the coding conventions below.
- Keep eye open for rgb vs bgr for color texture.

### To do (short term)
- Refact `BinocularDrift`
  - Add rgb handling
  - Add uint16 handlin
  - Clean up stimulus_classes example. E.g  what should be stim_params dict
- Add a bunch of examples (sinusoid, colored sin, different colored static)
- Change examples in stimulus_classes don't just use two gratings.
- Fill in rotating_mask_drifting_grating.py in examples: make sure it works.
- Fix window title of drift/static versions: they shouldn't inherit title!
- Refactor experiments
  - Add experiment for static (save data to file options etc) (e.g., grating)
  - Add experiment for drifting.
  - Add generic experiment class
  - Add experiment for binocular
  - Add three experiments to examples.
  - NBote new position is negative of what you expect because it being applied
  to a texture *stage* uv coordinates, not the texture: https://www.panda3d.org/manual/?title=Texture_Transforms

### To do (medium term)
- Update all docstrings in textures.py
- Two independent textures for binocularDrift etc, or make that the parent class with identical textures a child class
- Independent color of middle band.
- Add drifting noise stimulus to drifting_fullfield examples.
- Add expanding or contracting circle or both (very different from drifter! this will be a scaling-based dynamic stimulus)
- Add contrast to sine
- Bring 'notes' for `FullfieldDrift` into readme.md?
- Make animal angle a decorated property and when it is changed change the window title?
- Add PR to p3d
- Revisit binocular_plaid_oneside.py very cool but based on mistake.
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
- Make abstract stimulus class, drift/static are instances?
  - turn creation of texture_stage (componenttype/format setting) into a method
- To make plaids is pretty easy, just supereimpose two guys at two angles as in BinocularDrift fail 1am 3//9/19.
- Show a huge set of possible stimuli to show: the basis set (including plaids)
- orientation, velocity, color, spatial frequency, temporal frequency. All of these can be shown in a binocular fashion and we can get a functional decomposition...don't need inter-individual differences, can get intra-indivfidual differences and see effects on OMR in the circuitry based on pretectal activity and fiferences in functional connectivity, a kind of internal control.  There is nothing magical about moving sinusoids or gratings: what we can have moving will reveal the functional architecture of the visual system.

#### Notes
- panda3d doesn't listen to windows scale setting, so 800 is 800.
- It typically looks like textures are drifting vertically/horizontally even when they are not. This is the well-known 'aperture problem'. To disambiguate, increase the window size until you can see their edges. Question: is this a problem when analyzing fish data?
- Could be useful to disentangle chromatic, orientation, and motion representations using light sheet. Talk to linsday glickfeld. Look at more traditional spatiotemporal chromatic representations.

#### To think about
- Should we start at same position each time, or randomize phase?

#### Conventions
- UpperCamelCase for class names; lower_case_underscore for vars/functions.
- Documentation:
  - Module: path to module/one line description//longer desciption if needed//pandastim blurb
  - Functions/classes :
    - If simple, just one-line description
    - If not simple:
      - one-line description and enumeration of inputs/outputs w/types
      - Example if needed

#### Acknowledgments
Thanks to the panda3d developers who answered dozens of my questions. In particular, rdb provided lots of help figuring out how to efficiently do 2d things in a 3d game engine.
