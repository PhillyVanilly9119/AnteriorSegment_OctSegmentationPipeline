%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [currentMaxIdx] = checkAndCreateDirsForDeepLearningData(mainDir, rawBScan, ...
    processedBScan, mask, thickOrigMask, thickMask)

[currentMaxIdx, folder] = checkForPresegmentedScans(mainDir);

imwrite(rawBScan, fullfile(folder, 'raw_bScan.png'));
imwrite(processedBScan, fullfile(folder, 'processed_bScan.png'));
imwrite(mask, fullfile(folder, 'mask.png'));
imwrite(thickOrigMask, fullfile(folder, 'thick_mask.png'));
imwrite(thickMask, fullfile(folder, 'continuous_mask.png'));

end