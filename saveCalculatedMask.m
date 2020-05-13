%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveCalculatedMask(DataStruct, curve, mask, image, frames, bScanIDX)

maskFolder = DataStruct.maskFolder;
% binFolder = DataStruct.dataFolder;

%Resize images to original 
% fac = DataStruct.loadedVolumeDims(1);

% % save mask to bin-file
% binID = sprintf('mask_of_bScanNo%0.0f.bin', bScanIDX-1);
% fileID = fopen(fullfile(maskFolder, binID), 'w');
% fwrite(fileID, uint8(mask));
% fclose(fileID);

%save overlayed images of bScan
f = figure('visible', 'off');
imagesc(image); 
colormap gray; 
hold on
plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),1))
% condition if ONLY Endothelium is visible
if frames(1,2) ~= 0 && frames(2,2) ~= 0
    plot(frames(1,2):frames(2,2), curve(frames(1,2):frames(2,2),2)) 
end
maskNumber = sprintf('maskNo%0.0f.png', bScanIDX-1);
% saveas(f, fullfile(binFolder, maskNumber));
close(f)

%save mask as image
imwrite(mask, fullfile(maskFolder, maskNumber));

end