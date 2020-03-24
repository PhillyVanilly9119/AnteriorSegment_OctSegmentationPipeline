%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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