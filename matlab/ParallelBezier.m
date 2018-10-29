%% Oskar I, Parallel Bézier Curve and Orthagonal Distance with 1m Check

clear all, close all, clc;

% CurveIndex specifying which Bézier Curve Control Points
CurveIndex = 0

% LaneWidth in meters
LaneWidth = 2;

% The division is to get the distance to the 
% center of the lane (from the middle of the road)
LaneWidth = LaneWidth / 2;

% Control Points for the Bézier Curve
pMatrix = [ 
            1,1;        % p0 for CurveIndex = 1
            1,5;        % p1 for CurveIndex = 1
            4,9;        % p2 for CurveIndex = 1
            10,10;      % p3 for CurveIndex = 1
            1,1;        % p0 for CurveIndex = 2
            1,50;       % p1 for CurveIndex = 2
            40,90;      % p2 for CurveIndex = 2
            100,100;    % p3 for CurveIndex = 2
            1,1;        % p0 for CurveIndex = 3
            -5,6;       % p1 for CurveIndex = 3
            11,9;       % p2 for CurveIndex = 3
            10,1;       % p3 for CurveIndex = 3
            0,0;        % p0 for CurveIndex = 4
            1,6;        % p1 for CurveIndex = 4
            7,4;        % p2 for CurveIndex = 4
            10,10;      % p3 for CurveIndex = 4
            4,0;        % p0 for CurveIndex = 5
            1,6;        % p1 for CurveIndex = 5
            7,4;        % p2 for CurveIndex = 5
            10,10;      % p3 for CurveIndex = 5
            0,0;        % p0 for CurveIndex = 6
            10,10;      % p1 for CurveIndex = 6
            10,-10;     % p2 for CurveIndex = 6
            0,0;        % p3 for CurveIndex = 6
          ]

% This for loop serves to plot all different 
% Curves in pMatrix in different figures
for CurveIndex = 0:1:length(pMatrix(:,1))/4-1
    
    p0 = pMatrix(CurveIndex * 4 + 1,:);
    p1 = pMatrix(CurveIndex * 4 + 2,:);
    p2 = pMatrix(CurveIndex * 4 + 3,:);
    p3 = pMatrix(CurveIndex * 4 + 4,:);

% Generate parametrization p from control points p0-p3, and calculate
% ParametrizationSteps so that distance between adjacent Autoware points
% is shorter than 1 meter

ParametrizationSteps = 0;
while 1
    p           = [];
    dpdt        = [];
    direction   = [];
    left        = [];
    right       = [];
    DistanceMax = 0;
    ParametrizationSteps = ParametrizationSteps + 1;
    for t = 0:1/ParametrizationSteps:1
        p           = [p        ; p0*(1-t)^3 + 3*p1*(1-t)^2*t + 3*p2*(1-t)*t^2+ p3*t^3]; % ?? x 2 vector, x-values in c1, y-values in c2
        dpdt        = [dpdt     ; -3*p0*(1-t)^2 + 3*p1*(1-t)^2 - 6*p1*(1-t)*t + 6*p2*(1-t)*t - 3*p2*t^2 + 3*p3*t^2];
        direction   = [direction; atan2(dpdt(end,2),dpdt(end,1))];
        left        = [left     ; p(end,1) + LaneWidth*(-sin(direction(end))), p(end,2) + LaneWidth*( cos(direction(end)))];
        right       = [right    ; p(end,1) + LaneWidth*( sin(direction(end))), p(end,2) + LaneWidth*(-cos(direction(end)))];
        if t ~= 0
            LDistance = norm(left(end,:) -left(end-1,:));
            RDistance = norm(right(end,:)-right(end-1,:));
            if LDistance > DistanceMax
                DistanceMax = LDistance;               
            end
            if RDistance > DistanceMax
                DistanceMax = RDistance;
            end
            if DistanceMax > 1
                break
            end
        end
    end
    if DistanceMax <= 1
        break
    end
end

%DistanceMax

% Plots for Center Road Curve
figure(CurveIndex+1)
set(gcf,'position',[180*(CurveIndex+1) 50 200 200])

hold on
plot(p0(1), p0(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p1(1), p1(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p2(1), p2(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p3(1), p3(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot([p0(1), p1(1), p2(1), p3(1)], [p0(2), p1(2), p2(2), p3(2)], '--g')
%plot(pm(1), pm(2), 'rx')
plot(p(:,1), p(:,2), 'Color', [0, 0.4470, 0.7410]) % Bézier Curve
axis equal


% Lanes

% Control point 0, p0LLane and p0RLane, for Left and Right Lanes, respectively
p01 = p1-p0;
p01Direction = atan2(p01(2), p01(1));
p0LLane = [p0(1) + LaneWidth*(-sin(p01Direction)), p0(2) + LaneWidth*( cos(p01Direction))];
p0RLane = [p0(1) + LaneWidth*( sin(p01Direction)), p0(2) + LaneWidth*(-cos(p01Direction))];
%plot(p0LLane(1),p0LLane(2), 'rx', p0RLane(1), p0RLane(2), 'rx')

% Control points 3, p3LLane and p3RLane, for Left and Right Lanes, respectively
p23 = p3-p2;
p23Direction = atan2(p23(2), p23(1));
p3LLane = [p3(1) + LaneWidth*(-sin(p23Direction)), p3(2) + LaneWidth*( cos(p23Direction))];
p3RLane = [p3(1) + LaneWidth*( sin(p23Direction)), p3(2) + LaneWidth*(-cos(p23Direction))];
%plot(p3LLane(1),p3LLane(2), 'rx', p3RLane(1), p3RLane(2), 'rx')

% Guess of Control points 1 and 2, p1LLaneGuess, p1RLaneGuess, p2LLaneGuess, and p2RLaneGuess
p12 = p2-p1;
p12Direction = atan2(p12(2), p12(1));
p1LLaneGuess = [p1(1) + LaneWidth*(-sin(p12Direction)), p1(2) + LaneWidth*( cos(p12Direction))];
p1RLaneGuess = [p1(1) - LaneWidth*(-sin(p12Direction)), p1(2) - LaneWidth*( cos(p12Direction))];
p2LLaneGuess = [p2(1) + LaneWidth*(-sin(p12Direction)), p2(2) + LaneWidth*( cos(p12Direction))];
p2RLaneGuess = [p2(1) - LaneWidth*(-sin(p12Direction)), p2(2) - LaneWidth*( cos(p12Direction))];
plot(p1LLaneGuess(1), p1LLaneGuess(2), 'rx', p2LLaneGuess(1), p2LLaneGuess(2), 'rx')
plot(p1RLaneGuess(1), p1RLaneGuess(2), 'rx', p2RLaneGuess(1), p2RLaneGuess(2), 'rx')

% Control lines for Left Lane
plot([p1LLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2LLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1LLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2LLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980])
plot([p0LLane(1), p0LLane(1) + 1.5*norm(p01)*cos(p01Direction)], [p0LLane(2), p0LLane(2) + 1.5*norm(p01)*sin(p01Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980]);
plot([p3LLane(1), p3LLane(1) - 1.5*norm(p23)*cos(p23Direction)], [p3LLane(2), p3LLane(2) - 1.5*norm(p23)*sin(p23Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980]);

% Control lines for Right Lane
plot([p1RLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2RLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1RLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2RLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980])
plot([p0RLane(1), p0RLane(1) + 1.5*norm(p01)*cos(p01Direction)], [p0RLane(2), p0RLane(2) + 1.5*norm(p01)*sin(p01Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980]);
plot([p3RLane(1), p3RLane(1) - 1.5*norm(p23)*cos(p23Direction)], [p3RLane(2), p3RLane(2) - 1.5*norm(p23)*sin(p23Direction)], '--', 'Color', [0.8500, 0.3250, 0.0980]);

% Calculate intersection of lines to figure out actual values for control points 1 and 2
[p1LLane(1), p1LLane(2)] = polyxpoly([p0LLane(1), p0LLane(1) + 1.5*norm(p01)*cos(p01Direction)], [p0LLane(2), p0LLane(2) + 1.5*norm(p01)*sin(p01Direction)],[p1LLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2LLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1LLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2LLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)]);
[p1RLane(1), p1RLane(2)] = polyxpoly([p0RLane(1), p0RLane(1) + 1.5*norm(p01)*cos(p01Direction)], [p0RLane(2), p0RLane(2) + 1.5*norm(p01)*sin(p01Direction)],[p1RLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2RLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1RLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2RLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)]);
[p2LLane(1), p2LLane(2)] = polyxpoly([p1LLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2LLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1LLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2LLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)], [p3LLane(1), p3LLane(1) - 1.5*norm(p23)*cos(p23Direction)], [p3LLane(2), p3LLane(2) - 1.5*norm(p23)*sin(p23Direction)]);
[p2RLane(1), p2RLane(2)] = polyxpoly([p1RLaneGuess(1) - 0.5*norm(p12)*cos(p12Direction), p2RLaneGuess(1) + 0.5*norm(p12)*cos(p12Direction)], [p1RLaneGuess(2) - 0.5*norm(p12)*sin(p12Direction), p2RLaneGuess(2) + 0.5*norm(p12)*sin(p12Direction)], [p3RLane(1), p3RLane(1) - 1.5*norm(p23)*cos(p23Direction)], [p3RLane(2), p3RLane(2) - 1.5*norm(p23)*sin(p23Direction)]);
plot(p0LLane(1),p0LLane(2), 'ro', p0RLane(1),p0RLane(2), 'ro', p1LLane(1),p1LLane(2), 'ro', p1RLane(1),p1RLane(2), 'ro', p2LLane(1),p2LLane(2), 'ro', p2RLane(1),p2RLane(2), 'ro', p3LLane(1),p3LLane(2), 'ro', p3RLane(1),p3RLane(2), 'ro')

% Control points 0 and 3 for left and right lanes, respectively



% Bézier Curves for Left and Right Lanes
pLLane = [];
pRLane = [];
for t = 0:1/ParametrizationSteps:1
    pLLane = [pLLane; p0LLane*(1-t)^3 + 3*p1LLane*(1-t)^2*t + 3*p2LLane*(1-t)*t^2+ p3LLane*t^3];
    pRLane = [pRLane; p0RLane*(1-t)^3 + 3*p1RLane*(1-t)^2*t + 3*p2RLane*(1-t)*t^2+ p3RLane*t^3];
end
plot(pLLane(:,1), pLLane(:,2), 'r', pRLane(:,1), pRLane(:,2), 'r') % Bézier Curve

% Lanes from Orthagonal Derivation
plot(left(:,1), left(:,2), 'bx', right(:,1), right(:,2), 'bx')
%plot(left(1:1:end,1), left(1:1:end,2), 'yx', right(1:1:end,1), right(1:1:end,2), 'yx')

end

%% Oskar II, only Orthagonal Distance with 1m Check

clear all, close all, clc;

% CurveIndex specifying which Bézier Curve Control Points
CurveIndex = 0

% LaneWidth in meters
LaneWidth = 2;

% The division is to get the distance to the 
% center of the lane (from the middle of the road)
LaneWidth = LaneWidth / 2;

% Control Points for the Bézier Curve
pMatrix = [ 
            1,1;        % p0 for CurveIndex = 1
            1,5;        % p1 for CurveIndex = 1
            4,9;        % p2 for CurveIndex = 1
            10,10;      % p3 for CurveIndex = 1
            1,1;        % p0 for CurveIndex = 2
            1,50;       % p1 for CurveIndex = 2
            40,90;      % p2 for CurveIndex = 2
            100,100;    % p3 for CurveIndex = 2
            1,1;        % p0 for CurveIndex = 3
            -5,6;       % p1 for CurveIndex = 3
            11,9;       % p2 for CurveIndex = 3
            10,1;       % p3 for CurveIndex = 3
            0,0;        % p0 for CurveIndex = 4
            1,6;        % p1 for CurveIndex = 4
            7,4;        % p2 for CurveIndex = 4
            10,10;      % p3 for CurveIndex = 4
            4,0;        % p0 for CurveIndex = 5
            1,6;        % p1 for CurveIndex = 5
            7,4;        % p2 for CurveIndex = 5
            10,10;      % p3 for CurveIndex = 5
            0,0;        % p0 for CurveIndex = 6
            10,10;      % p1 for CurveIndex = 6
            10,-10;     % p2 for CurveIndex = 6
            0,0;        % p3 for CurveIndex = 6
          ]

% This for loop serves to plot all different 
% Curves in pMatrix in different figures
for CurveIndex = 0:1:length(pMatrix(:,1))/4-1
    
    p0 = pMatrix(CurveIndex * 4 + 1,:);
    p1 = pMatrix(CurveIndex * 4 + 2,:);
    p2 = pMatrix(CurveIndex * 4 + 3,:);
    p3 = pMatrix(CurveIndex * 4 + 4,:);

% Generate parametrization p from control points p0-p3, and calculate
% ParametrizationSteps so that distance between adjacent Autoware points
% is shorter than 1 meter

ParametrizationSteps = 0;
while 1
    p           = [];
    dpdt        = [];
    direction   = [];
    left        = [];
    right       = [];
    DistanceMax = 0;
    ParametrizationSteps = ParametrizationSteps + 1;
    for t = 0:1/ParametrizationSteps:1
        p           = [p        ; p0*(1-t)^3 + 3*p1*(1-t)^2*t + 3*p2*(1-t)*t^2+ p3*t^3]; % ?? x 2 vector, x-values in c1, y-values in c2
        dpdt        = [dpdt     ; -3*p0*(1-t)^2 + 3*p1*(1-t)^2 - 6*p1*(1-t)*t + 6*p2*(1-t)*t - 3*p2*t^2 + 3*p3*t^2];
        direction   = [direction; atan2(dpdt(end,2),dpdt(end,1))];
        left        = [left     ; p(end,1) + LaneWidth*(-sin(direction(end))), p(end,2) + LaneWidth*( cos(direction(end)))];
        right       = [right    ; p(end,1) + LaneWidth*( sin(direction(end))), p(end,2) + LaneWidth*(-cos(direction(end)))];
        if t ~= 0
            LDistance = norm(left(end,:) -left(end-1,:));
            RDistance = norm(right(end,:)-right(end-1,:));
            if LDistance > DistanceMax
                DistanceMax = LDistance;               
            end
            if RDistance > DistanceMax
                DistanceMax = RDistance;
            end
            if DistanceMax > 1
                break
            end
        end
    end
    if DistanceMax <= 1
        break
    end
end

% Plots for Center Road Curve
figure(CurveIndex+1)
set(gcf,'position',[180*(CurveIndex+1) 50 200 200])

hold on
plot(p0(1), p0(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p1(1), p1(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p2(1), p2(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot(p3(1), p3(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])
plot([p0(1), p1(1), p2(1), p3(1)], [p0(2), p1(2), p2(2), p3(2)], '--g')
%plot(pm(1), pm(2), 'rx')
plot(p(:,1), p(:,2), 'Color', [0, 0.4470, 0.7410]) % Bézier Curve
axis equal

% Lanes from Orthagonal Derivation
plot(left(:,1), left(:,2), 'bx', right(:,1), right(:,2), 'bx')
%plot(left(1:1:end,1), left(1:1:end,2), 'yx', right(1:1:end,1), right(1:1:end,2), 'yx')

end

%% SAM, LOOK HERE!

clear all, close all, clc;

% LaneWidth in meters
LaneWidth = 2;

% The division is to get the distance to the 
% center of the lane (from the middle of the road)
LaneWidth = LaneWidth / 2;

% Control Points for the Bézier Curve
p0 = [1,1];
p1 = [1,5];
p2 = [4,9];
p3 = [10,10];

% Generate parametrization p from control points p0-p3, and calculate
% ParametrizationSteps so that distance between adjacent Autoware points
% is shorter than 1 meter

ParametrizationSteps = 0;
while 1
    p           = [];
    dpdt        = [];
    direction   = [];
    left        = [];
    right       = [];
    DistanceMax = 0;
    ParametrizationSteps = ParametrizationSteps + 1; % ParametrizationSteps is incremented to make a smoother curve, until the distance between adjacent points is below 1 meter.
    for t = 0:1/ParametrizationSteps:1
        p           = [p        ; p0*(1-t)^3 + 3*p1*(1-t)^2*t + 3*p2*(1-t)*t^2+ p3*t^3]; % ?? x 2 vector, x-values in c1, y-values in c2
        dpdt        = [dpdt     ; -3*p0*(1-t)^2 + 3*p1*(1-t)^2 - 6*p1*(1-t)*t + 6*p2*(1-t)*t - 3*p2*t^2 + 3*p3*t^2];
        direction   = [direction; atan2(dpdt(end,2),dpdt(end,1))];
        left        = [left     ; p(end,1) + LaneWidth*(-sin(direction(end))), p(end,2) + LaneWidth*( cos(direction(end)))];
        right       = [right    ; p(end,1) + LaneWidth*( sin(direction(end))), p(end,2) + LaneWidth*(-cos(direction(end)))];
        if t ~= 0   % The first iteration (t = 0) it is impossible to create a distance between two adjacent data points, because there is only one so far.
            LDistance = norm(left(end,:) -left(end-1,:));   % Distance between the current left lane point and the previous one.
            RDistance = norm(right(end,:)-right(end-1,:));  % Distance between the current right lane point and the previous one.
            if LDistance > DistanceMax
                DistanceMax = LDistance;    % Update DistanceMax if the previous DistanceMax is surpassed.             
            end
            if RDistance > DistanceMax
                DistanceMax = RDistance;    % Update DistanceMax if the previous DistanceMax is surpassed. 
            end
            if DistanceMax > 1              % If the DistanceMax ever surpasses 1 meter, it is unnecessary to finish the current parametrization, as its ParametrizationSteps are too few.
                break
            end
        end
    end
    if DistanceMax <= 1  % If a parametrization completes with a DistanceMax below 1 meter, a good model for a curve road has been found!
        break
    end
end

% Plots for Center Road Curve
figure()

hold on
plot(p0(1), p0(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])             % Control Point 0
plot(p1(1), p1(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])             % Control Point 1
plot(p2(1), p2(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])             % Control Point 2
plot(p3(1), p3(2), 'o', 'MarkerEdgeColor', [0, 0.4470, 0.7410])             % Control Point 3
plot([p0(1), p1(1), p2(1), p3(1)], [p0(2), p1(2), p2(2), p3(2)], '--g')     % Line connecting points p0 through p3
plot(p(:,1), p(:,2), 'Color', [0, 0.4470, 0.7410]) % Bézier Curve
axis equal

% Center of left and right lanes from Orthagonal Derivation
plot(left(:,1), left(:,2), 'bx', right(:,1), right(:,2), 'bx')