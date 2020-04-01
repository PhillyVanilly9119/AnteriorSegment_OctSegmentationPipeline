function [seg, mns] = segmentImage(input, mask, offset1, offset2)
    
    image = createGradImg(single(input));
    adjMat = createAdjMat(image, mask, offset1, offset2);
    grph = digraph(adjMat);
    path = shortestpath(grph, 1, size(adjMat, 1));
    [pathX, pathY] = ind2sub(size(image), path);
    seg = pathX(gradient(pathY) ~= 0);
    
    sz = size(image);
    if numel(seg) > sz(2)
        seg = seg(1:sz(2));
    end
    
    mns = mean(seg);
    
end