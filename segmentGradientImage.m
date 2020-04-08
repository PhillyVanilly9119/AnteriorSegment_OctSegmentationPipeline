%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%                         Note: LOI* = Layer of interest
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [segmImg, curve] = segmentGradientImage(image, label, nExtrema)
%% Preprocessing
% globals
sz = size(image);
curve = zeros(sz(1), 2);
segmImg = zeros(sz(1),sz(2));
gradImg = createGradImg(single(image));

%% Filter bScan on aScan-basis
% TODO: Try alternatively with derivative of a-Scan
a = 1;
windowSize = 15;
b = (1/windowSize)*ones(1,windowSize);
filteredAScans = zeros(sz(1), sz(2));
for i = 1:sz(1)
    filteredAScans(:,i) = filter(b,a,gradImg(:,i));
end

%% Find extrema (i.e. bScans' boaders)
% 1): Endothelium
qtr = round(sz(1)/4);
hlf = round(sz(1)/2);
endoVec = hlf-qtr:(hlf+qtr-1);
for i = 1:length(endoVec)
    [~, cMax] = maxk(filteredAScans(:,i+qtr), nExtrema);
    [~, cMin] = mink(filteredAScans(:,i+qtr), nExtrema);
    if label == 1 %if only ENDO is visible
        %Endo-layer is last max-layer
        curve(i+qtr,1) = round(mean(cMax(end), cMin(end)));
    elseif label == 2 %if both OVD and ENDO are visible
        %Endo-layer is second to last max-layer
        curve(i+qtr,1) = round(mean(cMax(end-1), cMin(end-1)));
    else %of no LOI* is visible
        curve(i+qtr,1) = 0;
    end
end

% 2): OVD
for i = 1:sz(1)
    [~, cMax] = maxk(filteredAScans(:,i), nExtrema);
    [~, cMin] = mink(filteredAScans(:,i), nExtrema);
    if label == 2
        curve(i,2) = round(mean(cMax(end), cMin(end)));
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