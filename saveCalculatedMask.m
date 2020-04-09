%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveCalculatedMask(DataStruct, curve, mask, image, maskFolder, bScanIDX)

%Resize images to original 
fac = DataStruct.loadedVolumeDims(1);

%save mask to bin-file
binID = sprintf('mask_of_bScanNo%0.0f.bin', bScanIDX);
fileID = fopen(fullfile(maskFolder, binID), 'w');
fwrite(fileID, uint8(mask));
fclose(fileID);

%save overlayed images of bScan
f = figure('visible', 'off');
imagesc(image); 
colormap gray; 
hold on, plot(curve); 
imMask1 = sprintf('mask_of_bScanNo%0.0f.png', bScanIDX);
saveas(f, fullfile(maskFolder, imMask1));
close(f)

end