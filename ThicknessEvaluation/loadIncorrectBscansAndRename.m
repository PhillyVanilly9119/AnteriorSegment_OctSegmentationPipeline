%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% load "IncorrectScans" (manually segmented) from evaluated Data to rename 
% it with original B-Scan indexing

%% Current Folder has to be the "IncorrectScans" folder!!!!
path                      = uigetdir('D:\OVID_segmentedDataforBA_addedIncorrectScanNo', 
                            'Select "IncorrectScans" folder');
fpath                     = [path '\'];
incorrect_bscan_list      = dir('*.bmp'); % Speichern der Nummern der B-Scans

fpath1                    = [fpath '\Data_Machine_Learning\'];
Data_Machine_Learning_old = dir(fpath1);

dirResult                 = dir(fpath1);
allDirs                   = dirResult([dirResult.isdir]);
allSubDirs                = allDirs(3:end);


%% rename manually segmented "Data_Machine_Learning" data
% oldname: indexing of "Data_Machine_Learning" begins with 0001 
% newname: oldname_incorrectScanNo.XXX (XXX=original B-Scan indexing)

for i = 1:length(allSubDirs)
    
           thisDir        = allSubDirs(i);
           thisDirName    = thisDir.name;
                   
           thisnewDir     = incorrect_bscan_list(i);
           thisnewDirName = thisnewDir.name;
           [~,name,~]     =  fileparts(thisnewDirName);
    
           oldname        = fullfile(fpath1,thisDir.name);
           newname        = [fullfile(fpath1,thisDir.name) '_incorrectScanNo.' name ];
           movefile(oldname,newname);            

end




