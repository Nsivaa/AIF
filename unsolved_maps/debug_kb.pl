:- dynamic position/3.
:- dynamic unsafe_position/2.

% action(run(OppositeDirection)) :- position(agent, AgentR, AgentC), position(enemy, EnemyR, EnemyC),
 %                                  is_close(AgentR, AgentC, EnemyR, EnemyC),
 %                                  resulting_direction(AgentR, AgentC, EnemyR, EnemyC, Direction),
  %                                 opposite(Direction, OD), 
   %                             IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT).


% WHEN ENEMY IS NOT SEEN OR IS NOT A THREAT WE JUST MOVE TOWARDS THE GOAL
action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, D), 
                           IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT).

% TODO: WHEN STAIR POISITON IS NOT KNOWN, WE JUST EXPLORE

% CHECKS IF TWO POSITIONS ARE CLOSE, I.E. IF THEY ARE AT 1 CELL DISTANCE

is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).


% COMPUTE THE RESULTING DIRECTION GIVEN STARTING AND TARGET POSITION

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

safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) -> Direction = D;
                                      % else, get a new close direction
                                      % and check its safety
                                      
                                       (0 is (IT mod 2)) ->
                                       (ITN is (IT + 1), clock_close_direction(CL_D, CL_ND), 
                                       safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN));
                                       
                                      (ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND), 
                                       safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN))
                                      ).


% UNSAFE/UNWALKABLE POSITIONS

unsafe_position(R,C) :- position(boulder, R, C).
unsafe_position(R,C) :- position(enemy, R, C).
unsafe_position(R,C) :- position(tree, R, C).
unsafe_position(R,C) :- position(enemy, ER, EC), is_close(ER, EC, R, C).

%% CHECK FOR WALLS. 
%% TOP LEFT CORNER OF MAP IS POS.[7,34]
%% BOTTOM RIGHT CORNER OF MAP IS POS.[15,44]

unsafe_position(R,_) :- R < 7; R > 15.
unsafe_position(_,C) :- C < 34; C > 44.

unsafe_position(_,_) :- fail.

% CALCULATES RESULTING COORDINATES GIVEN THE DIRECTION

resulting_position(R, C, NewR, NewC, north) :-
    NewR is R-1, NewC = C.
resulting_position(R, C, NewR, NewC, south) :-
    NewR is R+1, NewC = C.
resulting_position(R, C, NewR, NewC, west) :-
    NewR = R, NewC is C-1.
resulting_position(R, C, NewR, NewC, east) :-
    NewR = R, NewC is C+1.
resulting_position(R, C, NewR, NewC, northeast) :-
    NewR is R-1, NewC is C+1.
resulting_position(R, C, NewR, NewC, northwest) :-
    NewR is R-1, NewC is C-1.
resulting_position(R, C, NewR, NewC, southeast) :-
    NewR is R+1, NewC is C+1.
resulting_position(R, C, NewR, NewC, southwest) :-
    NewR is R+1, NewC is C-1.


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
c_clock_close_direction(soutwest, south).
c_clock_close_direction(south, southeast).
c_clock_close_direction(southeast, east).
c_clock_close_direction(east, northeast). 
c_clock_close_direction(northeast, north).


safe_position(R,C) :- \+ unsafe_position(R,C).
