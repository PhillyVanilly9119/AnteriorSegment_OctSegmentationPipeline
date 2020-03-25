%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MAIN FILE for data processing pipeline of Ant. Eye Segmentation-Pipeline
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Forward declarations and globals

% Add main path of repository of search path
warning("Change 'localGlobPath'-variable to your local path, were you keep the repository")
localGlobPath = 'C:\Users\ZEISS Lab\Documents\MATLAB\AnteriorEyeSegmentationPipeline\Code';
addpath(localGlobPath);

binFileOct = 'octDataCube.bin';
maskFolder = fullfile(localGlobPath, 'SegmentedMasks');
a = 1024; %static for standard
b = 512;
c = 128;

%% 1) Preprocessing
% Check if a data stack is already in the workspace
if exist('octData', 'var')
    answer = questdlg('There is already a data set in the workspace. Would you like to load a new set?', ...
        'Load OCT data from image files', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            disp('Loading new data set...')
            path = uigetdir();
            octData = loadOctImages(path, a, b, 'bmp');
        case 'No'
            octData = octData;
            %flag_Savedata = 0;
    end
    
else
    path = uigetdir();
    octData = loadOctImages(path, a, b, 'bmp');
    % Check if octDataCube.bin-file exists
    % -> if not: dialog for saving OCT volume in said *.bin-file
    if isfile(fullfile(localGlobPath, binFileOct))
        answer = questdlg('Would you like to save all images as a binary-file?', ...
            'Saving Options for OCT Images', 'Yes', 'No', 'No');
        switch answer
            case 'Yes'
                disp('Saving your data on same path as images were loaded from')
                flag_Savedata = 1;
            case 'No'
                disp('Data was not saved')
                flag_Savedata = 0;
        end
        if flag_Savedata == 1
            saveDataCubeAsBinFile(path, binFileOct, octData)
        end
    end
    
end


%% Display b-Scan
% bScan = octData(:,:,60);
% figure; imshow(bScan);

%% 2) Pre-segementation image-filter-options

sz = size(octData);
imshow(octData(:,:,round(sz(3)/2)));
title("B-Scan at the middle of the loaded volume")
pause(2);

[flag_ImageQualiyIsGood, filteredOctCube] = filterVolume(octData);
while ~flag_ImageQualiyIsGood
    close all
    
    imshow(filteredOctCube(:,:,round(sz(3)/2)));
    title("B-Scan at the middle of the pre-processed volume")
    pause(2);
    
    answer = questdlg('Would you like to continue to apply image filter?', ...
        'Is the image qualitey satisfying to start segmentation?', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            [flag_ImageQualiyIsGood, filteredOctCube] = filterVolume(filteredOctCube);
        case 'No'
            flag_ImageQualiyIsGood = 1;
            
    end
    
    close all
    
end

imshow(filteredOctCube(:,:,64))
%% Begin segmenatation
% CAUTION!!! Still in manual trial-phase of implementation
% TODO: call from loop, to go through whole volume

%Check if folder for masks exists &/ create it
if ~exist(maskFolder, 'dir')
    mkdir(maskFolder)
end

%%Maunal segmentation
%%CONTINUE HERE
cubeSz = size(filteredOctCube);
segPts = round(cubeSz(2)/20);
for i = 1:cubeSz(3)

    pts = selectNPointsManually(fltBScan, segPts); %segment points along boarder
    intPts = interpolateSegmentedPoints(pts, cubeSz(2), cubeSz(1)); %returns "point-string" of 1st interface in bScan

end

mask(:,:,1) = zeros(cubeSz(1), cubeSz(2)); %declare mask of first layer
%loop to replace all boarder pixels with ones
for i = 1:length(intPts)
    if (mask(1,:,1) <= cubeSz(2)) && (mask(:,1,1) <= cubeSz(1))
        mask(intPts(2,i),intPts(1,i),1) = 1;
    end
end

%% Michis segmentation logic
% fltBScan = filteredOctCube(:,:,64);
% % fltBScan = filterImageNoise(fltBScan(5:end,:), 'openAndClose', 3);
% % fltBScan = filterImageNoise(fltBScan, 'open', 7);
% % fltBScan = denoiseAndRescaleBScan(fltBScan, 25);
% % figure; imshow(fltBScan)
% sz = size(fltBScan);
% mask = zeros(sz(1), sz(2));
%
% im = createGradImg(single(fltBScan)); %if no image-processing toolbox available
% figure; imshow(im);
% [seg, mns] = segmentImage(im, mask, 1e-4);
%
% figure
% imagesc(fltBScan);
% colormap gray;
% hold on, plot(seg)
% %??? TODO: implement function that finds boarder on basis of gradient


% gradImg = findVerticalImageGradient(fltBScan);
% figure; imshow(gradImg);

%TODO: Add saving logic for segmented masks in a sub-folder
%TODO: add pre-check if masks already exist