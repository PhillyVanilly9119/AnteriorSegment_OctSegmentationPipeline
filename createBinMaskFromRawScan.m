%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [binaryMask] = createBinMaskFromRawScan(DataStruct, rawBScan)

binaryMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

% reduce hoise on basis of histogram 
b = rawBScan;
[pixelCounts, grayLevels] = imhist(b);
[~,c] = max(pixelCounts(:));
histBoundary = grayLevels(c);
limit = mean(histBoundary + std(double(b)));
% filter image and create binary mask
b = filterImageNoise(b, 'openAndClose', 2);
img = medfilt2(b);
img = medfilt2(img);
img(img < limit) = 0;
img(img >= limit) = 1;
imagesc(img)

end