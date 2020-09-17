%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% histogram with threshold and central circle area 
%%% type title of histogram: (OVD (eye - measurement repetition))
OVD_name_measurement_number= 'VISCOAT (6-2)';

%% set threshold
threshold_thickness = 150;

%%% central map: circle with diameter of 3 mm
whole_map = interpol_thickness_map_smooth_micron_TWINVISC_10_2; 

mittelpunkt_x = length(whole_map)/2;
mittelpunkt_y = length(whole_map)/2;
radius = length(whole_map)/4;

central_map_circle = NaN(length(whole_map),length(whole_map));

for i=1:size(whole_map,1)
    for j = 1:size(whole_map,2)
        if sqrt((i-mittelpunkt_x)^2+(j-mittelpunkt_y)^2) <= radius
            central_map_circle(i,j) = whole_map(i,j);
        end
    end
end


%% percentage of values greater than threshold
number_of_all_values_in_central_map_circle = sum(~isnan(central_map_circle) | central_map_circle == 0, 'all');
number_of_values_greater_than_threshold = numel(find(central_map_circle > threshold_thickness));
percentage_greater_than_threshold = number_of_values_greater_than_threshold / number_of_all_values_in_central_map_circle

%% Histogramm with all values und threshold
% Count numbers within binranges
threshold_mask = central_map_circle > threshold_thickness;
bin_edges = 0:200:3000;

% figure
%absolute frequency:
histogram(central_map_circle(threshold_mask),bin_edges, 'FaceColor', 'black'); hold on
histogram(central_map_circle(~threshold_mask),bin_edges, 'FaceColor', 'red'); hold off

%% format plot
title(['OVD Schichtdickenwerte: ' OVD_name_measurement_number ' '])
xlabel('OVD Schichtdicke in µm')
xticks([0, 200, 600, 1000, 1400, 1800, 2200, 2700]);
xticklabels({'0','200','600','1000','1400','1800','2200','>2800'});
ylabel('Absolute Häufigkeit')
% ylim([0 18000000])

%% plot calculate percantage in histogramm 
NE = [max(xlim) max(ylim)]-[diff(xlim) diff(ylim)]*0.05;
text(NE(1), NE(2), [num2str(percentage_greater_than_threshold*100, '%.1f')  '%'],  'VerticalAlignment','top', 'HorizontalAlignment','right', 'color', 'black')