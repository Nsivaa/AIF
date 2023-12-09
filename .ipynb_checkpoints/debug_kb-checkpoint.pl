:- dynamic(position/3).
:- dynamic(unsafe_position/2).
:- dynamic(unwalkable_position/2).
:- dynamic(shifting/3).

position(up_stairs, 7, 34).
position(tree, 7, 35).
position(floor, 7, 36).
position(cloud, 7, 37).
position(floor, 7, 38).
position(floor, 7, 39).
position(cloud, 7, 40).
position(tree, 7, 41).
position(floor, 7, 42).
position(floor, 7, 43).
position(dark, 7, 44).
position(floor, 8, 34).
position(floor, 8, 35).
position(floor, 8, 36).
position(cloud, 8, 37).
position(tree, 8, 38).
position(floor, 8, 39).
position(cloud, 8, 40).
position(floor, 8, 41).
position(floor, 8, 42).
position(dark, 8, 43).
position(floor, 8, 44).
position(tree, 9, 34).
position(agent, 9, 35).
position(floor, 9, 36).
position(floor, 9, 37).
position(cloud, 9, 38).
position(floor, 9, 39).
position(floor, 9, 40).
position(floor, 9, 41).
position(cloud, 9, 42).
position(floor, 9, 43).
position(tree, 9, 44).
position(tree, 10, 34).
position(floor, 10, 35).
position(floor, 10, 36).
position(floor, 10, 37).
position(floor, 10, 38).
position(floor, 10, 39).
position(floor, 10, 40).
position(cloud, 10, 41).
position(cloud, 10, 42).
position(floor, 10, 43).
position(floor, 10, 44).
position(tree, 11, 34).
position(floor, 11, 35).
position(floor, 11, 36).
position(floor, 11, 37).
position(floor, 11, 38).
position(floor, 11, 39).
position(floor, 11, 40).
position(cloud, 11, 41).
position(cloud, 11, 42).
position(floor, 11, 43).
position(cloud, 11, 44).
position(floor, 12, 34).
position(floor, 12, 35).
position(floor, 12, 36).
position(floor, 12, 37).
position(floor, 12, 38).
position(floor, 12, 39).
position(floor, 12, 40).
position(floor, 12, 41).
position(floor, 12, 42).
position(floor, 12, 43).
position(tree, 12, 44).
position(floor, 13, 33).
position(floor, 13, 34).
position(floor, 13, 35).
position(floor, 13, 36).
position(floor, 13, 37).
position(cloud, 13, 38).
position(cloud, 13, 39).
position(floor, 13, 40).
position(floor, 13, 41).
position(floor, 13, 42).
position(floor, 13, 43).
position(floor, 13, 44).
position(floor, 14, 33).
position(cloud, 14, 34).
position(cloud, 14, 35).
position(tree, 14, 36).
position(floor, 14, 37).
position(cloud, 14, 38).
position(cloud, 14, 39).
position(cloud, 14, 40).
position(floor, 14, 41).
position(floor, 14, 42).
position(floor, 14, 43).
position(floor, 14, 44).
position(floor, 15, 33).
position(down_stairs, 15, 34).
position(cloud, 15, 35).
position(floor, 15, 36).
position(cloud, 15, 37).
position(dark, 15, 38).
position(cloud, 15, 39).
position(cloud, 15, 40).
position(floor, 15, 41).
position(floor, 15, 42).
position(floor, 15, 43).
position(floor, 15, 44).


% dark part of a room
 % floor of a room
 % fog/vapor cloud
 % tree
 % staircase down
   % floor of a room
   % fog/vapor cloud
   % floor of a room
   % human rogue called Agent
% se il mostro è visibile:
 %	-ti trovi tra il goal e il mostro(o il mostro sta nella tua stessa riga/colonna ma è più lontano dal goal) -> minpath(nuvole OK) verso il goal
 %	-il mostro si trova tra il goal e te (o è nella stessa riga/colonna del goal):
 %		-ti trovi lontano dal mostro/goal, fai un passo per avvicinarti al goal e ripeti sopra
 %		-ti trovi a <=2 mosse di distanza dal mostro:
 %			-muovi in una cella sicura che ti avvicini al traguardo (se ci sono)
 %			-altrimenti che non ti allontani, altrimenti che ti allontani
 % se non è visibile -> minpath sicuro(no nuvole) se esite, altrimenti con nuvole
 % per allontanarsi di meno dal goal, se è possibile allontanarsi solo di una riga o una colonna piuttosto che di entrambe
 % se il mostro dopo esser stato avvistato scompare si considera come se fosse dov'era prima
 %-se il mostro dopo esser stato avvistato è scomparso, se la distanza dal traguardo non cambia, meglio scegliere il percorso che maggiora la distanza dall'ultima posizione conosciuta del mostro.
 %-optional: implementare un bayesian network per stimare le probabilità che le celle hanno di essere in target del mostro dopo x turni dalla sua scomparsa, partendo dalla sua posizione e scegliere quella con probabilità minore come safe, piuttosto che quella più "lontana"
 %
 %non hai safe move perchè il mostro è vicino?
 %non si vede il goal?
 %	ce sopra il mostro-> allontanati dal mostro per farlo spostare
 %	è in una cella buia -> segna nella KB le coordinate delle celle buie e delle celle illuminate,
 %	controlla per ogni cella buia avvicinandoti se siano li le scale, man mano che ti avvicini se celle si illuminanp aggiungi all KB delle celle      illuminate quelle che prima erano buie, se una cella da illumana passa a buia è cmq già "esplorata"
 %	una volta trovate le scale, si switcha al problema originale
% WHEN ENEMY IS NOT SEEN OR IS NOT A THREAT WE JUST MOVE TOWARDS THE GOAL
% TODO: KB must by emptied of all shifting added when the monster is found or it started a new episode
% azione dell agente quando si vedono le scale ma non il mostro

% if stairs are at 1 distance, go for it and ignore every safety check

action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC), is_close(AgentR, AgentC, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, Direction).


action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, D), 
                           IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT).


% CHECKS IF TWO POSITIONS ARE CLOSE, I.E. IF THEY ARE AT 1 CELL DISTANCE

is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+ 1; C1 is C2- 1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+ 1; R1 is R2- 1).
is_close(R1,C1,R2,C2) :- (R1 is R2+ 1; R1 is R2- 1), (C1 is C2+ 1; C1 is C2- 1).

% CHECKS IF TWO POINTS ARE ON THE SAME DIAGONAL

are_on_same_diagonal(R ,C ,ER, EC) :- abs(R - ER) =:= abs(C - EC).

% TODO: when the stairs are visible, find a path to them


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
%We must check also if the agent is not already shifted from R,C following direction D (it would be a loop).
% we are using the fact "shifting" instead of "unsafe_position" to check the already path routed because shifting will remain in the KB until the end of an episode
% while unsafe position is recalculated before every step.

addShiftingList(R,C,Direction) :- shifting(R,C,List),retract(shifting(R,C,List)),append(List,[Direction],NewList) ,asserta(shifting(R,C,NewList)).

% LOOK FOR A SAFE DIRECTION IN THE CLOSEST 4


% IF WE HAVENT FOUND A SAFE POSITION IN THE CLOSEST 4, WE PLAY MORE RISKY 

safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT) :- resulting_position(R, C, NewR, NewC, D),
                                      ( walkable_position(NewR, NewC) -> Direction = D;
                                      % else, get a new close direction
                                      % and check its safety

                                       (0 is (IT mod 2)) ->
                                       (ITN is (IT + 1), clock_close_direction(CL_D, CL_ND), 
                                       safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN));

                                      (ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND), 
                                       safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN))
                                      ).

% UNWALKABLE POSITIONS

unwalkable_position(R,C) :- position(boulder, R, C).
unwalkable_position(R,C) :- position(enemy, R, C).
unwalkable_position(R,C) :- position(tree, R, C).

%% CHECK FOR WALLS. 
%% EVERY UNKNOWN POSITION IS CONSIDERED OUT OF BOUNDS.

unwalkable_position(R,C) :- \+ position(_,R,C).


% UNSAFE POSITIONS


% we avoid the perpendicular and diagonal positions to the enemy to make ranged attacks less likely to hit, if the enemy is not close to us (enemy will not use range attacks) and there is no tree in between

unsafe_position(R, C) :- position(enemy, R, EC), \+ is_close(R, C, R, EC), \+ (position(tree, R, TC), abs(TC - EC) < abs(EC - C)). % ROW CHECK
unsafe_position(R, C) :- position(enemy, ER, C), \+ is_close(R, C, ER, C), \+ (position(tree, TR ,C), abs(TR - ER) < abs(ER - R)). % COLUMN CHECK

unsafe_position(R,C) :- position(enemy, ER, EC), are_on_same_diagonal(R ,C , ER, EC), \+ is_close(R, C, ER, EC),
                        \+ ( position(tree, TR ,TC), ( (abs(TR - ER) + abs(TC - EC)) < (abs(ER - R) + abs(EC + C)) ) ). 

unsafe_position(R,C) :- position(enemy, ER, EC), is_close(ER, EC, R, C).

%todo:aggiungere cloud

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
c_clock_close_direction(soutwest, south).
c_clock_close_direction(south, southeast).
c_clock_close_direction(southeast, east).
c_clock_close_direction(east, northeast). 
c_clock_close_direction(northeast, north).


safe_position(R,C) :- \+ unsafe_position(R,C).
walkable_position(R,C) :- \+ unwalkable_position(R,C).

