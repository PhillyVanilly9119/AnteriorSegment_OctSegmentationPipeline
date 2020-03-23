%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% First shot for data preprocessing of OVD study
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Gloabals
file = 'octDataCube.bin';
a = 1024;
b = 512;
c = 128;
d = 3;

%% Data pre-processing
% Check if a data stack is already in the workspace
if exist('data', 'var')
    answer = questdlg('There is already image data in workspace\n Would you like to load a new set?', ...
        'Load OCT data from image files', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            disp('Loading new data set...')
            path = uigetdir();
            data = loadOctImages(path, a, b, 'bmp');
        case 'No'
            data = data;
            flag_Savedata = 0;
    end
    
else
    path = uigetdir();
    data = loadOctImages(path, a, b, 'bmp');
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
        saveDataCubeAsBinFile(path, file, data)
    end
end

bScan = data(:,:,60);
figure; imshow(bScan);
% noise = mean2(bScan(512-100:512+100,256-25:256+25));
noise = mean2(bScan(end-25:end,:));
rescaled = denoiseBScan(bScan, 50);
meded = filterImageNoise(rescaled, 'median', 1);
filtered = filterImageNoise(meded, 'openAndClose', 2);
figure; imshow(rescaled);
weighted = (((1/max(max(double(bScan)))) * double(bScan))) + ((1/max(max(double(rescaled)))) * double(rescaled));
figure; imshow(weighted);
figure; imshow(filterImageNoise(weighted, 'openAndClose', 2));

% figure; imshow(filterImageNoise(bScan, 'closeAndOpen', 2));
% figure; imshow(detectEdges(bScan, .005, 'log'))
% smoothAScans = smoothenAScans(bScan, 3, 25); % Params: image, Order, Length
% figure; plot(bScan(:,512)); hold on; plot(smoothAScans(:,512));
% figure; imshow(smoothAScans)

%% Loading and Store Data
function [octCube] = loadOctImages(path, aScanLength, bScanLength, imgDtTypr)

cd(path)
files = dir(strcat('*.', imgDtTypr));
octCube = [];

for i = 1:length(files)
    if isfile(fullfile(path, files(i).name))
        tmp = imread(files(i).name);
        if length(tmp(:,1)) == aScanLength && length(tmp(1,:)) == bScanLength
            octCube(:,:,i) = tmp;
        else
            fprintf("Image NO.%0.0f has a different size than was expected!\n", i);
        end
    else
        disp("Input path does not contain a or the right file!");
    end
    octCube = uint8(octCube);
end

end


function [] = saveDataCubeAsBinFile(path, fileName, dataCube)

fileID = fopen(fullfile(path, fileName), 'w');
fwrite(fileID, dataCube, 'uint8');
fclose(fileID);
fprintf('Done saving data to %s', fullfile(path, fileName));

end


function [octData] = loadBinFile(path, file, a, b, c)

finalPath = fullfile(path, file);
octData = zeros(a,b,c);

if isfile(finalPath)
    f = fopen(finalPath, 'rb');
    octData = fread(f, a * b * c, 'uint8', 'ieee-le');
    octData = reshape(data, [a,b,c]);
    fclose(f);
else
    disp("Input path does not contain a file!");
end

end


function [denoisedBScan] = denoiseBScan(bScan, scaleFac)
    
    noise = mean2(bScan(end-25:end,:));
%     denoisedBScan = bScan - noise;
    denoisedBScan = ((bScan-noise) ./ scaleFac) .* 255; %scale in dB
    
end


function [edgesBScan] = detectEdges(image, factor, filterOption)

switch filterOption
    case 'log'
        edgesBScan = edge(image, factor, 'log');
end

end


function [filteredBScan] = filterImageNoise(image, filterOption, kernelSize)

switch filterOption
    case 'openAndClose'
        se = strel('square',kernelSize);
        temp = imopen(image, se);
        filteredBScan = imclose(temp, se);
    case 'closeAndOpen'
        se = strel('square',kernelSize);
        temp = imclose(image, se);
        filteredBScan = imopen(temp, se);
    case 'open'
        se = strel('square',kernelSize);
        filteredBScan = imopen(image, se);
    case 'close'
        se = strel('square',kernelSize);
        filteredBScan = imclose(image, se);
    case 'median'
        filteredBScan = medfilt2(image);
end

end


function [filteredBScan] = smoothenAScans(bScan, order, window)

filteredBScan = zeros(size(bScan));
bScan = double(bScan);
sz = size(bScan);

for i = 1:sz(2)
    filteredBScan(:,i) = sgolayfilt(bScan(:,i), order, window);
end

filteredBScan = uint8(filteredBScan);

end