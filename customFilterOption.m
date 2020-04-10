%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filtVol] = customFilterOption(DataStruct, vol)

% 2) manually selected pre-segementation image-filter-options
sz = size(vol);
if isfield(DataStruct, 'flag_isGoodImgQual') && ~DataStruct.flag_isGoodImgQual
    imshow(vol(:,:,round(DataStruct.imageVolumeDims(3)/2)));
    title("Sample b-Scan of volume to evaluate image quality")
    [DataStruct.flag_isGoodImgQual, filtVol] = filterVolume(vol);
else
    filtVol = vol;
end

while ~DataStruct.flag_isGoodImgQual
    close all
    imshow(filtVol(:,:,round(sz(3)/2)));
    title("B-Scan at the middle of the pre-processed volume")
    pause(2);
    
    answer = questdlg('Would you like to continue to apply image filter?', ...
        'Is the image qualitey satisfying to start segmentation?', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            [DataStruct.flag_isGoodImgQual, filtVol] = filterVolume(filtVol);
        case 'No'
            DataStruct.flag_isGoodImgQual = 1;
    end
    
    close all
    
end

end

