%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [edgesBScan] = detectEdges(image, factor)

edgesBScan = edge(image, factor, 'log');

end