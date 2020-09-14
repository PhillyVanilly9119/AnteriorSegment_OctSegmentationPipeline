%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%% type OVD name
OVD_name= 'DUOVISC ()';

figure 
load('MyColormap.mat', 'mymap')
colormap(mymap)

whole_map = interpol_thickness_map_smooth_micron_VISCOAT_9_1; 
imagesc(whole_map)

caxis([0 2830])
colorbar
colorbar('Ticks',[0, 200, 600, 1000, 1400, 1800, 2200, 2600, 2830], 'TickLabels',{'0','200','600','1000','1400','1800','2200','2600','>2800'});

t = sgtitle('[µm]            ');
t.HorizontalAlignment = 'right';
t.FontSize = 9;

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