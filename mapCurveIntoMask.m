%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask] = mapCurveIntoMask(DataStruct, curve)

mask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

for i = 1:DataStruct.processingVolumeDims(1)
    if curve(i,1) ~= 0
        mask(curve(i,1),i) = 1;
    end
    if curve(i,2) ~= 0
        mask(curve(i,2),i) = 1;
    end
    if curve(i,3) ~= 0
        mask(curve(i,3),i) = 1;
    end
end

end