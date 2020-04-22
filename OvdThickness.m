%loading of the masks
dir = uigetdir();
maskVolume = loadOctImages(dir, 1024, 1024, 'png');
maskVolume(maskVolume==255)=1;

% all masks in 3D matrix (1024, 1024, 128)
maskSZ = size(maskVolume);

% zero matrix (128, 1024)
thicknessMap = zeros(maskSZ(3), maskSZ(2)); 

for i = 1:maskSZ(3)
   onemask = maskVolume(:,:,i);
   thicknessMap(i,:) = calculateThicknessPerBscan(onemask);
end 

Median_OvdThickness = median(find(thicknessMap),'all')
Mean_OvdThickness = mean(find(thicknessMap),'all')

imagesc(thicknessMap)
colorbar
title('2D Falschfarbenprojektion der OVD-Schicht')
