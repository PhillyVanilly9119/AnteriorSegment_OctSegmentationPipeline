%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask, continuousMask, thickMask, binaryMask] = createAllMasks(DataStruct, curve)

mask = mapCurveIntoMask(DataStruct, curve);
continuousMask = mapContinousCurveIntoMask(DataStruct, curve);
thickMask = thickenMask(continuousMask, DataStruct.processingVolumeDims, 0);
binaryMask = createBinaryMask(DataStruct, curve);

end