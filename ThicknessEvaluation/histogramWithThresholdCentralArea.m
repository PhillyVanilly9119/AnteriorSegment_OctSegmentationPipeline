%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% histogram with threshold and central area of scanfield (3x3mm)
%%% type title of histogram
OVD_name_measurement_number= 'VISCOAT (6-2)';

%%% central map square
central_map_square = interpol_thickness_map_smooth_micron_VISCOAT_9_1(256:768, 256:768); 


%% set threshold
threshold_thickness = 50;

%% percentage of values greater than threshold
number_of_all_values_in_thicknessmap = numel(central_map_square);
number_of_values_greater_than_threshold = numel(find(central_map_square > threshold_thickness));
percentage_greater_than_threshold = number_of_values_greater_than_threshold / number_of_all_values_in_thicknessmap

%% Histogramm with all values und threshold
% Count numbers within binranges
threshold_mask = central_map_square > threshold_thickness;
bin_edges = 0:200:3000;

% figure
%absolute frequency:
histogram(central_map_square(threshold_mask),bin_edges, 'FaceColor', 'black'); hold on
histogram(central_map_square(~threshold_mask),bin_edges, 'FaceColor', 'red'); hold off

title(['OVD Schichtdickenwerte: ' OVD_name_measurement_number ' '])
xlabel('OVD Schichtdicke in µm')
xticks([0, 200, 600, 1000, 1400, 1800, 2200, 2700]);
xticklabels({'0','200','600','1000','1400','1800','2200','>2800'});
ylabel('Absolute Häufigkeit')
% ylim([0 18000000])

% plot calculate percantage in histogramm 
NE = [max(xlim) max(ylim)]-[diff(xlim) diff(ylim)]*0.05;
text(NE(1), NE(2), [num2str(percentage_greater_than_threshold*100, '%.1f')  '%'],  'VerticalAlignment','top', 'HorizontalAlignment','right', 'color', 'black')