%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Caution!!!
% This function is currently also declared/ defined in main.m
% (currently Deprecated!)

function [octData] = LoadDataFromFile(a, b)
% Check if a data stack is already in the workspace
if exist('octData', 'var')
    answer = questdlg('There is already a data set in the workspace. Would you like to load a new set?', ...
        'Load OCT data from image files', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            disp('Loading new data set...')
            path = uigetdir();
            octData = loadOctImages(path, a, b, 'bmp');
        case 'No'
            octData = octData;
            %flag_Savedata = 0;
    end
    
else
    path = uigetdir();
    octData = loadOctImages(path, a, b, 'bmp');
    % Dialog for saving options of OCT images
    answer = questdlg('Would you like to save all images as a binary-file?', ...
        'Saving Options for OCT Images', 'Yes', 'No', 'No');
    switch answer
        case 'Yes'
            disp('Saving your data on same path as images were loaded from')
            flag_Savedata = 1;
        case 'No'
            disp('Data was not saved')
            flag_Savedata = 0;
    end
    if flag_Savedata == 1
        saveDataCubeAsBinFile(path, file, octData)
    end
    
end

end