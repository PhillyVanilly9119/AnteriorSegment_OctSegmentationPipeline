%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [reSzCube] = resizeOctCube(cube, widthFac)

sz = size(cube);
reSzCube = zeros(sz(1), widthFac*sz(2), sz(3));

for i = 1:sz(3)
    bScan = cube(:,:,i);
    reSzCube(:,:,i) = imresize(bScan, [sz(1), widthFac*sz(2)], 'bicubic');
end

reSzCube = uint8(reSzCube);

end