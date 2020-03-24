%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [octData] = loadOctDataFromBinFile(path, file, a, b, c)

finalPath = fullfile(path, file);
octData = zeros(a,b,c);

if isfile(finalPath)
    f = fopen(finalPath, 'rb');
    octData = fread(f, a * b * c, 'uint8', 'ieee-le');
    octData = reshape(data, [a,b,c]);
    fclose(f);
else
    disp("Input path does not contain a file!");
end

end