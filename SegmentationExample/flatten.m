close all;

clear all;
folderName = "D:\EyeClinic\220120\D6\60deg\";
fileName = "1024x3072x2000x3_12905";

ending = ".bin";
fileStruc = strcat(folderName, "struc_", fileName, ending);
fileFlow = strcat(folderName, "flow_", fileName, ending);
fileFlowDefolded = strcat(folderName, "flowfl_", fileName, ending);
fileStrucDefolded = strcat(folderName, "strucfl_", fileName, ending);

parts = split(fileName, "_");
dims = split(parts(1), "x");

a = str2double(dims(1));
b = str2double(dims(2));
c = str2double(dims(3));

name = parts(2);

bofs = 0;

%%
%settings

v = 0.03;
treshold = 15;

vRm = 0.01;
sigma = 0.7;
sigmaTr = 3;
sigMImg = 4;
slfc = 0.7;

rpeWidthF = 5;

rpeWidth = 40;
ilmWidth = 20;
ilmOffs = 20;
chorWidth = 100;
retWidth = 300;

dcWidth = 50;

%find rpe
roiSelect = 1;
roiTRLSelect = 15;

vertOffs = 3;
%vertOffs = round(rpeWidth * (b/a));

minSize = 200;

% fileSettings = strcat(folderName, "settings_flatten.mat");
% load(fileSettings);

%
rstrd = floor(b/50);
sstrd = 3;
%%
%header

disp("flattening");
disp("==========");
disp(" ");

disp(strcat("a: ", num2str(a)));
disp(strcat("b: ", num2str(b)));
disp(strcat("c: ", num2str(c)));
disp(" ");

disp(strcat("v: ", num2str(v)));
disp(strcat("vRm: ", num2str(vRm)));
disp(strcat("sigMImg: ", num2str(sigMImg)));
disp(strcat("treshold: ", num2str(treshold)));
disp(strcat("rpeWidth: ", num2str(rpeWidth)));
disp(strcat("ilmWidth: ", num2str(ilmWidth)));
disp(strcat("dcWidth: ", num2str(dcWidth)));
disp(strcat("roiSelect: ", num2str(roiSelect)));
disp(strcat("roiTRLSelect: ", num2str(roiTRLSelect)));
disp(" ");

disp("start flattening...");
disp(" ");

%%
%detect onh
disp("create enface");
enface = zeros(b, c);

enfaceMask = zeros(b, c, "int8");

fStruc = fopen(fileStruc, "rb");
for i = 1:c
    bscan = fread(fStruc, [a, b], "uint8=>single");
    proj = mean(bscan, 1);
    enface(:, i) = proj;
end
fclose(fStruc);

% filterX = 5;
% filterY = 5;
% sigmaEf = 5;
% 
% ffimg = fft2(enface);
% ffimg(filterY:end-filterY, 1:filterX) = 0;
% ffimg(filterY:end-filterY, end:end-filterX) = 0;
% ffimg(1:filterX, filterY:end-filterY) = 0;
% ffimg(end:end-filterX, filterY:end-filterY) = 0;
% enface = abs(ifft2(ffimg));

% senface = imgaussfilt(enface, sigmaEf);
% [~, mi] = max(senface(:));
% [mx, my] = ind2sub(size(enface), mi);
% 
% onhWidth = 150;
% onhHeight = 150;
% 
% sx = mx - floor(onhWidth/2);
% ex = mx + floor(onhWidth/2);
% sy = my - floor(onhHeight/2);
% ey = my + floor(onhHeight/2);
% 
% roi = enface(sx:ex, sy:ey);
% projX = mean(roi, 1);
% projY = mean(roi, 2);

figure, imagesc(enface);
[x, y] = ginput(2);
x = round(x);
y = round(y);

enfaceMask(y(1):y(2), x(1):x(2)) = -1;
% enfaceMask(850:1150, 830:1030) = -1;
% enfaceMask(550:620, 380:440) = -2;

figure
subplot(2, 1, 1), imagesc(enface);
subplot(2, 1, 2), imagesc(enfaceMask);
    
%%
fStruc = fopen(fileStruc, "rb");
fseek(fStruc, a*b*bofs, 0);
fFlow = fopen(fileFlow, "rb");
fseek(fFlow, a*b*bofs, 0);

fStrucOut = fopen(fileStrucDefolded, "wb");
fseek(fStrucOut, a*b*bofs, 0);
fFlowOut = fopen(fileFlowDefolded, "wb");
fseek(fFlowOut, a*b*bofs, 0);

%%
%process
disp("segment");

oi = 0;
for i = 1:c
    disp(strcat("bscan: ", num2str(i)));
    
    oi = oi + 1;
    
    bscan = fread(fStruc, [a, b], "uint8=>uint8");
    flow = fread(fFlow, [a, b], "uint8=>uint8");

    bscanTr = bscan - treshold;
    bscanTr(bscanTr < treshold) = 0; 
    
    %smooth bscan
    sbscan = imgaussfilt(bscanTr, sigmaTr);
    %sbscan = bscan;
    
%     sbscan = bscan;
%     cmat = [1 1 1; 1 1 1; 1 1 1];
%     sbscan = conv2(sbscan, cmat);
%     sbscan = sbscan(2:a+1, 2:b+1);

    %get roi
    projZ = mean(sbscan, 1);
    projX = mean(sbscan, 2);
    
    for j = 1:b
        if projZ(j) > roiSelect
            break;
        end
    end
    roiZl = j;
    
    for j = b:-1:1
        if projZ(j) > roiSelect
            break;
        end
    end
    roiZr = j;
    
    for j = dcWidth:a
        if projX(j) > roiSelect
            break;
        end
    end
    roiXl = j;
    
    for j = a:-1:dcWidth
        if projX(j) > roiSelect
            break;
        end
    end
    roiXr = j;
    
    %skip roi detection
%     roiXl = 1;
%     roiXr = a;
%     roiZl = 1;
%     roiZr = b;
    
    roiTr = sbscan(roiXl:roiXr, roiZl:roiZr);
    roi = bscan(roiXl:roiXr, roiZl:roiZr);
    roi = imgaussfilt(roi, sigma);
    [ar, br] = size(roi);
    
    roiTr = [roiTr; zeros(rpeWidth + chorWidth, br)];
    roi = [roi; zeros(rpeWidth + chorWidth, br)];
    [ar, br] = size(roi);
    
    if ar == 0 || br < minSize
        bscan = zeros(a, b);
        flow = zeros(a, b);
        
        fwrite(fStrucOut, bscan, "uint8");
        fwrite(fFlowOut, flow, "uint8");
        
        if ar == 0
            disp("skipped (ar = 0)");
        else
            disp("skipped (br < minSize)");
        end
        
        continue;
    end

    st = bscan(roiXl:roiXr, roiZl:roiZr);
    st = [st; zeros(rpeWidth + chorWidth, br)];
    
    fl = flow(roiXl:roiXr, roiZl:roiZr);
    fl = [fl; zeros(rpeWidth + chorWidth, br)];
    
    %select enface Mask line
    efMline = enfaceMask(roiZl:roiZr, i+bofs);
    
    %create mask
    mask = zeros(ar, br, "int8");

    %perform coarse flattening and crop ret
    coarseRpeSeg = zeros(br, 1);
    coarseRoiTr = imgaussfilt(roi, 3*sigmaTr);
    for j = 1:br
        ascan = coarseRoiTr(:, j);
        
        [mx, s] = max(ascan);
        
        if mx < 5*mean(ascan)
            s = 0;
            coarseRpeSeg(j) = nan;
        else
            coarseRpeSeg(j) = s;
        end
        
        s = s - retWidth;
        if s < 1
            s = 1;
        end
        if s > ar
            s = ar;
        end
        
        e = s + 2*retWidth;
        if e < 1
            e = 1;
        end
        if e > ar
            e = ar;
        end
        
        roiTr(1:s, j) = 0;
        roiTr(e:end, j) = 0;
    end

    %detect zero crossing
    [~, mdl] = max(coarseRpeSeg);
            
    lside = coarseRpeSeg(1:mdl);
    mn = min(lside);
    for sj = numel(lside):-1:1
        if lside(sj) == mn
            break;
        end
    end
    brl = sj;
    
    rside = coarseRpeSeg(mdl:end);
    mn = min(rside);
    for sj = 1:1:numel(rside)
        if rside(sj) == mn
            break;
        end
    end
    brr = sj + 1;
    brr = brr + mdl;
    
    if brl ~= 1
        retl = brl + vertOffs;
    else
        retl = 1;
    end
    if  brr ~= br
        retr = brr - vertOffs;
    else
        retr = br;
    end
    
    if retl < 1 || retr > br
        retl = 1;
        retr = br;
    end
    
    %skip flip detection
    retl = 1;
    retr = br;
    
    %find centroid line
    cln = [];
    oj = 0;
    for j = [retl:rstrd:retr-rstrd retr]
        if j > br
            break;
        end
        
        ascan = roiTr(:, j);
        oj = oj + 1;
        
        sm = sum(ascan);
        it = int32(0);
        
        for sj = 1:ar
            it = it + int32(ascan(sj));
            if it > sm/2
                break;
            end
        end
        
        cln(oj, 1) = sj;
        cln(oj, 2) = j;
    end

    nel = size(cln, 1);
    
    %skip if nel too small
    if nel <= 2*sstrd
        bscan = zeros(a, b);
        flow = zeros(a, b);
        
        fwrite(fStrucOut, bscan, "uint8");
        fwrite(fFlowOut, flow, "uint8");
        
        disp("skipped (nel too small)");
        
        continue;
    end
    
    %smooth
    cln(1:sstrd, 3) = cln(1:sstrd, 1);
    cln(end-sstrd:end, 3) = cln(end-sstrd:end, 1);
    for j = sstrd:nel-sstrd
        s = j - sstrd + 1;
        e = j + sstrd;
        
        cln(j, 3) = mean(cln(s:e, 1));
    end 
    
    ft = fit(cln(:, 2), cln(:, 3), "linearinterp");
    cline = ft(1:br);
    devCline = gradient(cline);
    cline = round(cline);
    
    %find start
    oj = 0;
    strt = [];
    for j = [retl:rstrd:retr-rstrd retr]
        if j > br
            break;
        end
        
        ascan = roiTr(:, j);
        mx = max(ascan);
        oj = oj + 1;

        for sj = cline(j)-retWidth:ar
            s = sj;
            if s < 1
                s = 1;
            end
            if s > ar
                s = ar;
            end

            if ascan(s) > roiTRLSelect
                break;
            end
        end
        
        strt(oj, 1) = s + round(ilmOffs/(abs(devCline(j)) + 1));
        strt(oj, 2) = j;
    end
    
    %smooth
    strt(1:sstrd, 3) = strt(1:sstrd, 1);
    strt(end-sstrd:end, 3) = strt(end-sstrd:end, 1);
    nel = size(strt, 1);
    for j = sstrd:nel-sstrd
        s = j - sstrd + 1;
        e = j + sstrd;
        
        strt(j, 3) = mean(strt(s:e, 1));
    end 
    
    %find end
    oj = 0;
    endl = [];
    for j = [retl:rstrd:retr-rstrd retr]
        if j > br
            break;
        end
        
        ascan = roiTr(:, j);
        mx = max(ascan);
        oj = oj + 1;

        for sj = ar:-1:cline(j)
            e = sj;
            if e < 1
                e = 1;
            end
            if e > ar
                e = ar;
            end

            if ascan(e) > roiTRLSelect
                break;
            end
        end
        
        endl(oj, 1) = e;
        endl(oj, 2) = j;
    end
    
    %smooth
    endl(1:sstrd, 3) = endl(1:sstrd, 1);
    endl(end-sstrd:end, 3) = endl(end-sstrd:end, 1);
    nel = size(endl, 1);
    for j = sstrd:nel-sstrd
        s = j - sstrd + 1;
        e = j + sstrd;
        
        endl(j, 3) = mean(endl(s:e, 1));
    end 

    sline = round(interp1(strt(:, 2), strt(:, 3), 1:br, "linear", "extrap"));
    sline(sline < 1) = 1;
    eline = round(interp1(endl(:, 2), endl(:, 3), 1:br, "linear", "extrap"));
    eline(sline < 1) = 1;
    
    %limit center of mass to centroid
    mline = round((eline + sline)/2);
    for j = 1:br
        if cline(j) < mline(j)
            cline(j) = mline(j);
        end
    end
    cline(cline < 1) = 1;
    
    %mask start line
    for j = retl:retr
        if sline(j) > cline(j)
            s = cline(j);
        else
            s = sline(j);
        end
        e = s + ilmWidth;
        
        mask(s:e, j) = 1;
    end

    clf;
    subplot(5, 1, 1), imagesc(roiTr);
    hold on, plot(cline);
    hold on, plot(sline);
    hold on, plot(eline);
    legend("cline", "sline", "eline");
    title(strcat("bscan: ", num2str(i)));
    
    shift = -cline + floor(ar/2);
    
    %apply enfaceMask
    mn = mean(roi(:));
    for j = 1:br
        if efMline(j) == -1
            roi(:, j) = mn;
        end
    end
    
    %mask
    diff = retr - retl;
    retlb = retl + floor(diff/10);
    retrb = retr - floor(diff/10);
    
    mask(end-shift(retlb), retlb) = 1;
    mask(end-shift(retrb):end, retrb) = 1;
    for j = retlb:retrb
        %mask dc
        mask(1:floor(dcWidth/2), j) = 1;
        mask(end-floor(dcWidth/2):end, j) = 1;
    end

    for j = retl:retr
        mask(:, j) = circshift(mask(:, j), shift(j), 1);
    end
   
    %shift
    for j = 1:br
        roi(:, j) = circshift(roi(:, j), shift(j), 1);
        
        e = ar - shift(j);
        if e > ar
            e = ar;
        end
        if e < 1
            e = 1;
        end
        
        st(e:end, j) = 0;
        st(:, j) = circshift(st(:, j), shift(j), 1);
        fl(e:end, j) = 0;
        fl(:, j) = circshift(fl(:, j), shift(j), 1);
    end

    %segment 3 times for rpe and ilm
    seg = [];
    
    gradImg = createGradImg(single(roi));
    [seg(1, :), mns(1)] = segment(gradImg, mask, v);
    
    %plot 1th seg
    subplot(5, 1, 2), imagesc(gradImg);
    hold on, plot(seg(1, :));
    
    %mask seg1
    for j = retl:retr
        s = seg(1, j) - floor(rpeWidth/2);
        if s < 1
            s = 1;
        end
        e = seg(1, j) + floor(rpeWidth/2);
        if e > ar
            e = ar;
        end

        mask(s:e, j) = 1;
    end
    mask(1:dcWidth, :) = 1;
    mask(end-dcWidth-rpeWidth-chorWidth:end, :) = 1;
    
    %seg 2nd time
    [seg(2, :), mns(2)] = segment(gradImg, mask, v);
    
    %plot 2nd seg
    hold on, plot(seg(2, :));
    legend("seg1", "seg2");
    
    %mask seg2
    for j = retl:retr
        s = seg(2, j) - floor(rpeWidth/2);
        if s < 1
            s = 1;
        end
        e = seg(2, j) + floor(rpeWidth/2);
        if e > ar
            e = ar;
        end

        mask(s:e, j) = 1;
    end
    mask(1:dcWidth, :) = 1;
    mask(end-dcWidth-rpeWidth-chorWidth:end, :) = 1;
    
    %seg 3nd time
    [seg(3, :), mns(3)] = segment(gradImg, mask, v);
    
    %exclude coroid line
    seg(3, :) = ar;
    mns(3) = ar;
    
    %plot 2nd seg
    hold on, plot(seg(3, :));
    legend("seg1", "seg2", "seg3");
    
    [~, mni] = sort(mns);
    
    %choose if rpe or ilm
    ilm = seg(mni(1), :);
    rpe = seg(mni(2), :);
    chr = seg(mni(3), :);
   
    %flatten
    %define shift at rpe and set everything above ilm to 0
    
    %plot
    subplot(5, 1, 3), imagesc(mask);
    hold on, plot(rpe);
    hold on, plot(ilm);
    hold on, plot(chr);
    legend("rpe", "ilm", "chr");
    
    %segment maximum of rpe
    %mask rpe
    
    mask = zeros(rpeWidthF*rpeWidth, br);
    mask(1, :) = 1;
    mask(end, :) = 1;
    
    %mask with chor
    for j = retl:retr
        %mask ilm in max search
        ilms = -(rpe(j) - ilm(j)) + floor(rpeWidthF/2)*rpeWidth + 1;
        if ilms > 0
            mask(1:ilms, j) = 1;
        end
        
        %mask chor in max search
        s = (chr(j) - rpe(j)) + floor(rpeWidthF/2)*rpeWidth + 1;
        if s < 1
            s = 1;
        end
        if s > ar
            s = ar;
        end
        
        mask(s:end, j) = 1;
    end
   
    roi = [roi; zeros(rpeWidthF*rpeWidth, br)];
    rpeRoi = zeros(rpeWidthF*rpeWidth, br);
    for j = 1:br
        s = rpe(j) - floor(rpeWidthF/2)*rpeWidth + 1;
        if s < 1
            s = 1;
        end
        
        e = s + rpeWidthF*rpeWidth - 1;
        
        %extract rpe
        rpeRoi(:, j) = roi(s:e, j);
    end
    
    %segment along maximum
    gradImg = createGradImg(rpeRoi);
    segRpeG = segment(gradImg, mask, vRm);

    maxImg = createMaxImg(rpeRoi);
    maxImg = imgaussfilt(maxImg, sigMImg);
    slope = linspace(1, slfc, size(rpeRoi, 1))';
    for j = 1:br
        maxImg(:, j) = maxImg(:, j) .* slope;
    end
    segRpeB = segment(maxImg, mask, vRm);
    
    cList = [];
    ci = 1;
    for j = 2:br-1
        if efMline(j) == 0 && efMline(j+1) == -1
            cList(ci, 1) = j+1;
        end
        
        if efMline(j) == -1 && efMline(j+1) == 0
            cList(ci, 2) = j;
            ci = ci + 1;
        end
    end
    cList(cList == 0) = 2;
    
    if ci > 1
        for j = 1:ci-1
            s = cList(j, 1);
            e = cList(j, 2);
            
            segRpeB(s:e) = round(linspace(segRpeB(s-1), segRpeB(e+1), e-s+1));
        end
    end

    %plot
    subplot(5, 1, 4), imagesc(rpeRoi);
    hold on, plot(segRpeB);
    hold on, plot(segRpeG);
    
    %average between max and grad
%     segRpe = segRpeB;
    segRpe = segRpeG;
%     segRpe = floor((segRpeB + segRpeG) / 2);
    
    hold on, plot(segRpe);
    legend("Max", "Grad", "Avg");
    
    %set above ilm to 0
%     for j = 1:br
%         st(1:ilm(j)-ilmWidth, j) = 0;
%         fl(1:ilm(j)-ilmWidth, j) = 0;
%     end

    %shift
    
    %shift = -rpe + floor(ar/2);
    shift = -(rpe + segRpe) + floor(ar/2);
    for j = 1:br
        s = ar - shift(j);
        if s < 1
            s = 1;
        end
        if s > ar
            s = ar;
        end
        
        roi(:, j) = circshift(roi(:, j), shift(j), 1);
        st(s:end, j) = 0;
        st(:, j) = circshift(st(:, j), shift(j), 1);
        fl(s:end, j) = 0;
        fl(:, j) = circshift(fl(:, j), shift(j), 1);
    end
    
    %stretch data to needed size
    bscan = zeros(a, b);
    flow = zeros(a, b);
    alen = roiXr - roiXl;
    an = floor(a/2) - floor(alen/2);
    bscan(an:an+alen, roiZl:roiZr) = st(1:alen+1, :);
    flow(an:an+alen, roiZl:roiZr) = fl(1:alen+1, :);
    
    %save
    fwrite(fStrucOut, bscan, "uint8");
    fwrite(fFlowOut, flow, "uint8");
    
    %plot
    subplot(5, 1, 5), imagesc(bscan);
    pause(0.1);
end

%%

fclose(fStruc);
fclose(fFlow);
fclose(fStrucOut);
fclose(fFlowOut);

%%

% %save enface
% enface = enface - min(enface(:));
% enface = enface/max(enface(:));
% 
% imwrite(enface', fileEnface);

disp(" ");
disp(" ");

%%

function minImg = createMinImg(input)
    minImg = single(input);
    
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