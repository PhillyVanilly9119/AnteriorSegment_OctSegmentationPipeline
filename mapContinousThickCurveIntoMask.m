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
        mask(curve(i,1)-1:curve(i,1)+1,i) = 1;
    end
    if curve(i,2) ~= 0
        mask(curve(i,2)-1:curve(i,2)+1,i) = 1; % mask(px#,i)
        % if "next aScan contains continuous segmented pixel
        % -> interpolate continously"
        if (curve(i+1,2) ~= 0) && (i < (DataStruct.processingVolumeDims(1) - 1)) &&...
                (curve(i+1,2) ~= curve(i,2) || curve(i+1,2) ~= curve(i,2)-1 || curve(i+1,2) ~= curve(i,2)+1)
            diffHalf = round( (curve(i,2)-curve(i+1,2)) / 2 );
            if diffHalf > 0 % positive slope of boundary layer
                mask( curve(i,2) : curve(i,2) - diffHalf, i ) = 1;
                mask( curve(i+1,2) + diffHalf : curve(i+1,2), i ) = 1;
            else % negative slope of boundary layer
                mask( curve(i,2) : curve(i,2) + diffHalf, i ) = 1;
                mask( curve(i+1,2) : curve(i+1,2) - diffHalf, i ) = 1;
            end
        end
    end
end

% Thicken lines through 2x 2D-interpolation
intImg = interp2(double(mask));
mask = interp2(double(intImg));
mask = imresize(mask,[DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2)]);
mask(mask>0) = 1;

end