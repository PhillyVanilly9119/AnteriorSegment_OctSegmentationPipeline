%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [thickness] = calculateThicknessPerBscan(onemask)

one_px_in_micron = 2900/1024;
n_ovd = 1.333412;
scale = 1.34 * one_px_in_micron;
sz = size(onemask);
% sz = size(mask); %[1024, 1024] = [länge, breite]
thickness = NaN(1,sz(2));
% thickness = zeros(1,sz(2));

firstlayerindex = zeros(1, sz(2));
% % make first layer (Epithelium) to zero -> not necesarry (only for
% Machine Learning Data)
%   onemask(  (find(onemask(:,i), 1, 'first')) , : ) = NaN;
 for j = 1:sz(2)
   firstlayerindex(1,j) = find(onemask(:,j), 1, 'first');
   onemask(firstlayerindex(1,j), j) = 0;
 end


for i = 1:sz(2)
        
    if nnz(onemask(:,i)) == 2      
        thickness(1,i) = scale * ( (find(onemask(:,i), 1, 'last')) - find(onemask(:,i), 1, 'first') ) / n_ovd ;
%         if thickness(1,i) == 0
%             thickness(1,i) = 1;
%         end
%     else
%         thickness(1,i) = NaN;
%     end
end


end
