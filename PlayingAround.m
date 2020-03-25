%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% playing aroung

% Calculate the volumes SNR
%[octSNR, ~] = calculateAvgSNR(filteredOctCube);

fltBScan = filteredOctCube(:,:,64);
cubeSz = size(fltBScan);
fltBScan = filteredOctCube(:,:,64);
%fltBScan = imbinarize(fltBScan);
f_img = filterImageNoise(fltBScan, 'open', 2);
f_img = filterImageNoise(f_img, 'closeAndOpen', 2);
f_img = f_img(1:512,:);
f_img = imbinarize(f_img);
f_img = filterImageNoise(f_img, 'open', 3);
f_img = detectEdges(f_img, 0.001);
imshow(f_img);



%% Apply image filter (playing around)
% noise = mean2(bScan(512-100:512+100,256-25:256+25));
% noise = mean2(bScan(end-25:end,:));
% rescaled = denoiseBScan(bScan, 50);
% meded = filterImageNoise(rescaled, 'median', 1);
% filtered = filterImageNoise(meded, 'openAndClose', 2);
% figure; imshow(rescaled);
% weighted = (((1/max(max(double(bScan)))) * double(bScan))) + ((1/max(max(double(rescaled)))) * double(rescaled));
% figure; imshow(weighted);
% figure; imshow(filterImageNoise(weighted, 'openAndClose', 2));

% figure; imshow(filterImageNoise(bScan, 'closeAndOpen', 2));
% figure; imshow(detectEdges(bScan, .005, 'log'))
% smoothAScans = smoothenAScans(bScan, 3, 25); % Params: image, Order, Length
% figure; plot(bScan(:,512)); hold on; plot(smoothAScans(:,512));
% figure; imshow(smoothAScans)