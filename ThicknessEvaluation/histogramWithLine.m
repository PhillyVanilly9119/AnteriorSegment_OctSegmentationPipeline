%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% plot histogram with values from one OVD
%  two lines: first and second measurement
%  --> to compare the two measurement repetitions
% for that you have to load thicknessmaps of first measurement repetition as 
% "A" and of second measurement repition as "B" in workspace

figure

bin_edges = 0:200:3000;
histogram(A,bin_edges, 'DisplayStyle', 'stairs', 'edgecolor', '#D95319');hold on
histogram(B,bin_edges, 'DisplayStyle', 'stairs', 'edgecolor', '#0072BD');
legend('1. MWH','2. MWH', 'Location','north'); hold off

% format plot
xlabel('OVD Schichtdicke in µm')
xticks([0, 200, 600, 1000, 1400, 1800, 2200, 2700]);
xticklabels({'0','200','600','1000','1400','1800','2200','>2800'});
ylabel('Absolute Häufigkeit')
ylim([0 18000000])

title(['OVD Schichtdicke: Kombisysteme'])