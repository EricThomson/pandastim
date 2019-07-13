# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Cross-platform Python package for generating visual stimuli using [Panda3d](https://www.panda3d.org/).

### Installation
This assumes you are using Anaconda and Python 3. Create an environment and install stuff.

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy matplotlib
    pip install panda3d json-tricks

To install pandastim, just to go the directory where you want it installed and run:    

    git clone https://github.com/EricThomson/pandastim.git

To test the installation, try running one of the examples in [examples/examples_readme.md](examples/examples_readme.md). For instance, `examples/drifting_fullfield_sin.py`. Note that panda3d doesn't always play nicely with IDEs, so I typically run scripts from the command line (e.g., `python -m examples.drifting_fullfield_sin.py`).

### Structure
There are three main modules:
- `textures.py`: defines the textures used in stimulus classes (2d numpy arrays)
- `stimulus_classes.py`: defines classes used to show stimuli (e.g., full field drifting texture). This is the main interface with panda3d.
- `experiments.py`: defines classes used to run experiments, which are sets of stimuli. Saves data as json.

If you run any of those modules, `__main__` will run examples. Further, the `examples` folder contains many examples of how to present different stimuli or run different types of experiments. If you want to roll your own, I would use those examples as a starting point.


### To do (short term)
- Create new updating stimulus classes
    - looming circle stimulus (static_fullfield_circle)
    - randomly updating stimulus (tex_random_working.py)
    - radial sine stimulus (use their code)
    - radial grating stimulus: https://github.com/pygobject/pycairo
- Experiment examples
  - Experiment we will actually use in simple form: red grating/black/white  spot.
- Save infrastructure  https://www.pythonforthelab.com/blog/introduction-to-storing-data-in-files/
    - Append to a dictionary value (a list) each time through, without changing the other values. Maybe simple standalone example of this.
    - Append each time a new stimulus is shown
    - Include time started (eg https://discourse.panda3d.org/t/window-closing-event-is-not-being-sent/13535/4)
    - Decide whether to continue with json vs binary/pandas/hdf5
- put experiments in experiments.py instead of stimulus_classes.py
- integrate stimulus_classes into experiments instead of doing them de novo?
- With movement task check to see if vel=0 first don't just run it
- make step plot of events a function/utils.py
- Make binocular experiment class
- Make generic experiment class
- Add some experiments to examples.
- Add note (do this with gui?)


### To do (medium term)
- for examples, make imports better (should I be appending ..?)
  could just make pip installable.
- when someone enters 1,0,0 or whatever for rgb fix it don't show black.
- Gui wrapper for all of the above. Either pyqt or panda3d built-in.
- New way of handling dtype and ndims is better: transfer to other classes, in fact: refactoring stim classes: DRY handling dtype and dims: this is also in experiment class!
- Have window name as an optional input argument?
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
- switch frame-based updating in task mgr instead of time?
### To do (long term)
- Integrate with GUI (either DirectGUI (panda3d) or pyqt): don't start with this it is premature
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
- If you are just learning panda3d, you might consider installing the panda3d SDK, as it comes with useful examples (https://www.panda3d.org/download/). There is a good tutorial/manual online: https://www.panda3d.org/manual/


#### To think about
- For gratings/sinusoids, start at same position each time, or randomize phase?

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
