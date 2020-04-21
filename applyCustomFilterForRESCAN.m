%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filtVol] = applyCustomFilterForRESCAN(DataStruct, vol, label)


%Custom filtering
if strcmp(label, 'user')
    filtVol = customFilterOption(DataStruct, vol);
    
%Userinput filtering
elseif strcmp(label, 'fixed')
    filtVol = applyFixedFilters(vol);

else
    error("You\'ve selected an unknown string for filter option identification!");
    
end