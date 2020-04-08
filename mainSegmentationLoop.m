function [] = mainSegmentationLoop(DataStruct, cube)

for i = 1:DataStruct.loadedVolumeDims(3)
    b_Scan = cube(:,:,i);
    [label, nExtrema] = createSegmenationLabel(b_Scan);
    flag_segmentationSufficient = 0;
    [mask, curve] = segmentGradientImage(b_Scan, label, nExtrema);
    while ~flag_segmentationSufficient
        figure
        axis equal
        imagesc(b_Scan);
        colormap gray;
        hold on
        title('Segmented layer boundarys')
        plot(curve(:,1)) %Endothelium
        plot(curve(:,2)) %OVD
        label('Segmented Endothelium boundary layer', 'Segmented OVD boundary layer');
        pause(1)
        if label == 0
            fprintf("There were no layers visible in b-Scan No.%0.0f", i);
            flag_segmentationSufficient = 1;
            continue
        elseif label == 1
            answer = questdlg('Were the visible boundary layers correctly segmented?','Please select one box',...
                'Yes, both',...
                'No, only Endothelium',...
                'No, only OVD',...
                'Yes, both');
            switch answer
                case 'Yes, both'
                    flag_segmentationSufficient = 1;
                    continue
                case 'No, only Endothelium'
                    curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                    %Fill boundary positions (only Endothelium) with ones
                    for ii = 1:sz(1)
                        if curve(ii,1) ~= 0
                            mask(curve(ii,1),ii) = 1;
                        end
                    end
                case 'No, only OVD'
                    intPts = selectOVDManually(b_Scan,...
                        round(DataStruct.loadedVolumeDims(3)/20));
                    curve(:,2) = interpolateSegmentedPoints(intPts,...
                        DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                    %Fill boundary positions (only OVD) with ones
                    for ii = 1:sz(1)
                        if curve(i,2) ~= 0
                            mask(curve(ii,2),ii) = 1;
                        end
                    end
            end
        elseif label == 2
            answer = questdlg('Were (the visible) boundary layers correctly segmented?','Please select one box',...
                'Yes',...
                'No, only Endothelium',...
                'None',...
                'None');
            switch answer
                case 'Yes'
                    flag_segmentationSufficient = 1;
                    continue
                case 'No only Endothelium'
                    intPts = selectOVDManually(b_Scan,...
                        round(DataStruct.loadedVolumeDims(3)/20));
                    curve(:,2) = interpolateSegmentedPoints(intPts,...
                        DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                    %Fill boundary positions (only OVD) with ones
                    for ii = 1:sz(1)
                        if curve(i,2) ~= 0
                            mask(curve(ii,2),ii) = 1;
                        end
                    end
                    
                case 'None'
                    curve(:,1) = selectEndotheliumManually(b_Scan, 9);
                    intPts = selectOVDManually(b_Scan,...
                        round(DataStruct.loadedVolumeDims(3)/20));
                    curve(:,2) = interpolateSegmentedPoints(intPts,...
                        DataStruct.loadedVolumeDims(2), DataStruct.loadedVolumeDims(1));
                    %Fill boundary positions (both layers) with ones
                    for ii = 1:sz(1)
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
    saveCalculatedMask(curve, mask, b_Scan, DataStruct.maskFolder, i);
end

end