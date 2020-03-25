%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveCalculatedMask(mask, maskFolder, bScanIDX)
    
    %save bin-file
    binID = sprintf('mask_of_bScanNo%0.0f.bin', bScanIDX);
    fileID = fopen(fullfile(maskFolder, binID), 'w');
    fwrite(fileID, uint8(mask));
    fclose(fileID);
    
    %save images
    imMask1 = sprintf('mask_of_bScanNo%0.0f_Cornea.png', bScanIDX);
    imMask2 = sprintf('mask_of_bScanNo%0.0f_OVA.png', bScanIDX);
    imwrite(mask(:,:,1),fullfile(maskFolder, imMask1))
    imwrite(mask(:,:,2),fullfile(maskFolder, imMask2))

end