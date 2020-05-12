%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%                         Note: LOI* = Layer of interest
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask, curve] = segmentAScanDerivative(image, label, frames)

% globals
sz = size(image);
offset = 30; %offset from cornea-boundary
curve = zeros(sz(1), 3);
mask = zeros(sz(1),sz(2));
qtr = round(sz(2)/4);
hlf = round(sz(2)/2);
polInt = hlf-qtr:hlf+qtr-1;
% filter params
windowWidthOVD = 21;
windowWidthEpi = 35; 
windowWidthEndo = 51; 
kernelOVD = ones(windowWidthOVD,1) / windowWidthOVD ;
kernelEpi = ones(windowWidthEpi,1) / windowWidthEpi;
kernelEndo = ones(windowWidthEndo,1) / windowWidthEndo;

%% Filter bScan on aScan-basis: Find extrema (i.e. bScans' layer boundaries)
corneaVec = frames(1,1):frames(2,1);
ovdVec = frames(1,2):frames(2,2);

for i = 1:sz(1)
    aScan = abs(diff(image(:,i))); %calculate derivate along a-Scan
    
    % Map points in range of epithelium
    if all(i >= min(corneaVec) & i <= max(corneaVec)) && label ~= 0
        [~, posesCornea] = maxk(aScan, 20); %TODO: once filters are working properly check whole aScan lenght
        posEndo = min(posesCornea); %find Endo in Cornea
        if ~isempty(posEndo)
            curve(corneaVec(i-min(corneaVec)+1),1) = posEndo + offset;
        end
    end
    
    % Map points in range of endothelium
    if all(i >= min(corneaVec) & i <= max(corneaVec)) && label ~= 0
        [~, posesCornea] = maxk(aScan, 20); %TODO: once filters are working properly check whole aScan lenght
        posEndo = max(posesCornea); %find Endo in Cornea
        if ~isempty(posEndo)
            curve(corneaVec(i-min(corneaVec)+1),2) = posEndo + offset;
        end
    end
    
    % Map points in range of OVD
    if all(i >= min(ovdVec) & i <= max(ovdVec)) && label == 2 && exist('posEndo', 'var')
        [~, posesOVD] = maxk(aScan(posEndo+offset:end), 3); %find OVD
        posOVD = min(posesOVD);
        if ~isempty(posOVD)
            curve(ovdVec(i-min(ovdVec)+1),3) = posOVD + (posEndo+offset);
        end
    end
    
end

%% Fit the two curves
% FILTER Epithelium
curve(:,1) = filter(kernelEpi, 1, curve(:,1));
curve(:,2) = filter(kernelEndo, 1, curve(:,2));

% INTERPOLATE Cornea layers
epiPolCoeffs = polyfit(polInt, curve(polInt,1)', 2);
fittedEpithel = polyval(epiPolCoeffs, min(corneaVec):max(corneaVec));
endoPolCoeffs = polyfit(polInt, curve(polInt,2)', 2);
fittedEndothel = polyval(endoPolCoeffs, min(corneaVec):max(corneaVec));
% round interpolated parabola values
for i = min(corneaVec):max(corneaVec)
    curve(i,1) = round(fittedEpithel(i-min(corneaVec)+1));
    curve(i,2) = round(fittedEndothel(i-min(corneaVec)+1));
end

% filter and round OVD-boundary layer
curve(:,3) = filter(kernelOVD, 1, curve(:,3));
curve(:,3) = round(curve(:,3));
% Catch out-of-image-size-errors
curve(curve > 1024) = 1024;
curve(curve < 0) = 0;

%% Write boarders into Mask
%TODO: Write (all available i.e non-0 curves) into segemented mask (segmImg)
for i = 1:sz(1)
    if curve(i,1) ~= 0
        mask(round(curve(i,1)),i) = 1;
    end
    if curve(i,2) ~= 0
        mask(round(curve(i,2)),i) = 1;
    end
    if curve(i,3) ~= 0
        mask(round(curve(i,3)),i) = 1;
    end
end

sSz = size(mask);
if sSz(1) ~= sz(1) || sSz(2) ~= sz(2)
    disp("Segmented mask has wrong dimensions!")
    return
end

end