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