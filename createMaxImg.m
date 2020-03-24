function maxImg = createMaxImg(input)

    maxImg = single(input);
    maxImg = maxImg - min(maxImg(:));
    maxImg = maxImg / max(maxImg(:));
    maxImg = 1 - maxImg;
    
end