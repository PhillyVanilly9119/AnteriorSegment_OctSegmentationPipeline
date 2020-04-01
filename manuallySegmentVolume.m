%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%               Auxiliary function for main implementation
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = manuallySegmentVolume(volume)

sz = size(volume);

for i = 1:sz(3)
  
    segPts = round(sz(2)/30);
    bScan = volume(:,:,i);
    mask = zeros(sz(1), sz(2), 2);
    [isEndo, isOVD] = segmentationDecision(bScan);
    
    if isEndo
        pts = selectNPointsManually(bScan, segPts, 1);
        while length(pts(1,:)) ~= length(unique(pts(1,:)))
            f = msgbox('Points are not unique, please reselect!','Re-segmentation neccessary');
            pause(1)
            pts = selectNPointsManually(bScan, segPts, 1);
        end
        mask(:,:,1) = intSelectedPointsOnMask(pts, sz(2), sz(1));
    else
        mask(:,:,1) = mask(:,:,1);
    end
    
    if isOVD
        pts = selectNPointsManually(bScan, segPts, 2);
        while length(pts(1,:)) ~= length(unique(pts(1,:)))
            f = msgbox('Points are not unique, please reselect!','Re-segmentation neccessary');
            pause(1)
            pts = selectNPointsManually(bScan, segPts, 2);
        end
        mask(:,:,2) = intSelectedPointsOnMask(pts, sz(2), sz(1));
    else
        mask(:,:,2) = mask(:,:,2);
    end
    
    %Save masks as *.bin-file and images
    saveCalculatedMask(mask, maskFolder, i);
    
end

end