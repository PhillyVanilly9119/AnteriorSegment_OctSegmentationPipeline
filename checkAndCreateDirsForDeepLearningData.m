%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = checkAndCreateDirsForDeepLearningData(mainDir, rawBScan, ...
    processedBScan, mask, thickOrigMask, thickMask)

% TODO: Add logic to check for existing dirs

dirList = dir(mainDir);
dirFlags = [dirList.isdir];
subFolders = dirList(dirFlags);
for k = 3 : length(subFolders)
    existingFiles{k-2} = subFolders(k).name; % add valid dirs
end

fileList = natsortfiles(existingFiles);
maxFileIdx = max(str2double(fileList)); % gets passed on from read-outs
folder = fullfile(mainDir, num2str(maxFileIdx+1,'%04.f'));
if ~exist(folder, 'dir')
    mkdir(folder)
end

imwrite(mask, fullfile(folder, 'mask.png'));
imwrite(thickMask, fullfile(folder, 'thick_interpolated_mask.png'));
imwrite(thickOrigMask, fullfile(folder, 'thick_mask.png'));
imwrite(rawBScan, fullfile(folder, 'raw_bScan.png'));
imwrite(processedBScan, fullfile(folder, 'processed_bScan.png'));

end