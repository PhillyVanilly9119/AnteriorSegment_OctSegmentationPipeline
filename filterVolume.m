%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [flag_ImageQualiyIsGood, filteredOctCube] = filterVolume(volume)

sz = size(volume);
filteredOctCube = zeros(sz(1), sz(2), sz(3));

list = {
    'Yes, Find Edges',... % 1
    'Yes, Noise Reduction', ... %2
    'Yes, Apply Salt&Pepper (fine)',... %3
    'Yes, Apply Salt&Pepper (coarse)',... %4
    'No' %last
    };

[indx,~] = listdlg('PromptString',{'Select filter-option to apply to your entire volume',...
    'Only one choice at a time'},'ListString',list);
answer = list{indx};

switch answer
    case 'Yes, find edges' %1
        warning("This option is not yet refined");
        for i = 1:sz(3)
            filteredOctCube(:,:,i) = detectEdges(volume(:,:,i));
        end
        flag_ImageQualiyIsGood = 0;
    case 'Yes, Noise Reduction' %2
        percentile = 40;
        for i = 1:sz(3)
            filteredOctCube(:,:,i) = denoiseBScan(volume(:,:,i), percentile);
        end
        flag_ImageQualiyIsGood = 0;
    case 'Yes, Apply Salt&Pepper (fine)' %3
        for i = 1:sz(3)
            filteredOctCube(:,:,i) = filterImageNoise(volume(:,:,i), 'openAndClose', 3);
        end
        flag_ImageQualiyIsGood = 0;
    case 'Yes, Apply Salt&Pepper (coarse)' %4
        for i = 1:sz(3)
            filteredOctCube(:,:,i) = filterImageNoise(volume(:,:,i), 'openAndClose', 5);
        end
        flag_ImageQualiyIsGood = 0;
    case 'No' %last
        filteredOctCube = volume;
        flag_ImageQualiyIsGood = 1;
        
end

filteredOctCube = uint8(filteredOctCube);

end