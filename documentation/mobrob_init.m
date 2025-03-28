
g = 10 ;             % Erdbeschleunigung
m = 0.1 ;            % Masse des Roboters

ell = 0.1 ;          % Hebelarm Massenpunkt bis Boden
Rr = 20e-3 ;         % Radius der Räder in Meter
J_B = 0.01 ;         % Trägheitsmoment des Roboterköpers

K_kont = 1e6 ;       % Federkonstante bei Bodenkontakt (der Räder) 

mg = m*g ;