%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%% type OVD name
OVD_name= 'DisCoVisc';

figure 
load('MyColormap.mat', 'OVDcolormap')
colormap(OVDcolormap)
imagesc(test2)
caxis([-10 2000])
colorbar
axis square
title(['OVD thickness map in µm (' OVD_name ')'])
ylabel('y')
xlabel('x')