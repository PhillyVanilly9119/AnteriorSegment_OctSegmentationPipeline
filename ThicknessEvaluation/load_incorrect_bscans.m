%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

path = uigetdir('D:\OVID_segmentedDataforBA_addedIncorrectScanNo', 'Select "IncorrectScans" folder');
fpath = [path '\'];
incorrect_bscan_list=dir('*.bmp'); % Speichern der Nummern der B-Scans

fpath1 = [fpath '\Data_Machine_Learning\'];
Data_Machine_Learning_old=dir(fpath1);

dirResult = dir(fpath1);
allDirs = dirResult([dirResult.isdir]);
allSubDirs = allDirs(3:end);

for i = 1:length(allSubDirs)
    
    thisDir = allSubDirs(i);
    thisDirName = thisDir.name;
                   
    thisnewDir = incorrect_bscan_list(i);
    thisnewDirName = thisnewDir.name;
    [~,name,~] =  fileparts(thisnewDirName);
    
    oldname = fullfile(fpath1,thisDir.name);
    newname = [fullfile(fpath1,thisDir.name) '_incorrectScanNo.' name ];
    movefile(oldname,newname);            

end




