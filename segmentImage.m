function [seg, mns] = segmentImage(input, mask, v)

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