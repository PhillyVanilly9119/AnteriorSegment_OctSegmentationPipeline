%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mainSegmentationLoop(DataStruct, cube)

for i = 1:DataStruct.imageVolumeDims(3)
    b_Scan = cube(:,:,i);
    %TODO: pass frames to the separate segmentaion function as additional
    %param
    [label, frames] = createSegmenationLabel(b_Scan);
    %No layer visible
    if label == 0
        fprintf("No layers visible in b-Scan No.%0.0f\n", i);
        continue
    else
        flag_segmentationSufficient = 0;
        [mask, curve] = segmentGradientImage(b_Scan, label, frames);
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
                        endPts = selectEndotheliumManually(b_Scan, 13);
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        %Fill boundary positions (only Endothelium) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
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
                            round(DataStruct.processingVolumeDims(2)/40));
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!\n')
                            intPts = selectOVDManually(b_Scan,...
                                round(DataStruct.processingVolumeDims(2)/40));
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.processingVolumeDims(2), DataStruct.processingVolumeDims(1));
                        %Fill boundary positions (only OVD) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                    case 'No, only OVD'
                        %Endo
                        endPts = selectEndotheliumManually(b_Scan, 13);
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        %Fill boundary positions (only Endo) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                    case 'None'
                        %Endo
                        endPts = selectEndotheliumManually(b_Scan, 13);
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        %OVD
                        intPts = selectOVDManually(b_Scan,...
                            round(DataStruct.processingVolumeDims(2)/40));
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!\n')
                            intPts = selectOVDManually(b_Scan,...
                                round(DataStruct.processingVolumeDims(2)/40));
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.processingVolumeDims(2), DataStruct.processingVolumeDims(1));
                        %Fill boundary positions (both layers) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                end
            else
                disp("Unecpected value for label of layers...\n")
                return
            end
            close all
        end
        
        %Save the mask containing correctly segmented boundary layers
        saveCalculatedMask(DataStruct, curve, mask, b_Scan, i);
        
    end
    
end