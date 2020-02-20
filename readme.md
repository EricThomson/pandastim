# pandastim
<img align = "right" width = "120" src=".\images\omr_sin_example.png ">

Cross-platform Python package for generating visual stimuli using the [Panda3d](https://www.panda3d.org/) library.

### Installation
This assumes you are using Anaconda and Python 3:

    conda create --name pstim
    conda activate pstim
    conda install numpy scipy matplotlib zeromq
    pip install panda3d

To install pandastim, just to go the directory where you want it installed and run:    

    git clone https://github.com/EricThomson/pandastim.git

To test the installation, try running one of the examples in [examples/examples_readme.md](examples/examples_readme.md). For instance, `examples/drifting_fullfield_sin.py`. Note that panda3d doesn't always play nicely with IDEs, so I typically run scripts from the command line (e.g., `python -m examples.drifting_fullfield_sin`).

### Package structure
The three main modules:
- `stimuli.py`: defines classes used to show different textures. Can be as simple as showing a static grey sinusoidal grating, or showing a sequence of stimuli locked to an input signal from some external source.
- `textures.py`: texture classes used by the stimulus classes. They are all instances of the `TextureBase` abstract base class defined therein. If you run textures by itself, you can toggle different examples in `main` for fun and debugging.
- `utils.py`: helper code used across different classes: the interface classes for zmq sockets are here.

The `examples/` folder contains many examples. If you want to roll your own, I would use one of those as a starting point. For testing closed-loop experiment code, you can run `pub_class_toggle.py`, a zeromq publisher socket that emits random 0's and 1's that can be consumed by the ClosedLoop class.

### Profiling pandastim code
Panda3d comes with a nice graphical code profiler. To ease access to it, the stimulus classes that subclass `ShowBase` include a `profile_on` flag (which defaults to `False`). To activate it, run `pstats.exe` and set that flag to `True` to run the profiler. This will also cause an FPS display to show on your stimulus window even if you aren't using the profiler.

You can find `pstats.exe` in your conda directory in `\envs\pstim\Scripts`. To learn more about profiling panda3d code: https://docs.panda3d.org/1.10/python/optimization/index

### To do (short term)
- Light refactoring:
    - Basic runthrough of code: documented, relatively clean, etc., including readme.
    -  - what is the deal with setColor versus setBackgroundColor? Also in 's' you are setting card color twice.
    - Also genrally the qm-set or whatever?
- main in stimuli is fubar
- Saving:
    - Save mechanism check. E.g. for save mechanism, save stimulus types and params at top of file before saving which ones were delivered.
    - Have it save start/end time?

- why for transform do you use card.setR for 's' but card.setTexRotate? Are these different?
- what are these different bg colors? sometimes 0 0 0 0 sometimes .5 .5  etc
- Get names straight: stim_class or stim or texture for inputs to stim and calling it self.stim? profile_on is sometimes just profile.
- Add usage note to stimuli for showing examples.
- Should trim down number of examples. Don't need example of everything. Just enough for a smart person to figure it out.
- Clean up stimulus_classes versus experiments (former includes experiments)
- Experiment examples
  - Experiment we will actually use in simple form: red grating/black/white  spot.
- Clean up examples and working directories and document the files better.
- Document how to use ClosedLoopStim. Also put closed loop stim in examples.


### To do (medium term)
- Create new updating stimulus classes
    - looming circle stimulus (static_fullfield_circle)
    - randomly updating stimulus (tex_random_working.py)
    - radial sine stimulus (use their code)
    - radial grating stimulus:
- Create open loop stim class.
- Find good example of weird rendiering differences with two angles, and ask about it @panda3d.
- Consider making monitor a process or use zmq iostream features.
- Make the 'Scaling' showbase? (this is for expanding/contracting circle)
    - Scaling card vs scaling texture?
- plot_timeline seems to not be used, or is used in lots of methods just make it a function?
- Independent color of middle band?
- Add drifting noise stimulus to drifting_fullfield examples.
- Add contrast to sines/gratings
- Have a stim code/previous stim or whatever, and only update task manager if it changes. Add better mechanism so if the stim type is same as previous, just return: don't change stimulus type, don't save anything.

### To do (long term)
- check with photodiode at different locations on window: is it identical?
- Ensure it works in real-time with inputs about fish location.
- Optimize
  - try compressing textures (https://www.panda3d.org/manual/?title=Texture_Compression) (note need 4x size for tex)?
- Consider porting to `pixel2d` (basics are in working/).
- Write up instructions on how to add new stimuli (basically make a numpy array, put it in stimuli.py, and then follow the examples whether you want a static, drifting stimulus, or experiment)
- To make plaids is pretty easy, just supereimpose two guys at two angles as in BinocularDrift fail 1am 3//9/19.
- Make a huge set of possible stimuli to show: the basis set (including plaids)

#### Notes
- If you are just learning panda3d, consider working through their tutorial (https://www.panda3d.org/manual/). Also you might consider installing their SDK, as it comes with useful examples (https://www.panda3d.org/download/).
- panda3d doesn't listen to your OS scale setting, so 800 pixel window is an 800 pixel window, it will not be scaled by your OS.
- It often looks like textures are drifting vertically/horizontally even when they are not. This is the well-known 'aperture problem'. To disambiguate, increase the window size until you can see their edges.
- `stimuli.KeyboardToggleStim` is largely a debugging class: it is really helpful for for testing out code snippits you are thinking of pushing to the closed loop stimuli. Try to keep it up to date with those classes.


#### Conventions
Mostly we are trying to follow PEP8. Naming conventions: UpperCamelCase for classes; lower_case_underscore for vars/functions/methods. Explicit is better than implicit.

#### Acknowledgments
Thanks to the panda3d developers, especially rdb provided lots of help figuring out how to efficiently do 2d things in a 3d game engine.
