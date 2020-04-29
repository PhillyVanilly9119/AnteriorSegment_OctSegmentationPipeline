%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveContAndThickMasks(DataStruct, contMask, thickMask, bScanIDX)

contMaskFolder = DataStruct.contMaskFolder;
thickMaskFolder = DataStruct.thickMaskFolder;

name = sprintf('maskNo%0.0f.png', bScanIDX);

imwrite(contMask, fullfile(contMaskFolder, name));
imwrite(thickMask, fullfile(thickMaskFolder, name));

end