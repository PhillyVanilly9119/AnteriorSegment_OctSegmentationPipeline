%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [isEndo, isOVD] = segmentationDecision(image)

imshow(image);
for i = 1:2
    if i == 1
        answer = questdlg('Is the endothelial boundary layer well enough identifiable for segmentation?', ...
            'Segmentation decision dialogue: Endothelium', 'Yes', 'No', 'Yes');
        switch answer
            case 'Yes'
                isEndo = 1;
            case 'No'
                isEndo = 0;
        end
    else
        answer = questdlg('Is the OVD boundary layer well enough identifiable for segmentation?', ...
            'Segmentation decision dialogue: OVD', 'Yes', 'No', 'Yes');
        switch answer
            case 'Yes'
                isOVD = 1;
            case 'No'
                isOVD = 0;
        end
        
    end
end

close(gcf);

end