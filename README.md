# monitorp

## Requirements

```
conda create -n env0
conda activate env0
conda install python=3.12
pip install imgui-bundle
```

## Running

Running the main monitorin GUI:
```
python -m rt2.uiimgui
```

Running the neuro data capture module:
```
python runner.py neuro neuro "neuro.NeuroDataCapture(4300)"
```

Running the kinematics data capture module:
```
python runner.py kinem kinem "kinem.KinemDataCapture(4600)"
```

Running the decoded data capture module (broken at the moment but not strictly needed):
```
# python runner.py kinemdec kinem "kinem.KinemDecodeCapture(4700)"
```
