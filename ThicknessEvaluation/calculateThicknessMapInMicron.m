%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% calculate thickness map from px to µm

%% choose refractive index of OVD and replace "n_OVD_..." in function 
n_OVD_PROVISC        = 1.357;
n_OVD_ZHYALINPLUS    = 1.364;
n_OVD_AMVISCPLUS     = 1.356;
n_OVD_DISCOVISC      = 1.337;
n_OVD_HEALONENDOCOAT = 1.357;
n_OVD_VISCOAT        = 1.356;
n_OVD_ZHYALCOAT      = 1.343;
n_OVD_COMBIVISC      = (1.343*2+1.364)/3;
n_OVD_DUOVISC        = (1.356*2+1.357)/3;
n_OVD_TWINVISC       = (1.363*2+1.332)/3;

one_px_in_micron = 2900/1024;
scale = 1.34 * one_px_in_micron;
 

interpol_thickness_map_smooth_micron = zeros(1024, 1024);
interpol_thickness_map_smooth_micron = scale * (INTERPOL_THICKNESS_MAP_SMOOTH) / n_OVD_ZHYALINPLUS;


