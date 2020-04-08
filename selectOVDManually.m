%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [intPts] = selectOVDManually(image, n)

sz = size(image);

if nargin < 2
    n = Inf;
    pts = zeros(2, 0);
else
    pts = zeros(2, n);
end
imshow(image);% display image of which the layers should be segmented

xold = 0;
yold = 0;
k = 0;
hold on;           % and keep it there while we plot

while 1
    [xi, yi, but] = ginput(1);      % get a point
    if ~isequal(but, 1)             % stop if not button 1
        break
    end
    k = k + 1;
    pts(1,k) = xi;
    pts(2,k) = yi;
    if xold
        plot([xold xi], [yold yi], 'go-');  % draw as we go
        text = sprintf("%0.0f Point(s) remaining for segmentation of layer OVD-margin",...
            n-k);
        title(text)
    else
        plot(xi, yi, 'go'); % first point on its own
    end
    if isequal(k, n)
        break
    end
    xold = xi;
    yold = yi;
end
hold off;
if k < size(pts,2)
    pts = pts(:, 1:k);
end

intPts = interpolateSegmentedPoints(pts, sz(2), sz(1));

close(gcf)

end