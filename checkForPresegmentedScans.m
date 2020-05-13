%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [currentMaxIdx, folder] = checkForPresegmentedScans(mainDir)

dirList = dir(mainDir);
dirFlags = [dirList.isdir];
subFolders = dirList(dirFlags);
if length(subFolders) > 2
    for k = 3 : length(subFolders)
        existingFiles{k-2} = subFolders(k).name;
    end
    
    fileList = natsortfiles(existingFiles);
    maxIdx = max(str2double(fileList));
    currentMaxIdx = maxIdx+1;
    folder = fullfile(mainDir, num2str(currentMaxIdx,'%04.f'));
    if ~exist(folder, 'dir')
        mkdir(folder)
    end
    
else
    maxIdx = 0;
    currentMaxIdx = maxIdx;
    folder = fullfile(mainDir, num2str(maxIdx+1,'%04.f'));
    if ~exist(folder, 'dir')
        mkdir(folder)
    end
    
end

end