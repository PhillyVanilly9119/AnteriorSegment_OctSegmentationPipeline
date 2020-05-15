    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MAIN FILE for data processing pipeline of Ant. Eye Segmentation-Pipeline
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Define global vars (Struct)
global DataStruct
DataStruct.imageVolumeDims = [1024,512,128]; %default cude size
DataStruct.aspectRatioFactor = 2; %change aspect ratio: stretch image width
DataStruct.processingVolumeDims =   [
    DataStruct.imageVolumeDims(1), ...
    DataStruct.aspectRatioFactor * DataStruct.imageVolumeDims(2),...
    DataStruct.imageVolumeDims(3)
    ];
DataStruct.mainPath = matlab.desktop.editor.getActiveFilename;
DataStruct.binFileName = 'octDataCube.bin';
DataStruct.endoText = ["Select the Endothelium boundary through clicking with the cursor"...
"Please only select unique, consecutive points"...
"When the segmentation is complete, end it with a double click"];
DataStruct.epiText = "Select the Epithelium boundary through clicking with the cursor";
DataStruct.ovdText = ["Select the Endothelium boundary through clicking with the cursor"...
"Please only select unique, consecutive points"...
"When the segmentation is complete, end it with a double click"];


%% 1) Preprocessing: Loading Data

% Add main path of repository of search path
filePath = matlab.desktop.editor.getActiveFilename;

warning("Change 'localGlobPath'-variable to your local path, were you keep the repository")
localGlobPath = 'C:\Users\ZeissLab\Documents\Documents_Philipp\Code\AnteriorSegment_OctSegmenationPipeline';
addpath(fullfile(localGlobPath, 'Code'));

binFileOct = 'octDataCube.bin'; 
maskFolder = fullfile(localGlobPath, 'Data', 'SegmentedMasks');
a = 1024; %static for standard
b = 512;
c = 128;

%% 2) Preprocessing
% Check if a data stack is already in the workspace
if exist('OctDataCube', 'var')
    answer = questdlg('There is already data in workspace. Would you like to load a new set?', ...
        'Load OCT data from image files', 'Yes', 'No', 'No');
    DataStruct.flag_isGoodImgQual = 1;
    switch answer
        case 'Yes'
            disp('Loading new data set...')
            DataStruct.currentDataPath = uigetdir();
            volume = loadOctImages( DataStruct.currentDataPath, ...
                DataStruct.imageVolumeDims(1),...
                DataStruct.imageVolumeDims(2), 'bmp');
            %Change aspect ration of BScans to square
            OctDataCube = resizeOctCube(volume, DataStruct.aspectRatioFactor);
    end
    
else
    DataStruct.flag_isGoodImgQual = 0;
    DataStruct.currentDataPath = uigetdir();
    %Change aspect ration of BScans to square
    volume = loadOctImages( DataStruct.currentDataPath, ...
        DataStruct.imageVolumeDims(1), ...
        DataStruct.imageVolumeDims(2), 'bmp');
    OctDataCube = resizeOctCube(volume, DataStruct.aspectRatioFactor);
    % Check if octDataCube.bin-file exists
    % -> if not: dialog for saving OCT volume in said *.bin-file
    if isfile(fullfile(DataStruct.currentDataPath, 'Data', DataStruct.binFileName))
        answer = questdlg('Would you like to save all images as a binary-file?', ...
            'Saving Options for OCT Images\n', 'Yes', 'No', 'No');
        switch answer
            case 'Yes'
                disp('Saving your data on same path as images were loaded from')
                saveDataCubeAsBinFile(  DataStruct.currentDataPath, ...
                    DataStruct.binFileName, OctDataCube);
            case 'No'
                disp('Data was not saved')
        end
    end
    
end

clear volume
%TODO: shouldnt change for whole volumes
correctSz = size(OctDataCube);
DataStruct.processingVolumeDims(2) = correctSz(2);
DataStruct.processingVolumeDims(3) = correctSz(3);

%Check if FOLDERS for MASKS already exist &/ create it
tmp = strsplit(DataStruct.currentDataPath, '\');
DataStruct.dataFolder = fullfile(DataStruct.currentDataPath, 'Segmented_Data');
DataStruct.maskFolder = fullfile(DataStruct.dataFolder, strcat('masks_',tmp{end}));
if ~exist(DataStruct.maskFolder, 'dir')
    mkdir(DataStruct.maskFolder);
end
DataStruct.contMaskFolder = fullfile(DataStruct.dataFolder, strcat('continuousMasks_',tmp{end}));
if ~exist(DataStruct.contMaskFolder, 'dir')
    mkdir(DataStruct.contMaskFolder);
end
DataStruct.thickMaskFolder = fullfile(DataStruct.dataFolder, strcat('thickMasks_',tmp{end}));
if ~exist(DataStruct.thickMaskFolder, 'dir')
    mkdir(DataStruct.thickMaskFolder);
end
DataStruct.machineLearningFolder = fullfile(DataStruct.currentDataPath, "Data_Machine_Learning");
if ~exist(DataStruct.machineLearningFolder, 'dir')
    mkdir(DataStruct.machineLearningFolder);
end

%% 3) Apply filter, to allow segmentation
ProcessedOctCube = applyCustomFilterForRESCAN(DataStruct, OctDataCube, 'fixed');
close all


%% 4) Begin segmenatation
segmentationLoop(DataStruct, OctDataCube, ProcessedOctCube);


%% END - Clean Up
close all

fprintf('Done segmenting recorded volume \"%s\"! \n', tmp{end});

