function [thickness] = calculateThicknessPerBscan(onemask)
one_px_in_micron=2900/1024;
n_ovd=1.333412;

sz = size(onemask);
% sz = size(mask); %[1024, 1024] = [länge, breite]  
thickness = zeros(1,sz(2)); 

    for i = 1:sz(2)     
         if nnz(onemask(:,i))==2 
            thickness(1,i) = (1.34*one_px_in_micron*(max(find(onemask(:,i)==1))-min(find(onemask(:,i)==1)))/n_ovd);
              else
                  thickness(1,i) = 0;
         end
    end
  
 ans = thickness;
end

