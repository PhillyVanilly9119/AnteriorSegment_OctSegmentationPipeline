%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = main_CreateAdditionalMasks()

% Get mask directory
maskDims = [1024, 1024];
maskDir = uigetdir();
tmp = strsplit(maskDir, 'masks_');
% Create direcotries for additional two types of masks
contMaskFolder = fullfile(tmp{1}, strcat('continuousMasks_',tmp{end}));
if ~exist(contMaskFolder, 'dir')
    mkdir(contMaskFolder)
end
thickMaskFolder = fullfile(tmp{1}, strcat('thickMasks_',tmp{end}));
if ~exist(thickMaskFolder, 'dir')
    mkdir(thickMaskFolder)
end

% Load all (sorted!) masks
maskStack = loadMasksFromFile(maskDir, maskDims(1), maskDims(2), 'png');
sz = size(maskStack);

% Loop through masks
for i = 1:sz(3)
    fileNamecont = sprintf('maskNo%0.0f.png', i-1);
    fileNameThick = sprintf('maskNo%0.0f.png', i-1);
    contiCurves = getCurves(maskStack(:,:,i));
    continMask = mapCurveIntoMasks(sz, contiCurves);
    thickMask = thickenMask(maskStack(:,:,i), maskDims);
    imwrite(continMask, fullfile(contMaskFolder, fileNamecont));
    imwrite(thickMask, fullfile(thickMaskFolder, fileNameThick));
    
end

end


