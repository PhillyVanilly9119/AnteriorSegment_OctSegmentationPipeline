%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [segmImg] = segmentGradientImage(image)

sz = size(image);
image = single(image);
segmImg = zeros(sz(1),sz(2));

gradImg = createGradImg(image);

for i = 1:sz(2)
    [val, col] = maxk(gradImg(:,i), 1); %3 because of the 3 expected layers
    segmImg(col, i) = val;
    %    mPts(:,i) = mink(gradImg(:,i), 3); % also 3 because I dont yet understand the gradient
end

%% think of logic for a loop to subsequently find max values on endothel
% -> find logic start/ boundary condition at image margins
% A = rand([15 129])*100; %matrix with random values
% [~,I] = min(abs(A - 15),[],1); %get indices for values closest to 15
% logicalMat = false(size(A)); %preallocate logical matrix
% arrayLength = size(A,2);
% for jj = 1:arrayLength
%     logicalMat(I(jj),jj) = 1; %fill logical matrix
% end

imagesc(segmImg);

end