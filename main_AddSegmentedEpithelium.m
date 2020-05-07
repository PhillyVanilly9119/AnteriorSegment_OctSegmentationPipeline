%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Main function
function [] = main_AddSegmentedEpithelium(ML_DataDir)

% directories
mainDir = uigetdir();
tmp = strsplit(mainDir, '\');
maskDir = fullfile(mainDir, 'Segmented_Data', strcat('masks_',tmp{end}));

% load b-Scans and Masks
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Careful when using this function outside of the context of this script
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
masks = loadMasksAndDeleteOldOnes(maskDir, 1024, 1024, 'png');
rawBScans = loadBScanImages(mainDir, 1024, 512, 'bmp');
bScans = resizeOctCube(rawBScans, 2);
bScans = applyFixedFilters(bScans);

sz = size(rawBScans);
mSz = size(masks);

% segment masks and overwrite old masks 
for j = 1:sz(3)
    [addedMask] = findEpitheliumPosition(bScans(:,:,j), masks(:,:,j));
    newMask = double(masks(:,:,j)) + addedMask;
    thickOrigMask = thickenMask(newMask, mSz, 0);
    thickMask = thickenMask(newMask, mSz, 0);
    checkAndCreateDirsForDeepLearningData(ML_DataDir, rawBScans(:,:,j), ...
    bScans(:,:,j), newMask, thickOrigMask, thickMask)
end

end


%% Auxiliary function(s)
function [newMask] = findEpitheliumPosition(image, mask)

% assert same sizes of image and mask
% assert((logical(1, 1) == size(mask) == size(image)), "image and mask dimension mismatch");
% normalize mask -> Check if necessary in the way the masks are loaded
mask(mask==255) = 1;
sz = size(mask);
% create vars
newMask = zeros(sz(1), sz(2));
% segment boundary spots bScan
pts = selectPointsManually(image, "Please select Epithelium. Finish with double-clokc on last point");
% Interpolate parabola through points
fittedEpi = interpolateQuadFctInRange(pts, min(pts(:,1)):max(pts(:,1)));
% fittedEpi = interpolateBetweenSegmentedPoints(pts, sz(1), sz(2));
% post-check of fitted curve
fittedEpi(fittedEpi > sz(1)) = sz(1);
fittedEpi(fittedEpi < 0) = 0;
fittedEpi = round(fittedEpi);

% write curve into mask
for i = 1:sz(1)
    if fittedEpi(i) ~= 0
        newMask(fittedEpi(i),i) = 1;
    end
end

end


