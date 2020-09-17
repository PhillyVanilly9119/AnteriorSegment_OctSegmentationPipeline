%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% type title of histogram
OVD_name_measurement_number= 'Kombisysteme 1. MWH';

%% calculate thickness map from px to micron
% choose refractive index of OVD and replace "n_OVD_..." in function 
% for combined systems there is a weighted mean value calculated:
% 2/3 dispersive OVD and 1/3 cohesive OVD

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
scale = 1.34 * one_px_in_micron; % 1.34 is calculated in RESCAN
  
% interpol_thickness_map_smooth_micron = zeros(1024, 1024);
% interpol_thickness_map_smooth_micron = scale * (INTERPOL_THICKNESS_MAP_SMOOTH) / n_OVD_ZHYALINPLUS;
interpol_thickness_map_smooth_micron = A;

%% set threshold
threshold_thickness = 200;

%% percentage of values greater than threshold
number_of_all_values_in_thicknessmap = numel(interpol_thickness_map_smooth_micron);
number_of_values_greater_than_threshold = numel(find(interpol_thickness_map_smooth_micron > threshold_thickness));
percentage_greater_than_threshold = number_of_values_greater_than_threshold / number_of_all_values_in_thicknessmap

%% Histogramm with all values und threshold
% Count numbers within binranges
threshold_mask = interpol_thickness_map_smooth_micron > 200;
bin_edges = 0:200:3000;

figure
%absolute frequency:
histogram(interpol_thickness_map_smooth_micron(threshold_mask),bin_edges, 'FaceColor', 'black'); hold on
histogram(interpol_thickness_map_smooth_micron(~threshold_mask),bin_edges, 'FaceColor', 'red'); hold off

title(['OVD Schichtdickenwerte: ' OVD_name_measurement_number ' '])
xlabel('OVD Schichtdicke in µm')
xticks([0, 200, 600, 1000, 1400, 1800, 2200, 2700]);
xticklabels({'0','200','600','1000','1400','1800','2200','>2800'});
ylabel('Absolute Häufigkeit')
ylim([0 18000000])

% plot calculated percantage in histogramm (top left corner)
NE = [max(xlim) max(ylim)]-[diff(xlim) diff(ylim)]*0.05;
text(NE(1), NE(2), [num2str(percentage_greater_than_threshold*100, '%.1f')  '%'],  'VerticalAlignment','top', 'HorizontalAlignment','right', 'color', 'black')