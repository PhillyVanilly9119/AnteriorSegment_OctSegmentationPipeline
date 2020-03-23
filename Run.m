%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MAIN FILE for data processing pipeline of Anterior Eye Seg-
%                   mentation-Pipeline
%
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Forward decs and globals
% Add main path of repository of search path
addpath('C:\Users\ZEISS Lab\Documents\MATLAB\AnteriorEyeSegmentationPipeline\Code')
file = 'octDataCube.bin';
a = 1024;
b = 512;
c = 128;

%% Preprocess
% call this return
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
    % Dialog for saving options of OCT images
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
        saveDataCubeAsBinFile(path, file, octData)
    end
    
end

bScan = octData(:,:,60);
figure; imshow(bScan);

%% Apply image filter
% noise = mean2(bScan(512-100:512+100,256-25:256+25));
% noise = mean2(bScan(end-25:end,:));
% rescaled = denoiseBScan(bScan, 50);
% meded = filterImageNoise(rescaled, 'median', 1);
% filtered = filterImageNoise(meded, 'openAndClose', 2);
% figure; imshow(rescaled);
% weighted = (((1/max(max(double(bScan)))) * double(bScan))) + ((1/max(max(double(rescaled)))) * double(rescaled));
% figure; imshow(weighted);
% figure; imshow(filterImageNoise(weighted, 'openAndClose', 2));

% figure; imshow(filterImageNoise(bScan, 'closeAndOpen', 2));
% figure; imshow(detectEdges(bScan, .005, 'log'))
% smoothAScans = smoothenAScans(bScan, 3, 25); % Params: image, Order, Length
% figure; plot(bScan(:,512)); hold on; plot(smoothAScans(:,512));
% figure; imshow(smoothAScans)