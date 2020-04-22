%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%loading of the masks
dir = uigetdir();
maskVolume = loadMasksFromFile(dir, 1024, 1024, 'png');
maskVolume(maskVolume==255)=1;

% all masks in 3D matrix (1024, 1024, 128)
maskSZ = size(maskVolume);

% zero matrix (128, 1024)
thicknessMap = zeros(maskSZ(3), maskSZ(2));

for i = 1:maskSZ(3)
    onemask = maskVolume(:,:,i);
    thicknessMap(i,:) = calculateThicknessPerBscan(onemask);
end

thicknessMap = round(abs(imresize(thicknessMap, [128, 512], 'bicubic')));
%%TODO: think about if rounding to interger multiples of µm is valid in
%%this case...
% thicknessMap = abs(imresize(thicknessMap, [128, 512], 'bicubic'));

Median_OvdThickness = median(nonzeros(thicknessMap))
Mean_OvdThickness = mean(nonzeros(thicknessMap))
NumberofValues_OvdThickness = numel(nonzeros(thicknessMap))

figure
%Change color map so that invalid points in thickness map are changes to a
%grey shade
cmap = hot(256);
cmap(1,:) = [0.5;0.5;0.5]; % grey
colormap(cmap); % activate it
imagesc(thicknessMap)

axis square
title('2D Falschfarbenprojektion der OVD-Schicht in µm (Z-HYALCOAT)')
ylabel('BScans')

% figure
% surf(thicknessMap)
