%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [masks] = loadMasksAndDeleteOldOnes(path, aScanLength, bScanLength, imgDtTypr)

cd(path)
delete *.bin
files = dir(strcat('*.', imgDtTypr));
cellStruct = struct2cell(files);
unsorted = cellStruct(1,:);
sorted = natsortfiles(unsorted);
masks = zeros(aScanLength, bScanLength, length(sorted));

for i = 1:length(sorted)
    if isfile(fullfile(path, sorted{i}))
        tmp = imread(sorted{i});
        if length(tmp(:,1)) == aScanLength && length(tmp(1,:)) == bScanLength
            masks(:,:,i) = tmp;
        else
            fprintf("Image NO.%0.0f has a different size than was expected!\n", i);
        end
    else
        disp("Input path does not contain a or the right file!");
    end
   
end

%delete *.png % delete all current masks
masks = uint8(masks);

end
