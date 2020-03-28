%opens a modal dialog box that displays the folders in the current working directory and returns the path that the user selects from the dialog box.
dir = uigetdir();
%displays the current folder
cd(dir);
fileIn = 'bscan.png';

image = imread(fileIn);
sz = size(image);
mask = zeros(sz(1), sz(2));

im = createGradImg(single(image));
[seg, mns] = segment(im, mask, 1e-7);

figure
imagesc(image);
colormap gray;
hold on, plot(seg)

%% Main processing functions

function minImg = createMinImg(input)
    minImg = single(input);
    
     %wie kommt man auf folgende Befehle? Differenz und dann Division? auch
     %bei folgenden functions
    minImg = minImg - min(minImg(:));
    minImg = minImg / max(minImg(:));
end

function maxImg = createMaxImg(input)
    maxImg = single(input);
    
    maxImg = maxImg - min(maxImg(:));
    maxImg = maxImg / max(maxImg(:));
    
    maxImg = 1 - maxImg;
end

function gradImg = createGradImg(input)
    sz = size(input);
    %Array of NaN
    segImg = nan(sz);
    
    for i = 1:sz(2)
        segImg(:,i) = -gradient(input(:, i), 2);
    end
    
    segImg = segImg - min(segImg(:));
    segImg = segImg / max(segImg(:));
    
    gradImg = segImg;
end

function [seg, mns] = segment(input, mask, v)
    adjMat = createAdjMat(input, mask, v, 1e-7);
    grph = digraph(adjMat);
    path = shortestpath(grph, 1, size(adjMat, 1));
    [pathX, pathY] = ind2sub(size(input), path);
    seg = pathX(gradient(pathY) ~= 0);
    
    sz = size(input);
    if numel(seg) > sz(2)
        seg = seg(1:sz(2));
    end
    mns = mean(seg);
end