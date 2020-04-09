%% Melli playing around

image = cdata; 

im1 = denoiseBScan(image, 60);
im2 = filterImageNoise(im1, 'openAndClose', 4);

im3 = denoiseBScan(image, 20);
im4 = filterImageNoise(im1, 'openAndClose', 3);

gradImg = createGradImg(double(im2));

figure;
imagesc(im4);
figure;
imagesc(gradImg);
figure;
plot(im4(:,75))
figure;
plot(gradImg(:,75))