%Formats the net cell into a CSV File which can be then used to calculate
%generation numbers build a geometry for CFD

function MAT2CSV(net, sizIm, filename)
%Get radius values from net cell by dividing diameter values by 2
radii = cell2mat(net(:,3))./2;

%Initialize table
table = [];

%Create table with diameter and start and end points for each branch
for i = 1:size(net, 1)
    coordinates = net(i,1);
    coordinates1 = coordinates{:}(1);    
    coordinates2 = coordinates{:}(end);
    radius = radii(i); 
    table(i,:) = [radius, coordinates1, coordinates2]; 
end

%Go through each branch's junctions list and change their end coordinates
%to ensure that they share the same end coordinates as sometimes the
%coordinates are 1 away but not equal. They must be equal.

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

%Create the final table by converting the coordinate values to cartesian
%coordinates.
for i = 1:size(table,1)
    radius = radii(i);
    final_table(i,:) = [radius, getCoordinates(table(i,2), sizIm), getCoordinates(table(i,3), sizIm)]; 
    
end

name = append(filename,'.csv');

writematrix(final_table,name);
end
%Function that converts a 1D coordinate into 3D cartesian coordinates using
%the image size.
function XYZ = getCoordinates(multcoords, sizIm)

    frame = sizIm(1) * sizIm (2);

    Z = floor(multcoords / frame);
    
    inFrame = multcoords - Z * frame;

    X = floor(inFrame / sizIm(1));

    Y = inFrame - X * sizIm(1);

    XYZ = [X, Y, Z];

end

