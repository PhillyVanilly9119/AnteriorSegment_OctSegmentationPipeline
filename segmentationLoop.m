%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = segmentationLoop(DataStruct, rawCube, cube)

% pre-allocate special masks
continuousMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));
thickMask = zeros(DataStruct.processingVolumeDims(1),...
    DataStruct.processingVolumeDims(2));

% get created folders and start segmentation accordingly
loopIdx = checkForPresegmentedScans(DataStruct.machineLearningFolder);

if loopIdx <= DataStruct.processingVolumeDims(3)
    for i = loopIdx:DataStruct.processingVolumeDims(3)
        
        b_Scan = cube(:,:,i);
        rawB_Scan = rawCube(:,:,i);
        [label, frames] = createSegmenationLabel(b_Scan);
        
        %No layer visible
        if label == 0
            % save all masks as "empty imges" in this case/ interation
            saveEmptyMask(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i);
            saveContinMasks(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i)
            saveThickMasks(DataStruct, zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), i);
            %% !!!CAUTION!!! non-useable for training but important for re-entering segmentation
            checkAndCreateDirsForDeepLearningData(DataStruct.machineLearningFolder,...
                rawB_Scan, b_Scan, ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)), ...
                zeros(DataStruct.processingVolumeDims(1),...
                DataStruct.processingVolumeDims(2)))
            fprintf("No layers visible in b-Scan No.%0.0f \nSaved empty a mask", i);
            continue
        else
            flag_segmentationSufficient = 0;
            [mask, curve] = segmentaScanDerivative(b_Scan, label, frames);
            
            while ~flag_segmentationSufficient
                %TODO: overwrite frames if manual additional segmentation took
                %place
                figure('units','normalized','outerposition',[0 0 1 1])
                imagesc(b_Scan);
                colormap gray;
                hold on
                title('Segmented layer boundarys')
                plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),1)) %Epithelium
                plot(frames(1,1):frames(2,1), curve(frames(1,1):frames(2,1),2)) %Endothelium
                % condition if ONLY Endothelium is visible
                if frames(1,2) ~= 0 && frames(2,2) ~= 0
                    plot(frames(1,2):frames(2,2), curve(frames(1,2):frames(2,2),3)) %OVD
                end
                pause(0.5)
                %______________________________________________
                % Only Epi- and Endothelium visible
                if label == 1
                    answer = questdlg('Were the Cornea layers segmented correctly?',...
                        'Please select one box',...
                        'Yes', 'No, resegment Epithelium', 'No, resegment Endothelium',...
                        'Yes');
                    switch answer
                        case 'Yes'
                            flag_segmentationSufficient = 1;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            continue
                            %Re-segment EPITHELIUM
                        case 'No, resegment Epithelium'
                            flag_segmentationSufficient = 0;
                            curve(:,1) = resegmentLayer(b_Scan, DataStruct, DataStruct.epiText);
                            curve(:,3) = 0;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            % re-segment ENDOTHELIUM
                        case 'No, resegment Endothelium'
                            flag_segmentationSufficient = 0;
                            curve(:,2) = resegmentLayer(b_Scan, DataStruct, DataStruct.endoText);
                            curve(:,3) = 0;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                    end
                %______________________________________________
                % All layers visible
                elseif label == 2
                    answer = questdlg('Were the boundary layers correctly segmented?',...
                        'Please select one box',...
                        'Yes', 'No, re-segment OVD', 'No, re-segment Cornea',...
                        'Yes');
                    switch answer
                        case 'Yes'
                            flag_segmentationSufficient = 1;
                            [mask, continuousMask, thickMask, binaryMask, inverseBinMask] = ...
                                createAllMasks(DataStruct, curve);
                            continue
                        case 'No, re-segment Cornea'
                            flag_segmentationSufficient = 0;
                            curve(:,1) = resegmentLayer(b_Scan, DataStruct, DataStruct.epiText);
                            curve(:,2) = resegmentLayer(b_Scan, DataStruct, DataStruct.endoText);
                        case 'No, re-segment OVD'
                            flag_segmentationSufficient = 0;
                            curve(:,3) = resegmentLayer(b_Scan, DataStruct, DataStruct.ovdText);
                    end
                %______________________________________________
                % All layers visible
                else
                    warning("Unexpected number layers detected!\n")
                    return
                end
                close all
            end
            %______________________________________________
            %Save the masks containing correctly segmented boundary layers)
            saveCalculatedMask(DataStruct, curve, mask, b_Scan, frames, i);
            saveContinMasks(DataStruct, continuousMask, i)
            saveThickMasks(DataStruct, thickMask, i);
            checkAndCreateDirsForDeepLearningData(DataStruct.machineLearningFolder,...
                rawB_Scan, b_Scan, ...
                mask, continuousMask, thickMask, binaryMask, inverseBinMask);
            
        end
        
    end
else
    disp("You have already segmented all b-Scans, you busy bee! :)")
end