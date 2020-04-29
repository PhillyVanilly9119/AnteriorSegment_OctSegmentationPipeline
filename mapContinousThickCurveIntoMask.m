%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask] = mapContinousThickCurveIntoMask(DataStruct, curve)

mask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

for i = 1:DataStruct.processingVolumeDims(1)
    if curve(i,1) ~= 0
        mask(curve(i,1),i) = 1; % mask(px#,i)
        % if next aScan contains segmented pixel -> interpolate continously
        if (curve(i+1,1) ~= 0) && (i < (DataStruct.processingVolumeDims(1) - 1))
            diff = curve(i,1)-curve(i+1,1); % distance in y between adjecent pixels
            diffHalf = round(diff/2);
            mask(curve(i,1):curve(i,1)+diffHalf,i) = 1;
            mask(curve(i+1,1):curve(i+1,1)-diffHalf,i) = 1;
        end
    end
    if curve(i,2) ~= 0
        mask(curve(i,2),i) = 1;
    end
end

end