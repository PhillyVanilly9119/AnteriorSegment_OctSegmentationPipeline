%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% c@ melanie.wuest@zeiss.com & philipp.matten@meduniwien.ac.at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = saveDataCubeAsBinFile(path, fileName, dataCube)

fileID = fopen(fullfile(path, fileName), 'w');
fwrite(fileID, dataCube, 'uint8');
fclose(fileID);
fprintf('Done saving data to %s', fullfile(path, fileName));

end