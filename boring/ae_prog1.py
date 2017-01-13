
from chaotic import chaotic
from aexp import join, bottom, top, assign, iota

succ = {1:{2}, 2:{2,3}, 3:{}} # CFG edges
tr = {(1,2): lambda ae: assign(ae, 'x', ('+', (('y',()), ('2',())))), \
     (2, 2): lambda x: x,\
         (2, 3): lambda x: x} # transfer function
tr_txt  = {(1,2): "x := y + 2", (2, 2): "nop", (2, 3): "nop"}  # for debugging


chaotic(succ, 1, iota, join, bottom, tr, tr_txt)
