%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filteredBScan] = applySavitzkyGolay(bScan, order, window)

filteredBScan = zeros(size(bScan));
bScan = double(bScan);
sz = size(bScan);

for i = 1:sz(2)
    filteredBScan(:,i) = sgolayfilt(bScan(:,i), order, window);
end

filteredBScan = uint8(filteredBScan);

end