% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % Run file to run through data that has to be re-segmented manually
% copyright:
% @philipp.matten@meduniwien.ac.at
%
% Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Define global vars (Struct)
global DataStruct
DataStruct.imageVolumeDims = [512,512,128]; %default cude size
DataStruct.aspectRatioFactor = 1; %change aspect ratio: stretch image width
DataStruct.processingVolumeDims =   [
    DataStruct.imageVolumeDims(1), ...
    DataStruct.aspectRatioFactor * DataStruct.imageVolumeDims(2),...
    DataStruct.imageVolumeDims(3)
    ];
DataStruct.mainPath = matlab.desktop.editor.getActiveFilename;
DataStruct.imgDataType = 'bmp';
DataStruct.binFileName = 'octDataCube.bin';
DataStruct.endoText = ["Select the Endothelium boundary through clicking with the cursor"...
    "Please only select unique, consecutive points"...
    "When the segmentation is complete, end it with a double click"];
DataStruct.epiText = "Select the Epithelium boundary through clicking with the cursor";
DataStruct.ovdText = ["Select the Endothelium boundary through clicking with the cursor"...
    "Please only select unique, consecutive points"...
    "When the segmentation is complete, end it with a double click"];


% 1) Preprocessing: Loading Data

%Add main path of repository of search path
filePath = matlab.desktop.editor.getActiveFilename;

warning("Change 'localGlobPath'-variable to your local path, were you keep the repository")
localGlobPath = 'C:\Users\ZeissLab\Documents\Documents_Philipp\Code\AnteriorSegment_OctSegmenationPipeline';
addpath(fullfile(localGlobPath, 'Code'));

binFileOct = 'octDataCube.bin';
maskFolder = fullfile(localGlobPath, 'Data', 'SegmentedMasks');

% 2) Preprocessing
DataStruct.currentDataPath = uigetdir();
cd(DataStruct.currentDataPath)
files = dir(strcat('*.', DataStruct.imgDataType));
nFiles = length(files);
octCube = zeros(DataStruct.imageVolumeDims(1), DataStruct.imageVolumeDims(2), nFiles);
% Load images
for i = 1:nFiles
    currFile = fullfile(files(1).folder, files(i).name);
    if isfile(currFile)
        tmp = imread(currFile);
        tmp = uint8(tmp(:,:,1));
        octCube(:,:,i) = tmp; 
    end
end

OctDataCube = resizeOctCube(octCube, DataStruct.aspectRatioFactor);
correctSz = size(OctDataCube);
DataStruct.processingVolumeDims(2) = correctSz(2);
DataStruct.processingVolumeDims(3) = correctSz(3);

%Check if FOLDERS for MASKS already exist &/ create it
DataStruct.machineLearningFolder = fullfile(DataStruct.currentDataPath, "Data_Machine_Learning");
if ~exist(DataStruct.machineLearningFolder, 'dir')
    mkdir(DataStruct.machineLearningFolder);
end

%% Main segmentation loop
% pre-allocate special masks
continuousMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));
thickMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

% get created folders and start segmentation accordingly
loopIdx = checkForPresegmentedScans(DataStruct.machineLearningFolder);

if loopIdx <= DataStruct.processingVolumeDims(3)
    for i = loopIdx:DataStruct.processingVolumeDims(3)
        
        b_Scan = OctDataCube(:,:,i);
        rawB_Scan = OctDataCube(:,:,i);
        [label, frames] = createSegmenationLabel(b_Scan);
        
        %No layer visible
        if label == 0
            % save all masks as "empty imges" in this case/ interation
            saveEmptyMask(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i);
            saveContinMasks(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i)
            saveThickMasks(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i);
            %% !!!CAUTION!!! non-useable for training but important for re-entering segmentation
            checkAndCreateDirsForDeepLearningData(DataStruct.machineLearningFolder,...
                rawB_Scan, b_Scan, ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)))
            fprintf("No layers visible in b-Scan No.%0.0f \nSaved empty a mask", i);
            continue
        else
            flag_segmentationSufficient = 0;
            [mask, curve] = segmentaScanDerivative(b_Scan, label, frames);
            
            while ~flag_segmentationSufficient
                %TODO: overwrite frames if manual additional segmentation took
                %place
                figure('units','normalized','outerposition',[0 0 1 1])
                imagesc(b_Scan);
                colormap gray;
                hold on
                title('Segmented layer boundarys')
                plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),1)) %Epithelium
                plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),2)) %Endothelium
                % condition if ONLY Endothelium is visible
                if frames(1,2) ~= 0 && frames(2,2) ~= 0
                    plot(frames(1,2):frames(2,2), curve(frames(1,2):frames(2,2),3)) %OVD
                end
                pause(0.5)
                %______________________________________________
                % Only Epi- and Endothelium visible
                if label == 1
                    answer = questdlg('Were the Cornea layers segmented correctly?',...
                        'Please select one box',...
                        'Yes', 'No, resegment Epithelium', 'No, resegment Endothelium',...
                        'Yes');
                    switch answer
                        case 'Yes'
                            flag_segmentationSufficient = 1;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            continue
                            %Re-segment EPITHELIUM
                        case 'No, resegment Epithelium'
                            flag_segmentationSufficient = 0;
                            curve(:,1) = resegmentLayer(b_Scan, DataStruct, DataStruct.epiText);
                            curve(:,3) = 0;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            % re-segment ENDOTHELIUM
                        case 'No, resegment Endothelium'
                            flag_segmentationSufficient = 0;
                            curve(:,2) = resegmentLayer(b_Scan, DataStruct, DataStruct.endoText);
                            curve(:,3) = 0;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                    end
                %______________________________________________
                % All layers visible
                elseif label == 2
                    answer = questdlg('Were the boundary layers correctly segmented?',...
                        'Please select one box',...
                        'Yes', 'No, re-segment OVD', 'No, re-segment Cornea',...
                        'Yes');
                    switch answer
                        case 'Yes'
                            flag_segmentationSufficient = 1;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            continue
                        case 'No, re-segment Cornea'
                            flag_segmentationSufficient = 0;
                            curve(:,1) = resegmentLayer(b_Scan, DataStruct, DataStruct.epiText);
                            curve(:,2) = resegmentLayer(b_Scan, DataStruct, DataStruct.endoText);
                        case 'No, re-segment OVD'
                            flag_segmentationSufficient = 0;
                            curve(:,3) = resegmentLayer(b_Scan, DataStruct, DataStruct.ovdText);
                    end
                %______________________________________________
                % All layers visible
                else
                    warning("Unexpected number layers detected!\n")
                    return
                end
                close all
            end
            %______________________________________________
            %Save the masks containing correctly segmented boundary layers)
            checkAndCreateDirsForDeepLearningData(DataStruct.machineLearningFolder,...
                rawB_Scan, b_Scan, ...
                mask, continuousMask, thickMask, binaryMask, inverseBinMask);
            
        end
        
    end
else
    disp("You have already segmented all b-Scans, you busy bee! :)")
end

% END - Clean Up
close all

fprintf('Done segmenting recorded volume \"%s\"! \n', tmp{end});