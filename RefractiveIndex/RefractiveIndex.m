clc
clear

fname = 'C:\C Drive Folder\Data\OVD\CALLISTOeye_1 mm kuevette_-2\OD-2020-06-03_101357.fs\000.bmp';

bscan = imread(fname);

figure(1)
imagesc(bscan)

rois = ginput(2);
rois = round(rois);

bscan = bscan(rois(1,2):rois(2,2),rois(1,1):rois(2,1));

figure(1)
imagesc(bscan)

avgAscan = mean(bscan,2);

[pks,locs,w,p] = findpeaks(avgAscan, 'MinPeakHeight', 70, 'MaxPeakWidth', 40, 'MinPeakProminence', 30);

x = [0.3 0.5];
y = [0.6 0.5];

figure(2)
plot(avgAscan)
hold on
sc = scatter(locs,pks);
for ii = 1:length(locs)
    dt = datatip(sc, locs(ii), pks(ii));
end
hold off
xlim([0 1024])
ylim([0 255])

refractiveIndex = (locs(3)-locs(1)) / (locs(2)-locs(1))



