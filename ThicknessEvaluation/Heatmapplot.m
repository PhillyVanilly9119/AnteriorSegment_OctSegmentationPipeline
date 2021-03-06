%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% plot heatmap with colorbar
% field of view 6x6 mm
% load the thicknessmap [�m] (line 24) into workspace and choose title


%% type OVD name
OVD_name             = 'DUOVISC ()';

%% load colormap: 
% "mymap" is specified with threshold at 200 �m and maximum value at 2800 �m
figure 
load('MyColormap.mat', 'mymap')
colormap(mymap)

%% load thicknessmap
whole_map            = interpol_thickness_map_smooth_micron_ZHYALINPLUS_10_2; 
imagesc(whole_map)

%% format plot
caxis([0 2830])

%  colorbar values
colorbar
colorbar('Ticks',[0, 200, 600, 1000, 1400, 1800, 2200, 2600, 2830], 'TickLabels',{'0','200','600','1000','1400','1800','2200','2600','>2800'});
  
%  title of colorbar
t                     = sgtitle('[�m]            ');
t.HorizontalAlignment = 'right';
t.FontSize            = 9;

% format x- and y-axis
% title and ticks for [mm] values
axis square
title(['OVD Schichtdicke: ' OVD_name ''])
ylabel('y [mm]')
yticks([1 170.7 341.3 512 682.7 853.3 1024])
yticklabels({'6','5','4','3','2','1','0'})
xlabel('x [mm]')
xticks([1 170.7 341.3 512 682.7 853.3 1024])
xticklabels({'0','1','2','3','4','5','6'})


%% save updated colormap:
% ax = gca;
% mymap = colormap(ax);
% save('MyColormap','mymap')