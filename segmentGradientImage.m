%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%                         Note: LOI* = Layer of interest
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% TODO: Try if different filter coeffs for both boarders
% TODO: Rethink and test ranges in which layers are being calculated

function [segmImg, curve] = segmentGradientImage(image, label)
%% Preprocessing
% globals
sz = size(image);
offset = 10; % pixels from (n,0) in image that are ignores for calculations
curve = zeros(sz(1), 2);
segmImg = zeros(sz(1),sz(2));
gradImg = createGradImg(single(image));

%% Filter bScan on aScan-basis
%% Find extrema (i.e. bScans' boaders)
a = 1;
windowSize = 7;
b = (1/windowSize)*ones(1,windowSize);

filteredAScans = zeros(sz(1), sz(2));
eigth = round(sz(1)/8);
qtr = round(sz(1)/4);
half = round(sz(1)/2);
endoVec = half-qtr:(half+qtr-1);
ovdVec = half-eigth:(half+eigth-1);

nExt = 3; %3 layers: epi, endo and ovd

for i = 1:sz(1)
    aScan = gradImg(:,i); %Placeholder
    aScan = filter(b,a,aScan); %Filter derivate
    aScan = normalizeAScan(aScan); %Normalize for comparability
    filteredAScans(:,i) = aScan;
    
    %find extrema
    [~, cMax] = maxk(aScan(offset:end-offset), nExt);
    [~, cMin] = mink(aScan(offset:end-offset), 2*nExt);
    
    %for every max in a-Scan find clostest min
    for ii = 1:nExt % length(cMax)
        [~,idx] = min(round(abs(cMin-cMax(ii))));
        boundarySpot(ii) = round(mean([cMin(idx), cMax(ii)]));
    end
    
    % Map points in range of OVD
    if all(i >= min(endoVec) & i <= max(endoVec)) && label ~= 0
        curve(endoVec(i-min(endoVec)+1),1) = boundarySpot(2);
    end
    
    % Map points in range of endothelium
    if all(i >= min(ovdVec) & i <= max(ovdVec)) && label == 2
        curve(ovdVec(i-min(ovdVec)+1),2) = boundarySpot(3);
    end
    
end

%% Fit the two curves
%Endothel -> if == 0-vector, retuns still a 0-vector
endoPolCoeffs = polyfit(endoVec, curve(endoVec,1)', 2);
fittedEndothel = polyval(endoPolCoeffs, 1:sz(1));
curve(:,1) = round(fittedEndothel);
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