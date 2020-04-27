%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%                         Note: LOI* = Layer of interest
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [segmImg, curve] = segmentAScanDerivative(image, label, frames)

% globals
sz = size(image);
offset = 30; %offset from found of ENDO-boundary
curve = zeros(sz(1), 2);
segmImg = zeros(sz(1),sz(2));

%% Filter bScan on aScan-basis: Find extrema (i.e. bScans' layer boundaries)
endoVec = frames(1,1):frames(2,1);
ovdVec = frames(1,2):frames(2,2);

for i = 1:sz(1)
    aScan = abs(diff(image(:,i))); %calculate derivate along a-Scan
    
    % Map points in range of endothelium
    if all(i >= min(endoVec) & i <= max(endoVec)) && label ~= 0
        [~, posesCornea] = maxk(aScan, 10); %TODO: once filters are working properly check whole aScan lenght
        posEndo = max(posesCornea); %find Endo in Cornea
        if ~isempty(posEndo)
            curve(endoVec(i-min(endoVec)+1),1) = posEndo + offset;
        end
    end
    
    % Map points in range of OVD
    if all(i >= min(ovdVec) & i <= max(ovdVec)) && label == 2
        [~, posesOVD] = maxk(aScan(posEndo+offset:end), 3); %find OVD
        posOVD = min(posesOVD);
        if ~isempty(posOVD)
            curve(ovdVec(i-min(ovdVec)+1),2) = posOVD + (posEndo+offset);
        end
    end
    
end

% nonZ = curve(curve(:,2)>0);
% nonZ(nonZ<prctile(nonZ,75)) = prctile(nonZ,75);
% windowWidth = 3; 
% kernel = ones(windowWidth,1) / windowWidth;
% out = filter(kernel, 1, nonZ);
% curve(ovdVec-1,2) = out;

%% Fit the two curves
%Endothel -> if == 0-vector, retuns still a 0-vector
endoPolCoeffs = polyfit(endoVec, curve(endoVec,1)', 2);
fittedEndothel = polyval(endoPolCoeffs, min(endoVec):max(endoVec));
for i = min(endoVec):max(endoVec)
    curve(i,1) = round(fittedEndothel(i-min(endoVec)+1));
end
curve(:,2) = round(curve(:,2));
%value boundaries after segmentation
curve(curve > 1024) = 1024;
curve(curve < 0) = 0;

%% Write boarders into Mask
%TODO: Write (all available i.e non-0 curves) into segemented mask (segmImg)
for i = 1:sz(1)
    if curve(i,1) ~= 0
        segmImg(curve(i,1),i) = 1;
    end
    if curve(i,2) ~= 0
        segmImg(curve(i,2),i) = 1;
    end
end

sSz = size(segmImg);
if sSz(1) ~= sz(1) || sSz(2) ~= sz(2)
    disp("Segmented mask has wrong dimensions!")
    return
end

end