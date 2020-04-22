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

thicknessMap = imresize(thicknessMap, [128, 512]);

Median_OvdThickness = median(nonzeros(thicknessMap))
Mean_OvdThickness = mean(nonzeros(thicknessMap)')

figure
imagesc(thicknessMap)
colorbar
axis square
title('2D Falschfarbenprojektion der OVD-Schicht in µm (Z-HYALCOAT)')
ylabel('BScans')

figure
surf(thicknessMap)
