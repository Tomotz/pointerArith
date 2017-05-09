
from chaotic import chaotic
from pointsto import join, bottom, top, set_addr, copy_var, load, store, iota

succ = {1:{2}, 2:{2,3}, 3:{}} # CFG edges
tr = {(1,2): lambda pt: set_addr(pt, 'x', 'a'), \
     (2, 2): lambda x: x,\
         (2, 3): lambda x: x} # transfer function
tr_txt  = {(1,2): "x := &a", (2, 2): "nop", (2, 3): "nop"}  # for debugging


chaotic(succ, 1, iota, join, bottom, tr, tr_txt)
