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

%Histogram
b = OctDataCube(:,:,1);
[pixelCounts, grayLevels] = imhist(b);
[~,c] = max(pixelCounts(:));
limit = grayLevels(c);
b(b < std(double(b))+limit) = 0;
% b(b > limit) = 1;
imagesc(b)

end