%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%                   @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [renderVolume] = createAndSaveRenderVolume()
%% Globals
a = 1024;
b = 1024;
c = 128;
renderVolume = zeros(a,b,c);

%% Load data
path = uigetdir();
scans = loadOctImages(path, 1024, 512, 'bmp');
scans = resizeOctCube(scans, 2);
masks = loadMasksFromFile(uigetdir(path), a, b, 'png');
masks(masks>0) = 255;

%% Make render-volume pretty
for i = 1:c
    renderVolume(:,:,i) = scans(:,:,i);
    mask = masks(:,:,i);
    for j = 1:b
        boundaries = find(mask(:,j)==255);
        if length(boundaries) == 3
            % Denoise vacant areas in volume
            renderVolume(1:boundaries(1),j,i) = 0;
            renderVolume(boundaries(2):boundaries(3),j,i) = 0;
            % Emphasize boundaries via mask overlay
            mask(boundaries(1)-1:boundaries(1)+1,j) = 255;
            mask(boundaries(2)-1:boundaries(2)+1,j) = 255;
            if boundaries(3) < 1024
                mask(boundaries(3)-1:boundaries(3)+1,j) = 255;
            else 
                mask(boundaries(3)-2:boundaries(3),j) = 255;
            end
        end
    end
    renderVolume(:,:,i) = uint8(renderVolume(:,:,i)) + mask;
    % Normalize vals?
end

%% Interpolate rendered volume
c = 1024;
% renderVolume = uint8(renderVolume;
outVol = zeros(a,b,c);
for ii = 1:a
    for jj = 1:b
        outVol(i,j,:) = interp1(1:128, squeeze(renderVolume(ii,jj,:)), ...
            linspace(1,128,1024), 'PCHIP');
    end
end

% Save images
saveDataCubeAsBinFile(path, strcat('renderVolume_uint8', '_', num2str(a), 'x', num2str(b), 'x', num2str(c),'.bin'), uint8(outVol));
disp('Saved Data Cube in selected path!')

end