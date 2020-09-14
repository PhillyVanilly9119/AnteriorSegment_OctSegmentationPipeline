%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% type OVD name
OVD_name= 'DisCoVisc';

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

%% 2-D Plot of OVD-Thickness
figure
%Change color map so that invalid points in thickness map are changes to a
%grey shade

load('MyColormap.mat', 'OVDcolormap')
colormap(OVDcolormap)

cmap = hot(256);
cmap(1,:) = [1;1;1]; % grey
colormap(cmap); % activate it
imagesc(thickness)
colorbar
axis square
title(['OVD thickness map in µm (' OVD_name ')'])
ylabel('BScans')
xlabel('AScans')


%% 3-D Plot of OVD-Thickness
figure
cmap = hot(256);
cmap(1,:) = [0, 0.9, 0.1]; % grey

% threshold = 200;
% cmap = hot(256, lower=threshold, upper = max)
% 
% displayMap = thicknessMap(thicknessMap < threshold)

colormap(cmap);
y = 1:64;
x = 1:64;
[X, Y] = meshgrid(x);
F = imresize(thicknessMap, [64, 64], 'bicubic');
surf(X,Y,F)
colorbar

%% Histogramm with all valid values
% Count numbers within binranges
figure
ThicknessValueswithoutZero=nonzeros(thicknessMap);
threshold_thickness = 200;
threshold_mask = ThicknessValueswithoutZero > 200;
maxbin = max(thicknessMap, [], 'all');
bin_edges = 0:50:maxbin;

%absolute frequency:
histogram(ThicknessValueswithoutZero(threshold_mask),bin_edges, 'FaceColor', 'red'); hold on
histogram(ThicknessValueswithoutZero(~threshold_mask),bin_edges, 'FaceColor', 'black'); hold off

title(['Histogram of OVD thickness (' OVD_name ')'])
xlabel('OVD-Thickness in µm')
ylabel('Absolute frequency')
ylim([0 6000])

%% calculate percentage above threshold (all valid values)
binranges=[0, threshold_thickness , maxbin];
[bincounts,ind] = histc(nonzeros(thicknessMap),binranges);
percentage_thickness_greaterthan = bincounts(2,1)/numel(nonzeros(thicknessMap))

% plot calculate percantage in histogramm 
NE = [max(xlim) max(ylim)]-[diff(xlim) diff(ylim)]*0.05;
text(NE(1), NE(2), [num2str(percentage_thickness_greaterthan*100) '%'],  'VerticalAlignment','top', 'HorizontalAlignment','right', 'color', 'red')

% relative frequency:
% histogram(ThicknessValueswithoutZero(threshold_mask),bin_edges, 'Normalization', 'probability')



%% Histogramm with all valid values in centre area (3 mm diameter)
% Count numbers within binranges
figure
ThicknessValueswithoutZero=nonzeros(thicknessMap(43:86, 171:342));
threshold_thickness = 200;
threshold_mask = ThicknessValueswithoutZero > 200;
maxbin = max(thicknessMap(43:86, 171:342), [], 'all');
bin_edges = 0:50:maxbin;

%absolute frequency:
histogram(ThicknessValueswithoutZero(threshold_mask),bin_edges, 'FaceColor', 'red'); hold on
histogram(ThicknessValueswithoutZero(~threshold_mask),bin_edges, 'FaceColor', 'black'); hold off

title('Histogram of OVD thickness in centre area diameter 3 mm (DisCoVisc)')
xlabel('OVD-Thickness in µm')
ylabel('absolute frequency')


%% calculate percentage above threshold (all valid values within 3 mm centre area)
binranges=[0, threshold_thickness , maxbin];
[bincounts,ind] = histc(nonzeros(thicknessMap(43:86, 171:342)),binranges);
percentage_thickness_greaterthan_centre_area = bincounts(2,1)/numel(nonzeros(thicknessMap(43:86, 171:342)))

% plot calculate percantage in histogramm (centre area)
NE = [max(xlim) max(ylim)]-[diff(xlim) diff(ylim)]*0.05;
text(NE(1), NE(2), [num2str(percentage_thickness_greaterthan_centre_area*100) '%'],  'VerticalAlignment','top', 'HorizontalAlignment','right', 'color', 'red')
