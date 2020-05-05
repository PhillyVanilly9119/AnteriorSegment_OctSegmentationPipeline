%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveEmptyMask(DataStruct, mask, bScanIDX)

maskFolder = DataStruct.maskFolder;

%save mask to bin-file
binID = sprintf('mask_of_bScanNo%0.0f.bin', bScanIDX);
fileID = fopen(fullfile(maskFolder, binID), 'w');
fwrite(fileID, uint8(mask));
fclose(fileID);

maskNumber = sprintf('mask_of_bScanNo%0.0f.png', bScanIDX);

%save mask as image;
imwrite(mask, fullfile(maskFolder, maskNumber));

end