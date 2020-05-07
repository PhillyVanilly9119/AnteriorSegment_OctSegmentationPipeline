%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask] = mapCurveIntoMasks(dims, curve)

mask = zeros(dims(1), dims(2));

for j = 1:dims(2)
    if curve(j,1) ~= 0 && curve(j+1,1) ~= 0 &&...
            ( round(0.02*dims(1)) > abs(curve(j+1,1)-curve(j,1)) )
        mask(curve(j,1),j) = 1;
        if curve(j,1) < curve(j+1,1)
            mask(curve(j,1)+1:curve(j+1,1),j+1) = 1;
        elseif curve(j,1) > curve(j+1,1)
            mask(curve(j+1,1)+1:curve(j,1),j+1) = 1;
        else
            mask(curve(j,1),j) = 1;
        end
    end
    
    %if a-Scan and next a-Scan ~= 0
    if curve(j,2) ~= 0 && curve(j+1,2) ~= 0 &&...
            ( round(0.02*dims(1)) > abs(curve(j+1,1)-curve(j,1)) )
        mask(curve(j,2),j) = 1;
        if curve(j,2) < curve(j+1,2)
            mask(curve(j,2)+1:curve(j+1,2),j+1) = 1;
        elseif curve(j,2) > curve(j+1,2)
            mask(curve(j+1,2)+1:curve(j,2),j+1) = 1;
        else
            mask(curve(j,2),j) = 1;
        end
    end
end

end