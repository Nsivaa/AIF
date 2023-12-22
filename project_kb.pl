:- dynamic(position/3).
:- dynamic(unsafe_position/2).
:- dynamic(unwalkable_position/2).
:- dynamic(already_walked/2).
:- dynamic(lastKnownEnemyPosition/2).

% WHEN ENEMY IS NOT SEEN OR IS NOT A THREAT WE JUST MOVE TOWARDS THE GOAL
% TODO: togliere la roba quando sei vicino alla scala
% TODO: KB must by emptied of all already_walked/2 and lastKnownEnemyPosition/2 added when it starts a new episode
% azione dell agente quando si vedono le scale ma non il mostro
% if stairs are at 1 distance, go for it and ignore every safety check
%In otder to get a direction of movement the preference hierarchy for direction is : safe_position>unsafe_position>already_walked>unwalkable_position
%unsafe_position>already_walked beacuse already walked position can lead to loops which is worse than walking in risky positions.
% se ti trovi tra il mostro e le scale, resetti already walked
action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC), is_close(AgentR, AgentC, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, Direction),(already_walked(AgentR,AgentC)->true;asserta(already_walked(AgentR,AgentC))).

action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, D), checkMonsterPosition(AgentR,AgentC,StairsC,StairsR),
                           setEnemyCloudPositions(AgentR, AgentC), IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT,_),
                           (already_walked(AgentR,AgentC)->true;asserta(already_walked(AgentR,AgentC))).

%if there is no stairs but the monster is visible we to a safe_position toward the monster cell until the monster moves out of the stairs.
action(move(Direction)) :- position(agent, AgentR, AgentC),\+position(down_stairs, _,_), position(enemy,TargetR,TargetC),
                           resulting_direction(AgentR, AgentC, TargetR,TargetC, D), setEnemyCloudPositions(AgentR, AgentC),
                           IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT,_).

checkMonsterPosition(AgentR,AgentC,TargetR,TargetC):- resulting_direction(AgentR, AgentC, TargetR,TargetC, D1),
                                                        (position(enemy,MonsterR,MonsterC)->
                                                            resulting_direction(TargetR,TargetC,MonsterR,MonsterC, D2),
                                                            (opposite(D1,D2);is_close(MonsterR, MonsterC, AgentR, AgentC) -> retractall(already_walked(_,_));true);true).
%the function set the last known enemy position if it is visible, if there is no enemy lastKnown position the function does nothing,
%otherwise the function set the enemy position as if it was in the position of the 3 nearest (to the agent) cells among the ones near
%last known position and with clouds or dark in them; That are the only 3 ones in which the monster could move (because he target the agent).
setEnemyCloudPositions(AgentR,AgentC):- (position(enemy,R,C)->
                            retractall(lastKnownEnemyPosition(_,_)), asserta(lastKnownEnemyPosition(R,C));
                            (lastKnownEnemyPosition(R,C)->
                                %if last known enemy position became a dark cell, maybe the monster is still there
                                (position(dark,R,C)->retractall(position(dark,R,C)), asserta(position(enemy,R,C));true),
                                resulting_direction(R, C, AgentR, AgentC, D),
                                checkCloudPosition(R,C,D),
                                clock_close_direction(D, CC_D),checkCloudPosition(R,C,CC_D),
                                c_clock_close_direction(D, AC_D),checkCloudPosition(R,C,AC_D);true)).

checkCloudPosition(R,C,D):- resulting_position(R,C,NewR,NewC,D),
                        (position(cloud,NewR,NewC)->
                            retractall(position(cloud,NewR,NewC)), asserta(position(enemy,NewR,NewC));
                            (position(dark,NewR,NewC)->
                                retractall(position(dark,NewR,NewC)), asserta(position(enemy,NewR,NewC));true)).

% CHECKS IF TWO POSITIONS ARE CLOSE, I.E. IF THEY ARE AT 1 CELL DISTANCE

is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+ 1; C1 is C2- 1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+ 1; R1 is R2- 1).
is_close(R1,C1,R2,C2) :- (R1 is R2+ 1; R1 is R2- 1), (C1 is C2+ 1; C1 is C2- 1).

% CHECKS IF TWO POINTS ARE ON THE SAME DIAGONAL

are_on_same_diagonal(R ,C ,ER, EC) :- abs(R - ER) =:= abs(C - EC).


% compute the direction of the target (r2,c2) w.r.t. th agent (r1,c1)
% D is the direction the agent will move
resulting_direction(R1,C1,R2,C2, D) :-
    ( R1 == R2 -> ( C1 > C2 -> D = west; D = east );
    ( C1 == C2 -> ( R1 > R2 -> D = north; D = south);
    ( R1 > R2 ->
        ( C1 > C2 -> D = northwest; D = northeast );
        ( C1 > C2 -> D = southwest; D = southeast )
    ))).
% CHECK IF THE DIRECTION LEADS TO A SAFE POSITION
% D = TEMPORARY DIRECTION - MAY BE UNSAFE
% Direction = THE DEFINITIVE DIRECTION
% IT = INTEGER ITERATING VALUE, TO ALTERNATINGLY CHECK FOR CLOCKWISE AND COUNTER-CLOCKWISE CLOSE DIRECTIONS
% the check is made alterning clockwise anti-clockwise because the greater is the angle between the resulting direction and the choosen direction
%to take a move, the longer the path will be.

% LOOK FOR A SAFE DIRECTION IN THE CLOSEST 4

safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT,safe) :- resulting_position(R, C, NewR, NewC, D),
                                      (safe_position(NewR, NewC) ->
                                        Direction=D;
                                      % else, get a new close direction
                                      % and check its safety
                                        (IT < 5 ->
                                            (0 is (IT mod 2)->
                                             ITN is (IT + 1), clock_close_direction(CL_D, CL_ND),
                                             safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN,safe);
                                             ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND),
                                             safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN,safe));false)).

% IF WE HAVENT FOUND A SAFE POSITION IN THE CLOSEST 4, WE PLAY MORE RISKY 

safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT,walkable) :- resulting_position(R, C, NewR, NewC, D),
                                      (walkable_position(NewR, NewC) ->
                                        Direction=D;
                                      % else, get a new close direction
                                      % and check its safety
                                        (IT < 9 ->
                                            (0 is (IT mod 2)->
                                             ITN is (IT + 1), clock_close_direction(CL_D, CL_ND),
                                             safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN,walkable);
                                             ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND),
                                             safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN,walkable));false)).

% IF WE HAVENT FOUND A WALKABLE POSITION WE TRY THE ALREADY_WALKED POSITIONS

safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT,walked) :- resulting_position(R, C, NewR, NewC, D),
                                      (already_walked(NewR, NewC) ->
                                        Direction=D;
                                      % else, get a new close direction
                                      % and check its safety
                                        (IT < 9 ->
                                            (0 is (IT mod 2)->
                                             ITN is (IT + 1), clock_close_direction(CL_D, CL_ND),
                                             safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN,walked);
                                             ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND),
                                             safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN,walked));false)).


% UNWALKABLE POSITIONS

unwalkable_position(R,C) :- position(boulder, R, C).
unwalkable_position(R,C) :- position(enemy, R, C).
unwalkable_position(R,C) :- position(tree, R, C).

%% CHECK FOR WALLS. 
%% EVERY UNKNOWN POSITION IS CONSIDERED OUT OF BOUNDS.

unwalkable_position(R,C) :- \+ position(_,R,C).
unwalkable_position(R,C) :- already_walked(R,C).

% UNSAFE POSITIONS


% we avoid the perpendicular and diagonal positions to the enemy to make ranged attacks less likely to hit, if the enemy is not close to us (enemy will not use range attacks) and there is no tree in between

unsafe_position(R, C) :- position(enemy, R, EC), position(agent, AR, AC), \+ is_close(AR, AC, R, EC), \+ (position(tree, R, TC), abs(TC - EC) < abs(EC - C)). % ROW CHECK
unsafe_position(R, C) :- position(enemy, ER, C), position(agent, AR, AC), \+ is_close(AR, AC, ER, C), \+ (position(tree, TR ,C), abs(TR - ER) < abs(ER - R)). % COLUMN CHECK

unsafe_position(R,C) :- position(enemy, ER, EC), are_on_same_diagonal(R ,C , ER, EC), position(agent, AR, AC), \+ is_close(AR, AC, ER, EC),
                        \+ ( position(tree, TR ,TC), ( (abs(TR - ER) + abs(TC - EC)) < (abs(ER - R) + abs(EC + C)) ) ). 

unsafe_position(R,C) :- position(enemy, ER, EC), is_close(ER, EC, R, C).


unsafe_position(R,C) :- unwalkable_position(R,C).
unsafe_position(_,_) :- fail.

% CALCULATES RESULTING COORDINATES GIVEN THE DIRECTION

resulting_position(R, C, NewR, NewC, north) :-
    NewR is R- 1, NewC = C.
resulting_position(R, C, NewR, NewC, south) :-
    NewR is R+ 1, NewC = C.
resulting_position(R, C, NewR, NewC, west) :-
    NewR = R, NewC is C- 1.
resulting_position(R, C, NewR, NewC, east) :-
    NewR = R, NewC is C+ 1.
resulting_position(R, C, NewR, NewC, northeast) :-
    NewR is R- 1, NewC is C+ 1.
resulting_position(R, C, NewR, NewC, northwest) :-
    NewR is R- 1, NewC is C- 1.
resulting_position(R, C, NewR, NewC, southeast) :-
    NewR is R+ 1, NewC is C+ 1.
resulting_position(R, C, NewR, NewC, southwest) :-
    NewR is R+ 1, NewC is C- 1.


%%%%%%%%%%%%%%%%%%%%%%%% FACTS %%%%%%%%%%%%%%%%%%55%%%%

% OPPOSITE DIRECTIONS

opposite(north, south).
opposite(south, north).
opposite(east, west).
opposite(west, east).
opposite(northeast, southwest).
opposite(southwest, northeast).
opposite(northwest, southeast).
opposite(southeast, northwest).

 
% CLOCKWISE CLOSE DIRECTIONS

clock_close_direction(north, northeast).
clock_close_direction(northeast, east).
clock_close_direction(east, southeast).
clock_close_direction(southeast, south).
clock_close_direction(south, southwest).
clock_close_direction(southwest, west).
clock_close_direction(west, northwest).
clock_close_direction(northwest, north).

% COUNTER-CLOCKWISE CLOSE DIRECTIONS

c_clock_close_direction(north, northwest).
c_clock_close_direction(northwest, west).
c_clock_close_direction(west, southwest).
c_clock_close_direction(southwest, south).
c_clock_close_direction(south, southeast).
c_clock_close_direction(southeast, east).
c_clock_close_direction(east, northeast). 
c_clock_close_direction(northeast, north).


safe_position(R,C) :- \+ unsafe_position(R,C).
walkable_position(R,C) :- \+ unwalkable_position(R,C).
