%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [currentMaxIdx] = checkAndCreateDirsForDeepLearningData(mainDir, rawBScan, ...
    processedBScan, mask, continuousMask, thickMask, binaryMask, inverseBinMask)

currentMaxIdx = checkForPresegmentedScans(mainDir);
folder = fullfile(mainDir, num2str(currentMaxIdx, '%04.f'));
if ~exist(folder, 'dir')
    mkdir(folder);
end

%TODO add folder putside of check fuction
imwrite(rawBScan, fullfile(folder, 'raw_bScan.png'));
imwrite(processedBScan, fullfile(folder, 'processed_bScan.png'));
imwrite(mask, fullfile(folder, 'mask.png'));
imwrite(continuousMask, fullfile(folder, 'continuous_mask.png'));
imwrite(thickMask, fullfile(folder, 'thick_mask.png'));
imwrite(binaryMask, fullfile(folder, 'binary_mask.png'));
imwrite(inverseBinMask, fullfile(folder, 'inverse_bin_mask.png'));

end