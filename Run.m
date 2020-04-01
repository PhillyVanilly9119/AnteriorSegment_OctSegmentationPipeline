%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MAIN FILE for data processing pipeline of Ant. Eye Segmentation-Pipeline
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Forward declarations and globals
global DataStruct
DataStruct.rawVolumeDims = [1024,512,128];
DataStruct.aspectRatioFactor = 2;
DataStruct.loadedVolumeDims =   [
    DataStruct.rawVolumeDims(1), ...
    DataStruct.aspectRatioFactor * DataStruct.rawVolumeDims(2),...
    DataStruct.rawVolumeDims(3)
    ];
DataStruct.mainPath = matlab.desktop.editor.getActiveFilename;
DataStruct.binFileName = 'octDataCube.bin';

%% 1) Preprocessing: Loading Data
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
                DataStruct.rawVolumeDims(1),...
                DataStruct.rawVolumeDims(2), 'bmp');
            %Change aspect ration of BScans to square
            OctDataCube = resizeOctCube(volume, DataStruct.aspectRatioFactor);
        case 'No'
            OctDataCube = OctDataCube;
    end
    
else
    DataStruct.flag_isGoodImgQual = 0;
    DataStruct.currentDataPath = uigetdir();
    %Change aspect ration of BScans to square
    volume = loadOctImages( DataStruct.currentDataPath, ...
        DataStruct.rawVolumeDims(1), ...
        DataStruct.rawVolumeDims(2), 'bmp');
    OctDataCube = resizeOctCube(volume, DataStruct.aspectRatioFactor);
    % Check if octDataCube.bin-file exists
    % -> if not: dialog for saving OCT volume in said *.bin-file
    if isfile(fullfile(DataStruct.currentDataPath, 'Data', DataStruct.binFileName))
        answer = questdlg('Would you like to save all images as a binary-file?', ...
            'Saving Options for OCT Images', 'Yes', 'No', 'No');
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

%Check if folder for masks exists &/ create it
%TODO: add volume ID#
tmp = strsplit(DataStruct.currentDataPath, '\');
DataStruct.maskFolder = fullfile(DataStruct.currentDataPath, 'Data', ...
    'Segmented Masks', strcat('masks_',tmp{end}));
clear temp
if ~exist(DataStruct.maskFolder, 'dir')
    mkdir(DataStruct.maskFolder)
end


%% Display b-Scan
% bScan = octData(:,:,60);
% figure; imshow(bScan);

%% 2) Pre-segementation image-filter-options
sz = size(OctDataCube);
if isfield(DataStruct, 'flag_isGoodImgQual') && ~DataStruct.flag_isGoodImgQual
    imshow(OctDataCube(:,:,round(DataStruct.rawVolumeDims(3)/2)));
    title("Sample b-Scan of volume to evaluate image quality")
    [DataStruct.flag_isGoodImgQual, ProcessedOctCube] = filterVolume(OctDataCube);
else
    ProcessedOctCube = OctDataCube;
end

while ~DataStruct.flag_isGoodImgQual
    close all
    imshow(ProcessedOctCube(:,:,round(sz(3)/2)));
    title("B-Scan at the middle of the pre-processed volume")
    pause(2);
    
    answer = questdlg('Would you like to continue to apply image filter?', ...
        'Is the image qualitey satisfying to start segmentation?', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            [DataStruct.flag_isGoodImgQual, ProcessedOctCube] = filterVolume(ProcessedOctCube);
        case 'No'
            DataStruct.flag_isGoodImgQual = 1;
    end
    
    close all
    
end

imshow(ProcessedOctCube(:,:,(sz(3)/2)));

%% Begin segmenatation
% CAUTION!!! Still in manual trial-phase of implementation
% TODO: Implement as just in case the automatic segmentation failed
% manuallySegmentVolume(ProcessedOctCube);



%% Michis segmentation logic
% TODO: place before manual segmentation (once it works)

%%CONTINUE HERE
% im = createGradImg(single(fltBScan)); %if no image-processing toolbox available
im = ProcessedOctCube(:,:,60);
mask = zeros(sz(1), sz(2));
[seg, mns] = segmentImage(im, mask, 1e-5, 1e-7);

figure
imagesc(im);
colormap gray;
hold on, plot(seg)
% %??? TODO: implement function that finds boarder on basis of gradient


% gradImg = findVerticalImageGradient(fltBScan);
% figure; imshow(gradImg);

