# Simulink Model

## File

`awe_dt.slx`

This is the short-name working model intended for MATLAB/Simulink R2024b
Update 5. The short filename reduces the risk of Windows path-length errors
during MATLAB Function and Stateflow code generation.

## Opening the model

Place the repository in a short path, preferably:

`C:\AWE\alkaline-water-electrolyzer-digital-twin`

In MATLAB, set the Current Folder to the repository root and run:

```matlab
addpath('matlab')
setup_awe_build
```

Press `Ctrl+D` to update the diagram before simulation.

## Important

Do not open or build the model directly from a ZIP preview or a deeply
nested temporary folder. MATLAB and Stateflow generate nested source paths,
and a long working path can exceed the Windows path limit.
