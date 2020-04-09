%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mainSegmentationLoop(DataStruct, cube)

for i = 1:DataStruct.loadedVolumeDims(3)
    b_Scan = cube(:,:,i);
    label = createSegmenationLabel(b_Scan);
    %No layer visible
    if label == 0
        fprintf("No layers visible in b-Scan No.%0.0f", i);
        continue
    else
        flag_segmentationSufficient = 0;
        [mask, curve] = segmentGradientImage(b_Scan, label);
        while ~flag_segmentationSufficient
            figure('units','normalized','outerposition',[0 0 1 1])
            imagesc(b_Scan);
            colormap gray;
            hold on
            title('Segmented layer boundarys')
            plot(curve(:,1)) %Endothelium
            plot(curve(:,2)) %OVD
            %         legend({'Segmented Endothelium boundary layer', 'Segmented O0VD boundary layer'});
            pause(1)
            
            %Only Endothelium visible
            if label == 1
                answer = questdlg('Was the Endothelium segmented correctly?',...
                    'Please select one box',...
                    'Yes',...
                    'No',...
                    'Yes');
                switch answer
                    case 'Yes'
                        flag_segmentationSufficient = 1; %exit while-loop
                        continue
                    case 'No'
                        %Endo
                        curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                        %Fill boundary positions (only Endothelium) with ones
                        for ii = 1:DataStruct.loadedVolumeDims(1)
                            if curve(ii,1) ~= 0
                                mask(curve(ii,1),ii) = 1;
                            end
                        end
                end
                
                %Both layers visible
            elseif label == 2
                answer = questdlg('Were the boundary layers correctly segmented?','Please select one box',...
                    'Yes, both',...
                    'No, only Endothelium',...
                    'No, only OVD',...
                    'Yes, both');
                switch answer
                    case 'Yes, both'
                        flag_segmentationSufficient = 1; %exit while-loop
                        continue
                    case 'No, only Endothelium'
                        %OVD
                        intPts = selectOVDManually(b_Scan,...
                            round(DataStruct.loadedVolumeDims(2)/40));
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!')
                            intPts = selectOVDManually(b_Scan,...
                                round(DataStruct.loadedVolumeDims(2)/40));
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                        %Fill boundary positions (only OVD) with ones
                        for ii = 1:DataStruct.loadedVolumeDims(1)
                            if curve(i,2) ~= 0
                                mask(curve(ii,2),ii) = 1;
                            end
                        end
                    case 'No, only OVD'
                        %Endo
                        curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                        %Fill boundary positions (only Endo) with ones
                        for ii = 1:DataStruct.loadedVolumeDims(1)
                            if curve(i,1) ~= 0
                                mask(curve(ii,1),ii) = 1;
                            end
                        end
                    case 'None'
                        %Endo
                        curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                        %OVD
                        intPts = selectOVDManually(b_Scan,...
                            round(DataStruct.loadedVolumeDims(2)/40));
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!')
                            intPts = selectOVDManually(b_Scan,...
                                round(DataStruct.loadedVolumeDims(2)/40));
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                        %Fill boundary positions (both layers) with ones
                        for ii = 1:DataStruct.loadedVolumeDims(1)
                            if curve(ii,1) ~= 0
                                mask(curve(ii,1),ii) = 1;
                            end
                            if curve(i,2) ~= 0
                                mask(curve(ii,2),ii) = 1;
                            end
                        end
                end
            else
                disp("Unecpected value for label of layers...")
                return
            end
            close all
        end
        
        %Save the mask containing correctly segmented boundary layers
        saveCalculatedMask(DataStruct, curve, mask, b_Scan, DataStruct.maskFolder, i);
        
    end
    
end