%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [octCube] = loadOctImages(path, aScanLength, bScanLength, imgDtTypr)

cd(path)
files = dir(strcat('*.', imgDtTypr));
nFiles = length(files);
octCube = zeros(aScanLength, bScanLength, nFiles);

for i = 1:nFiles
    if isfile(fullfile(path, files(i).name))
        tmp = imread(files(i).name);
        if length(tmp(:,1)) == aScanLength && length(tmp(1,:)) == bScanLength
            octCube(:,:,i) = tmp;
        else
            fprintf("Image NO.%0.0f has a different size than was expected!\n", i);
        end
    else
        disp("Input path does not contain a or the right file!");
    end
    octCube = uint8(octCube);
end

end