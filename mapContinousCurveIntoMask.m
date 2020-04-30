%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask] = mapContinousCurveIntoMask(DataStruct, curve)

mask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

for i = 1:DataStruct.processingVolumeDims(1)
    
    %if a-Scan and next a-Scan ~= 0
    if curve(i,1) ~= 0 && curve(i+1,1) ~= 0
        mask(curve(i,1),i) = 1;
        if curve(i,1) < curve(i+1,1)
            mask(curve(i,1)+1:curve(i+1,1),i+1) = 1;
        elseif curve(i,1) > curve(i+1,1)
            mask(curve(i+1,1)+1:curve(i,1),i+1) = 1;
        else
            mask(curve(i,1),i) = 1;
        end
    end
    
    %if a-Scan and next a-Scan ~= 0
    if curve(i,2) ~= 0 && curve(i+1,2) ~= 0
        mask(curve(i,2),i) = 1;
        if curve(i,2) < curve(i+1,2)
            mask(curve(i,2)+1:curve(i+1,2),i+1) = 1;
        elseif curve(i,2) > curve(i+1,2)
            mask(curve(i+1,2)+1:curve(i,2),i+1) = 1;
        else
            mask(curve(i,2),i) = 1;
        end
    end
end

% delta = curve(i,2) - curve(i+1,2); % current-next (aScan) [fl2r]
% 
% if mod(abs(delta),2) == 0 && abs(delta) > 1 % even deltas, i.e. ISSUES with d/2
%     if delta > 0 % positive slope: \ <=> y(x2) > y(x1)
%         mask( ( curve(i,2) - abs(floor(delta/2)) ) : curve(i,2), i) = 1; 
%         mask( curve(i+1,2) : ( curve(i+1,2) + abs(floor(delta/2)) -1 ), i+1) = 1;  
%     elseif delta < 0 % negative slope: / <=> y(x2) < y(x1)
%         
%     else % if delta == 1, do nothing -> next pixel 0° or 45° away, i.e. adjacent
%         mask(curve(i,2),i) = 1; % just write current pixel in mask
%     end
%     
% elseif mod(abs(delta),2) == 1 && abs(delta) > 1 % uneven deltas, i.e. NO issus with d/2
%     if delta > 0 % positive slope: \ <=> y(x2) > y(x1)
%         mask( curve(i,2): ( curve(i,2) + floor(delta/2) ), i) = 1; 
%         mask( ( curve(i+1,2) - floor(delta/2) ) : curve(i+1,2), i+1) = 1; 
%     elseif delta < 0 % negative slope: / <=> y(x2) < y(x1)
%         mask( ( curve(i,2) - abs(floor(delta/2)) ) : curve(i,2) , i) = 1; 
%         mask( curve(i+1,2) : ( curve(i+1,2) + abs(floor(delta/2))), i+1) = 1; 
%     else % if delta == 1, do nothing -> next pixel 0° or 45° away, i.e. adjacent
%         mask(curve(i,2),i) = 1; % just write current pixel in mask
%     end
%     
% else % delta = 1 or 0 -> next pixel is continuous, i.e. 0° or 45°
%     mask(curve(i,2),i) = 1;
%     
% end


end