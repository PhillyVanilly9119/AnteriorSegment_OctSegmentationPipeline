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

% 2-D Plot of OVD-Thickness
figure
%Change color map so that invalid points in thickness map are changes to a
%grey shade
cmap = hot(256);
cmap(1,:) = [0.5;0.5;0.5]; % grey
colormap(cmap); % activate it
imagesc(thicknessMap)
colorbar
axis square
title('OCT OVD thickness map in µm (Z-HYALCOAT)')
ylabel('BScans')
xlabel('AScans')

% 3-D Plot of OVD-Thickness
figure
cmap = hot(256);
cmap(1,:) = [0.5;0.5;0.5]; % grey
colormap(cmap);
y = 1:64;
x = 1:64;
[X, Y] = meshgrid(x);
F = imresize(thicknessMap, [64, 64], 'bicubic');
surf(X,Y,F)
colorbar

% Count numbers within binranges
figure
ThicknessValueswithoutZero=nonzeros(thicknessMap);
threshold_thickness = 200;
treshold_mask = ThicknessValueswithoutZero > 200;
maxbin = max(thicknessMap, [], 'all');
bin_edges = 0:50:maxbin;
histogram(ThicknessValueswithoutZero(treshold_mask),bin_edges, 'FaceColor', 'red');
hold on
histogram(ThicknessValueswithoutZero(~treshold_mask),bin_edges, 'FaceColor', 'black');
hold off
title('Histogram of OVD thickness')
xlabel('OVD-Thickness in µm')
ylabel('Absolute frequency')
% relative frequency:
% histogram(ThicknessValueswithoutZero(treshold_mask),bin_edges, 'Normalization', 'probability')

binranges=[0, threshold_thickness , maxbin];
[bincounts,ind] = histc(nonzeros(thicknessMap),binranges);
percentage_thickness_greaterthan = bincounts(2,1)/numel(nonzeros(thicknessMap))


