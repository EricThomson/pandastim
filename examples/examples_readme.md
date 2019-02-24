## Examples for pandastim package
List of examples to see how the code works or run to test initial install.

### Full field static stimuli
Nonmoving stimuli that use the `FullFieldStatic` class.
- static_fullfield_sine.py
- static_fullfield_circle.py
- static_fullfield_red.py

### Full field drifting stimuli
Textures that drift across the window forever, using the `FullFieldDrift` class.
- drifting_fullfield_sin.py : drifting full-field sinusoid at arbitrary angle/velocity/frequency
- drifting_fullfield_grating.py : drifting full-field grating at arbitrary angle/velocity/frequency
- binocular sin
- binocular grating

### Experiments
Standard trial-based structure: baseline/stimulus alternating, based on arrays of values you choose for different parameters for timing and stimulus values.
- full sin
- full grating
