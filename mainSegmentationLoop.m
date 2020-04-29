%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mainSegmentationLoop(DataStruct, cube)

% pre-allocate special masks
continMask = zeros(DataStruct.processingVolumeDims(1),...
            DataStruct.processingVolumeDims(2));
thickMask = zeros(DataStruct.processingVolumeDims(1),...
            DataStruct.processingVolumeDims(2));

for i = 1:DataStruct.processingVolumeDims(3)
    
    b_Scan = cube(:,:,i);
    [label, frames] = createSegmenationLabel(b_Scan);
    
    %No layer visible
    if label == 0
        fprintf("No layers visible in b-Scan No.%0.0f\n", i);
        continue
    else
        flag_segmentationSufficient = 0;
        [mask, curve] = segmentAScanDerivative(b_Scan, label, frames);

        while ~flag_segmentationSufficient
            %TODO: overwrite frames if manual additional segmentation took
            %place
            figure('units','normalized','outerposition',[0 0 1 1])
            imagesc(b_Scan);
            colormap gray;
            hold on
            title('Segmented layer boundarys')
            plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),1)) %Endothelium
            % condition if ONLY Endothelium is visible
            if frames(1,2) ~= 0 && frames(2,2) ~= 0
                plot(frames(1,2):frames(2,2), curve(frames(1,2):frames(2,2),2)) %OVD
            end
            pause(0.5)
            
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
                        endPts = selectEndotheliumManually(b_Scan);
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        curve(:,2) = 0;
                        %Fill boundary positions (only Endothelium) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                        continMask = mapContinousCurveIntoMask(DataStruct, curve);
                        thickMask = mapContinousThickCurveIntoMask(DataStruct, curve);
                end
                
                %Both layers visible
            elseif label == 2
                answer = questdlg('Were the boundary layers correctly segmented?','Please select one box',...
                    'Yes, both',...
                    'No, re-segment OVD',...
                    'No, re-segment Endothelium',...
                    'Yes, both');
                switch answer
                    case 'Yes, both'
                        flag_segmentationSufficient = 1; %exit while-loop
                        continue
                    case 'No, re-segment OVD'
                        %OVD
                        intPts = selectOVDManually(b_Scan);
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!\n')
                            intPts = seletOVDManually(b_Scan);
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.processingVolumeDims(2), DataStruct.processingVolumeDims(1));
                        %Fill boundary positions (only OVD) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                        continMask = mapContinousCurveIntoMask(DataStruct, curve);
                        thickMask = mapContinousThickCurveIntoMask(DataStruct, curve);
                    case 'No, re-segment Endothelium'
                        %Endo
                        endPts = selectEndotheliumManually(b_Scan);
                        figure, imagesc(b_Scan), hold on;
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        %Fill boundary positions (only Endo) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                        continMask = mapContinousCurveIntoMask(DataStruct, curve);
                        thickMask = mapContinousThickCurveIntoMask(DataStruct, curve);
                    case 'None'
                        %Endo
                        endPts = selectEndotheliumManually(b_Scan);
                        curve(:,1) = interpolateQuadFctInRange(endPts,...
                            DataStruct.processingVolumeDims(2));
                        %OVD
                        intPts = selectOVDManually(b_Scan);
                        while numel(intPts(1,:))~= numel(unique(intPts(1,:)))
                            disp('Points must be unique!\n')
                            intPts = selectOVDManually(b_Scan);
                        end
                        curve(:,2) = interpolateBetweenSegmentedPoints(intPts,...
                            DataStruct.processingVolumeDims(2), DataStruct.processingVolumeDims(1));
                        %Fill boundary positions (both layers) with ones
                        mask = mapCurveIntoMask(DataStruct, curve);
                        continMask = mapContinousCurveIntoMask(DataStruct, curve);
                        thickMask = mapContinousThickCurveIntoMask(DataStruct, curve);
                end
            else
                disp("Unecpected value for label of layers...\n")
                return
            end
            close all
        end
        
        %Save the masks containing correctly segmented boundary layers)
        saveCalculatedMask(DataStruct, curve, mask, b_Scan, frames, i);
        saveContinMasks(DataStruct, continMask, i)
        saveThickMasks(DataStruct, thickMask, i);
        
    end
    
end