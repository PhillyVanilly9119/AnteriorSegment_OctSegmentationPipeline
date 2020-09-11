

fpath = ('D:\Beispielordner_Rename\PROVISC_1_1_Size6_OD-2020-05-08_122555\IncorrectScans');
dirfpath = dir(fpath)
fpath1 = ('D:\Beispielordner_Rename\PROVISC_1_1_Size6_OD-2020-05-08_122555\IncorrectScans\Data_Machine_Learning');
incorrect_bscan_list=dir(fpath1);





for j=size(incorrect_bscan_list, 1)
    


for i= size(dirfpath, 1)
   dateiname =strrep(fpath, num2str(i));
   movefile(dateiname, sprintf(ind_name(i)));

   
end

end 



% function changeDirNames(dirName)
% dirResult = dir(dirName);
% % allDirs = dirResult([dirResult.isdir]);
% 
% 
% for i = 1:size(dirResult,1)
%     
%     thisDir = dirResult(i);
%     thisDirName = thisDir.name;
%     
%     oldDir = incorrect_bscan_list(i);
%     oldDirName = oldDir.name
%     
%         oldname = fullfile(dirName,thisDir.name);
%         newname = [fullfile(fpath, oldDirName)];
%         movefile(oldname,newname);
%    
% end
% changeDirNames(newname);
% end


