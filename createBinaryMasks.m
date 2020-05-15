%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [binaryMask, ovdMask] = createBinaryMasks(DataStruct, curve)

binaryMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));
ovdMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

for i = 1:DataStruct.processingVolumeDims(1)   
    %% binary mask #1
    % cornea is "complete" -> neccessary condition for mapping area
    if curve(i,1) ~= 0 && curve(i,2) ~= 0 
        binaryMask(curve(i,1):curve(i,2),i) = 1;
    end
    % OVD is visible -> all fom there 
    if curve(i,3) ~= 0
        binaryMask(curve(i,3):DataStruct.processingVolumeDims(1),i) = 1;
    end
    
    %% binary mask #2
    % Endothelium and OVD are visible
    if curve(i,2) ~= 0 && curve(i,3) ~= 0 
        ovdMask(curve(i,2):curve(i,3),i) = 1;
    end
    
end


end