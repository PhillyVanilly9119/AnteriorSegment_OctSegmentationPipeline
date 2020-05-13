%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [interpolatedMask] = thickenMask(mask, maskDims, flag_keepRealValues)

interpolatedMask = interp2(double(mask));
interpolatedMask = imresize(interpolatedMask, [maskDims(1), maskDims(2)] );
if flag_keepRealValues == 1
    interpolatedMask(interpolatedMask~=0) = 1;
end

end