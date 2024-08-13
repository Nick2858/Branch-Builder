diameters = cell2mat(net(:,3))./2;
table = [];
max = 0;
for i = 1:size(net, 1)
    coordinates = net(i,1);
    coordinates1 = coordinates{:}(1);    
    coordinates2 = coordinates{:}(end);
    diameter = diameters(i);
    %table(i,:) = [diameter, getCoordinates(coordinates1, sizIm), getCoordinates(coordinates2, sizIm)]; 
    table(i,:) = [diameter, coordinates1, coordinates2]; 
end

for i = 1:size(net,1)
    juncs = cell2mat(net(i,11));
    mainCoord1 = table(i,2);
    
    mainCoord2 = table(i,3);
    
    vec1 = getCoordinates(mainCoord1, sizIm);
    vec2 = getCoordinates(mainCoord2, sizIm);
    for j = 1:size(juncs)        

        coord1 = getCoordinates(table(juncs(j), 2), sizIm);
        coord2 = getCoordinates(table(juncs(j), 3), sizIm);
        
        oneOne = norm(vec1 - coord1);
        oneTwo = norm(vec1 - coord2);
        twoOne = norm(vec2 - coord1);
        twoTwo = norm(vec2 - coord2);

        minCoord = min([oneOne,oneTwo,twoOne,twoTwo]);
        
        if minCoord == oneOne
            table(juncs(j),2) = mainCoord1;
        elseif minCoord == oneTwo
            table(juncs(j),3) = mainCoord1;
        elseif minCoord == twoOne
            table(juncs(j),2) = mainCoord2;
        else
            table(juncs(j),3) = mainCoord2;
        end


    end

    
end

for i = 1:size(table,1)
    diameter = diameters(i);
    final_table(i,:) = [diameter, getCoordinates(table(i,2), sizIm), getCoordinates(table(i,3), sizIm)]; 
    
end

csvwrite(filename,final_table);


function XYZ = getCoordinates(multcoords, sizIm)

    frame = sizIm(1) * sizIm (2);

    Z = floor(multcoords / frame);
    
    inFrame = multcoords - Z * frame;

    X = floor(inFrame / sizIm(1));

    Y = inFrame - X * sizIm(1);

    XYZ = [X, Y, Z];

end

