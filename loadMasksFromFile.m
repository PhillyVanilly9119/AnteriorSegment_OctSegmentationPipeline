%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [octCube] = loadMasksFromFile(path, aScanLength, bScanLength, imgDtTypr)

cd(path)
files = dir(strcat('*.', imgDtTypr));
cellStruct = struct2cell(files);
unsorted = cellStruct(1,:);
sorted = natsortfiles(unsorted);
octCube = zeros(aScanLength, bScanLength, length(sorted));

for i = 1:length(sorted)
    if isfile(fullfile(path, sorted{i}))
        tmp = imread(sorted{i});
        if length(tmp(:,1)) == aScanLength && length(tmp(1,:)) == bScanLength
            octCube(:,:,i) = tmp;
        else
            fprintf("Image NO.%0.0f has a different size than was expected!\n", i);
        end
    else
        disp("Input path does not contain a or the right file!");
    end
   
end

octCube = uint8(octCube);

end
