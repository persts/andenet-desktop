# Bounding Box Editor and Exporter (BBoxEE)

BBoxEE is a open-source tool for annotating bounding boxes and exporting data to training object detectors. BBoxEE was specifically developed for the [Animal Detection Network (Andenet)](http://biodiversityinformatics.amnh.org/ml4conservation/animal-detection-network/) initiative, however, it is not limited to annotating camera trap data and can be used for any bounding box annotation task.

BBoxEE is actively under development by Peter Ersts of the [Center for Biodiversity and Conservation at the American Museum of Natural History](https://www.amnh.org/our-research/center-for-biodiversity-conservation). Additional documentation will be forthcoming.

------
## Quick Start Guide
We have put together a [quick start guide](https://github.com/persts/BBoxEE/blob/master/doc/Quick%20Start%20Guide.pdf). This quick start guide is intended to introduce the basic functionality of BBoxEE. It is not intended to be a comprehensive user guide. Additional documentation will follow.

------
## Installation

### Dependencies
BBoxEE is being developed with Python 3.8.5 on Ubuntu 20.04 with the following libraries:

* PyQt5 (5.15.1)
* Pillow (8.0.1)
* Numpy (1.18.5)
* Tabulate (0.8.9)
* TensorFlow (2.4.0)

Build a virtual environment and install the dependencies:
```bash
mkdir python-envs
cd python-envs
python -m venv bboxee-env
source bboxee-env/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy
python -m pip install pillow
python -m pip install pyqt5
python -m pip install tabulate
```

### Clone and Launch BBoxEE
```bash
git clone https://github.com/persts/BBoxEE
cd BBoxEE
# Make sure your Python virtual environment is active
python main.py
```
This is all you need to do to begin using the base annotation functionality of BBoxEE.

------
### Windows Virtual Environment
Download and install Python3 (tested with Python 3.8.5). During the install make sure
to check the box that says "Add Python to environment variables".

Once installed open a CMD window and type the following command to verify python is installed corretly.
```bash
python --version
```
Then build a virtual environment and install the dependencies:
```bash
cd c:\
mkdir python
cd python
mkdir python-envs
cd python-envs
python -m venv bboxee-env
bboxee-env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install numpy
python -m pip install pillow
python -m pip install pyqt5
python -m pip install tabulate
```
### Launching BBoxEE
Clone or download BBoxEE (https://github.com/persts/BBoxEE) into c:\python

```bash
cd c:\python\bboxee
python main.py
```
**Note you will need to activate you virtual environment each time you open an new CMD window.

------

## Assisted Annotation and Exporting

Assisted Annotation is the ability to load an existing object detection model and use the model's prediction(s) as initial annotated bounding box. Assisted Annotation is useful approach for visually assessing the accuracy and precision of your model as you continue to collect additional training data. 

Exporting to some formats may require additional libraries / frameworks.

## Assisted Annotation with TensorFlow and TFRecord Export

### Additional Dependencies:
For detailed steps to install TensorFlow, follow the [TensorFlow installation instructions](https://www.tensorflow.org/install/). 

A typical user can install TensorFlow in a virtual environment with:
``` bash
# Make sure your Python virtual environment is active
python -m pip install tensorflow

```

## Assisted Annotation with YOLOv3 (Torch)
**Note YOLO support has been removed
