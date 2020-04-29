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
thickness = zeros(1,sz(2));

for i = 1:sz(2)
%     if ~unique(onemask(:,i)==1)
    if nnz(onemask(:,i)) == 2
        thickness(1,i) = scale * ( (find(onemask(:,i), 1, 'last')) - find(onemask(:,i), 1, 'first') ) / n_ovd ;
        if thickness(1,i) == 0
            thickness(1,i) = 1;
        end
    else
        thickness(1,i) = 0;
    end
end


end
