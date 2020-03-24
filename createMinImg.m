function minImg = createMinImg(input)

minImg = single(input);
minImg = minImg - min(minImg(:));
minImg = minImg / max(minImg(:));

end