:- dynamic(position/3).
:- dynamic(unsafe_position/2).
:- dynamic(shifting/3).
%dark part of a room
 %floor of a room
 %fog/vapor cloud
 %tree
 %staircase down
   %floor of a room
   %fog/vapor cloud
   %floor of a room
   %human rogue called Agent
%se il mostro è visibile:
 %	-ti trovi tra il goal e il mostro(o il mostro sta nella tua stessa riga/colonna ma è più lontano dal goal) -> minpath(nuvole OK) verso il goal
 %	-il mostro si trova tra il goal e te (o è nella stessa riga/colonna del goal):
 %		-ti trovi lontano dal mostro/goal, fai un passo per avvicinarti al goal e ripeti sopra
 %		-ti trovi a <=2 mosse di distanza dal mostro:
 %			-muovi in una cella sicura che ti avvicini al traguardo (se ci sono)
 %			-altrimenti che non ti allontani, altrimenti che ti allontani
 %se non è visibile -> minpath sicuro(no nuvole) se esite, altrimenti con nuvole
 % per allontanarsi di meno dal goal, se è possibile allontanarsi solo di una riga o una colonna piuttosto che di entrambe
 %se il mostro dopo esser stato avvistato scompare si considera come se fosse dov'era prima
 %-se il mostro dopo esser stato avvistato è scomparso, se la distanza dal traguardo non cambia, meglio scegliere il percorso che maggiora la distanza dall'ultima posizione conosciuta del mostro.
 %-optional: implementare un bayesian network per stimare le probabilità che le celle hanno di essere in target del mostro dopo x turni dalla sua scomparsa, partendo dalla sua posizione e scegliere quella con probabilità minore come safe, piuttosto che quella più "lontana"
 %
 %non hai safe move perchè il mostro è vicino?
 %non si vede il goal?
 %	ce sopra il mostro-> allontanati dal mostro per farlo spostare
 %	è in una cella buia -> segna nella KB le coordinate delle celle buie e delle celle illuminate,
 %	controlla per ogni cella buia avvicinandoti se siano li le scale, man mano che ti avvicini se celle si illuminanp aggiungi all KB delle celle illuminate quelle che prima erano buie, se una cella da illumana passa a buia è cmq già "esplorata"
 %	una volta trovate le scale, si switcha al problema originale
% WHEN ENEMY IS NOT SEEN OR IS NOT A THREAT WE JUST MOVE TOWARDS THE GOAL
% TODO: KB must by emptied of all shifting added when the monster is found or it started a new episode
%azione dell'agente quando si vedono le scale ma non il mostro
action(move(Direction)) :- position(agent, AgentR, AgentC), position(down_stairs, StairsR, StairsC),
                           resulting_direction(AgentR, AgentC, StairsR, StairsC, D), 
                           IT is 0, safe_direction(AgentR, AgentC, D, D, D, Direction, IT).


% CHECKS IF TWO POSITIONS ARE CLOSE, I.E. IF THEY ARE AT 1 CELL DISTANCE

is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+ 1; C1 is C2- 1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+ 1; R1 is R2- 1).
is_close(R1,C1,R2,C2) :- (R1 is R2+ 1; R1 is R2- 1), (C1 is C2+ 1; C1 is C2- 1).

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
doubleCheck(X,Y,Direction,Check):- (safe_position(X,Y)->
					(\+shifting(X,Y,List)->
						Check=true, asserta(shifting( X,Y,[Direction]));
						(shifting(X,Y,List),member(Direction,List) ->
							Check = List;
							Check = true,write('addShift'), addShiftingList(X,Y,Direction)))).


safe_direction(R, C, CL_D, C_CL_D, D, Direction, IT) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) ->
                                      %if the agent hasn't moved there yet from current position
                                        (\+shifting(R,C,List)->
                                            Direction = D,asserta(shifting( R,C,[Direction]));
                                            % else, if the agent has already moved from this position and altready went to D, D will create a loop so it's usafe
                                            (shifting(R,C,List),member(Direction,List) ->
                                                (0 is (IT mod 2) ->
                                                   ITN is (IT + 1), clock_close_direction(CL_D, CL_ND),
                                                   safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN);
                                                   ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND),
                                                   safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN));
                                        	    %the agent has already moved from this position but not to the direction D
                                        	    Direction=D, addShiftingList(R,C,Direction))));
                                      % else, get a new close direction
                                      % and check its safety
                                      (0 is (IT mod 2) ->
                                         ITN is (IT + 1), clock_close_direction(CL_D, CL_ND),
                                         safe_direction(R, C, CL_ND, C_CL_D, CL_ND, Direction, ITN);
                                         ITN is (IT + 1), c_clock_close_direction(C_CL_D, C_CL_ND),
                                         safe_direction(R, C, CL_D, C_CL_ND, C_CL_ND, Direction, ITN)).


% UNSAFE/UNWALKABLE POSITIONS
%todo:aggiungere cloud
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