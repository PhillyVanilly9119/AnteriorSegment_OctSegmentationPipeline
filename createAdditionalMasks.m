%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = createAdditionalMasks()

%Get mask directory
maskDims = [1024, 1024];
maskDir = uigetdir();
tmp = strsplit(maskDir, '\masks_');
%create direcotries for other two types of masks
contMaskFolder = fullfile(tmp{1}, strcat('continuousMasks_',tmp{end}));
if ~exist(contMaskFolder, 'dir')
    mkdir(contMaskFolder)
end
thickMaskFolder = fullfile(tmp{1}, strcat('thickMasks_',tmp{end}));
if ~exist(thickMaskFolder, 'dir')
    mkdir(thickMaskFolder)
end

%Load all masks
maskStack = loadOctImages(maskDir, maskDims(1), maskDims(2), 'png');
sz = size(maskStack);

%loop through masks
for i = 1:sz(3)
    fileNamecont = sprintf('maskNo%0.0f.png', i);
    fileNameThick = sprintf('maskNo%0.0f.png', i);
    contiCurves = getCurves(maskStack(:,:,i));
    continMask = mapCurveIntoMasks(sz, contiCurves);
    thickMask = thickenMask(maskStack(:,:,i));
    % Save images
    imwrite(continMask, fullfile(contMaskFolder, fileNamecont));
    imwrite(thickMask, fullfile(thickMaskFolder, fileNameThick));
end


    function [intMask] = thickenMask(mask)
        int1 = interp2(double(mask));
        int1(int1>0) = 1;
        intMask = interp2(double(int1));
        intMask(intMask>0) = 1;
    end


    function [curve] = getCurves(mask)
        
        mSz = size(mask);
        curve = zeros(mSz(2),2);
        for ii = 1:mSz(2)
            [c,~] = find(mask(:,ii),255);
            if ~isempty(c) && length(c) == 1
                curve(ii,1) = c;
            elseif ~isempty(c) && length(c) == 2
                curve(ii,1) = min(c);
                curve(ii,2) = max(c);
            else
            end
        end
        
        
    end


    function [mask] = mapCurveIntoMasks(dims, curve)
        
        mask = zeros(dims(1), dims(2));
        
        for j = 1:dims(2)
            if curve(j,1) ~= 0 && curve(j+1,1) ~= 0
                mask(curve(j,1),j) = 1;
                if curve(j,1) < curve(j+1,1)
                    mask(curve(j,1)+1:curve(j+1,1),j+1) = 1;
                elseif curve(j,1) > curve(i+1,1)
                    mask(curve(j+1,1)+1:curve(j,1),j+1) = 1;
                else
                    mask(curve(j,1),j) = 1;
                end
            end
            
            %if a-Scan and next a-Scan ~= 0
            if curve(j,2) ~= 0 && curve(j+1,2) ~= 0
                mask(curve(j,2),j) = 1;
                if curve(j,2) < curve(j+1,2)
                    mask(curve(j,2)+1:curve(j+1,2),j+1) = 1;
                elseif curve(j,2) > curve(j+1,2)
                    mask(curve(j+1,2)+1:curve(j,2),j+1) = 1;
                else
                    mask(curve(j,2),j) = 1;
                end
            end
        end
        
    end



end


