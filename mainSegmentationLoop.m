function [] = mainSegmentationLoop(DataStruct, cube)

for i = 1:DataStruct.loadedVolumeDims(3)
    b_Scan = cube(:,:,i);
    [label, nExtrema] = createSegmenationLabel(b_Scan);
    flag_segmentationSufficient = 0; 
    [mask, curve] = segmentGradientImage(b_Scan, label, nExtrema);
    while ~flag_segmentationSufficient
        figure
        imagesc(b_Scan);
        colormap gray;
        hold on
        title('Segmented layer boundarys')
        plot(curve(:,1)) %Endothelium
        plot(curve(:,2)) %OVD
%         axis equal
        legend({'Segmented Endothelium boundary layer', 'Segmented O0VD boundary layer'});
        pause(1)
        
        %No layer visible
        if label == 0 
            fprintf("There were no layers visible in b-Scan No.%0.0f", i);
            flag_segmentationSufficient = 1;
            continue
            
        %Only Endothelium visible
        elseif label == 1 
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
                    intPts = selectOVDManually(b_Scan,...
                        round(DataStruct.loadedVolumeDims(2)/20));
                    curve(:,2) = interpolateSegmentedPoints(intPts,...
                        DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                    %Fill boundary positions (only OVD) with ones
                    for ii = 1:DataStruct.loadedVolumeDims(1)
                        if curve(i,2) ~= 0
                            mask(curve(ii,2),ii) = 1;
                        end
                    end
                 case 'No, only OVD'
                    curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                    %Fill boundary positions (only Endo) with ones
                    for ii = 1:DataStruct.loadedVolumeDims(1)
                        if curve(i,1) ~= 0
                            mask(curve(ii,1),ii) = 1;
                        end
                    end    
                case 'None'
                    curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                    intPts = selectOVDManually(b_Scan,...
                        round(DataStruct.loadedVolumeDims(2)/20));
                    curve(:,2) = interpolateSegmentedPoints(intPts,...
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
    saveCalculatedMask(curve, mask, b_Scan, DataStruct.maskFolder, i);

end

end