## Code Struture of *Oct Data Image processing and VisualizatioN Tool and GUI (ODIN)*

## Abstract
This document contains a brief discription of the code for the Pipeline
This pipeline provides methods for abstract layer segmentation of OCT volume tomograms and later useage for post-processing, analysis and intertretation.
However, the main scope is to evaluate two layers (of specific tomograms) and provide masks containing the boaders of the layers - **on a slice-tomogram-/"b-Scan"-basis** - for later processing and analysis.

### Run the
Main Function from wich to stat the application
**RUN.m**
pretty much guides the user through the entire **Pipeline**, i.e. the process of data selection (1), pre-processing (2) and confirmation/ correction of segemented layers (3)

**Legend**:
- all non-main functions and files are tagged with a "(Main)" or "(Sub)" at the end of the functions name. This is done to point out if it is a more abstract/ gerneally applicable function "(Sub)" or if it is a function that is essentially tuned to be used in the context of the main useage of this **Pipeline** (i.e. segmenting OCT images with certain dimensions) within the scope of this research project.
- the keywork "(Dep)" stands for depricated, meaning that the function either doesn't exist anymore due to refactoring or redunancy or the use of it in the scope of this **Pipeline** is no longer recommended

## Image filter
**denoiseAndRescaleBScan** (Sub)
// input:
// output:

**detectEdges** (Sub)
// input:
// output:

**filterImageNoise** (Sub)
// input:
// output:

**findVerticalImageGradient** (Sub)
// input:
// output:

**applySavitzkyGolay** (Sub)
// input:
// output:

## Graph Search/ Cut
**createAdjMat** (Sub)
// input:
// output:

**createGradImg** (Sub)
// input:
// output:

**createMaxImg** (Sub)
// input:
// output:

**createMaxImg** (Sub)
// input:
// output:

**automaicallySegementedBinBoundry** (Main)
// input:
// output:

## Manual Segmentation
**selectNPointsManually** (Main)
// input:
// output:


## Pre-/ Post Processing of Graph Search
**interpolateSegmentedPoints** (Main)
// input:
// output:


## Data pre-processing
**loadOctImages** (Main)
// input:
// output:

**saveDataCubeAsBinFile** (Sub)
// input:
// output:

**saveDataCubeAsBinFile** (Sub)
// input:
// output:

**loadDataFromFile** (Sub)
// input:
// output:

**loadOctDataFromBinFile** (Sub)
// input:
// output:


## Auxiliary functions
**calculateAvgSNR** (Sub)
// input:
// output:

**PlayingAround** (NONE)
// input:
// output:
