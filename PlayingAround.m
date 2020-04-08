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


%% Segmentation
%____________________________________________________
% %% Try by finding mean (slope) of upcoming 5 values
% qtr = round(sz(1)/4);
% hlf = round(sz(1)/2);
% n = 3; %number if mins and maxes per row
% for i = 1:length(hlf-qtr:hlf+qtr)-1 %-4 cause shortest nect 3 values are averaged
%     [~, posMax] = maxk(gradImg(:,i+qtr), n);
%     if i > 1
%         for ii = 1:n
%             dists(ii) = abs(meanNextMaxCurve(i-1) - posMax(ii));
%         end
%         [~, shortestNN] = min(dists);
%         meanNextMaxCurve(i) = posMax(shortestNN);
%     else
%         meanNextMaxCurve(i) = round(mean(posMax(:,i)));
%     end
% end
%
% figure;
% imagesc(gradImg);
% colormap gray;
% hold on, plot(hlf-qtr:(hlf+qtr-1), meanNextMaxCurve);
%
% p = polyfit(1:sz(1), meanNextMaxCurve, 2);
% fitMeanNextMaxCurve = polyval(p, 1:sz(1));
%
% figure;
% imagesc(gradImg);
% colormap gray;
% hold on, plot(curve);
% im = gradImg(1:300,256:3*256);
% sz = size(im);
% imshow(im)
%
%
% BW1 = edge(image, 'Sobel', 'vertical');
% BW2 = edge(image, 'log', 0.0001);
% imshowpair(BW1,BW2,'montage')
% colormap gray;

%_______________________________________________________
% %% Find curve based on differeces if extrema (per row)
% % mean(max(col)-max(col))

% qtr = round(sz(1)/4);
% hlf = round(sz(1)/2);
% n = 4; %number if mins and maxes per row
% for i = 1:length(hlf-qtr:hlf+qtr)-1
%     [~, posMax] = maxk(gradImg(:,i+qtr), n);
%     [~, posMin] = mink(gradImg(:,i+qtr), n);
%     maxMinDiffs = zeros(n, n);
%     for ii = 1:length(posMax)
%         maxMinDiffs(ii,:) = abs(posMax(ii) - posMin);
%     end
%     [r,c] = find(maxMinDiffs == min(maxMinDiffs(:)));
%     extDiffCurve(i) = abs(mean(posMax(r(1)), posMin(c(1))));
% end
% % fit polynominal
% pCoeffs = polyfit(hlf-qtr:(hlf+qtr-1), extDiffCurve, 2);
% fitExtDifCurve = polyval(pCoeffs, 1:sz(1));
% %plot
% figure; imagesc(gradImg);
% colormap gray;
% hold on, plot(1:sz(1), fitExtDifCurve);
% plot(hlf-qtr:(hlf+qtr-1), extDiffCurve)

%_____________________________________________________
% %%Try by finding the most consecutive values == 0.5 (
% boarders are that after resizing)
%
% for i = 1:sz(1)
%     deltas = diff(gradImg(:,i));
%     [r,~] = find(deltas == 0);
%     counter = 1;
%     for ii = 1:(length(r)-1)
%         if r(ii)+1 == r(ii+1)
%             counter = counter + 1;
%             tracking(ii) = counter;
%         else
%             counter = 1;
%             tracking(ii) = counter;
%         end
%         [~,pos] = max(tracking);
%         curve(i) = r(pos);
%     end
%     clear tracking
% end
%
% filtered = sgolayfilt(curve(100:200), 2, length(100:200));
% % filtered = sgolayfilt(filtered, 2, sz(1)-1);
% figure;
% imagesc(gradImg);
% colormap gray;
% hold on, plot(100:200, filtered);