function adjMatrixW = createAdjMat(img, mask, v, minWeight)
    segImg = img;

    idx = 1:size(img,1);
    idx = idx(sum(img(:,:,1)==0,2)==size(img,2));

    if numel(idx)>0
        if idx(1)>1, idx = [idx(1)-1,idx]; end
        if idx(end)<size(segImg,1), idx = [idx,idx(end)+1]; end
    end

    % get the "invert" of the gradient image.
    segImg = segImg*-1+1; 

    %arry to store weights
    adjMW = nan([numel(img(:)),5]);
    %arry to store point 1 locations
    adjMX = (1:numel(img(:)))';
    adjMX = repmat(adjMX,1,5);
    %arry to store point 2 locations
    adjMY = nan([numel(img(:)),5]);

    % pad with zeros at left and right border
    idx1 = 1:numel(segImg);
    idx1 = reshape(idx1,size(segImg,1),size(segImg,2));

    segImg = cat(1,zeros(1,size(segImg,2)),segImg,zeros(1,size(segImg,2)));
    segImg = cat(2,zeros(size(segImg,1),1),segImg,zeros(size(segImg,1),1));
    
    mask = cat(1,zeros(1,size(mask,2)),mask,zeros(1,size(mask,2)));
    mask = cat(2,zeros(size(mask,1),1),mask,zeros(size(mask,1),1));
    
    idx2 = cat(1,zeros(1,size(idx1,2)),idx1,zeros(1,size(idx1,2)));
    idx2 = cat(2,zeros(size(idx2,1),1),idx2,zeros(size(idx2,1),1));

    mn = size(segImg,1);
    nn = size(segImg,2);

    %minimum weight
    count = 1;
    maxWeight = 1e9;

    % calculate weights of the graph
    for i = [-1, 0, 1]
        for j = [-1, 0, 1]
            if j < 0 || (i==0 && j==0)
                continue;
            else

                % cost function to define weights
                if i == 0
                    w = 2 - segImg(2:(mn-1),2:(nn-1)) - segImg((2:(mn-1))+i,(2:(nn-1))+j) + minWeight;
                else
                    w = 2 - segImg(2:(mn-1),2:(nn-1)) - segImg((2:(mn-1))+i,(2:(nn-1))+j) + minWeight + v;
                end
                
                %w(isnan(mask(2:(mn-1),2:(nn-1)))) = maxWeight;
                w(mask(2:(mn-1),2:(nn-1)) == 1) = maxWeight;
                w(mask(2:(mn-1),2:(nn-1)) == -1) = minWeight;
                w(:,1) = minWeight;
                w(:,end) = minWeight;
                if numel(idx)>0, w(idx,2:end-1) = max(w(:)); end
                adjMW(:,count) = w(:);

                tidx = idx2((2:(mn-1))+i,(2:(nn-1))+j);

                adjMY(:,count) = tidx(:);
                count = count + 1;
            end
        end
    end

    keepInd = adjMY(:) ~= 0;
    adjMW = adjMW(keepInd);
    adjMY = adjMY(keepInd);
    adjMX = adjMX(keepInd);

    % sparse matrices (graph representation)
    adjMatrixW = sparse(adjMX(:),adjMY(:),adjMW(:),numel(img(:)),numel(img(:)));
end