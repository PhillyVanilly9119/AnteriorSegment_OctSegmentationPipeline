%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filtVol] = applyCustomFilterForRESCAN(DataStruct, vol, label)


%Custom filtering
if label == 1
    filtVol = customFilterOption(DataStruct, vol);
    
%Userinput filtering
elseif label == 2
    %TODO: add Mellis filter and return as filtVol
%     filtVol = 0;
else
    error("You\'ve selected the wrong filtering option!");
    
end