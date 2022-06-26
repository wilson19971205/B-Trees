import random
import graph
from py_btrees.btree import BTree

M = 3
L = 2
btree = BTree(M, L)
#keys = [i for i in range(4)]
keys = [0,1,2,3]
#random.shuffle(keys)
for k in keys:
    btree.insert(k, str(k))

g = graph.create(btree)
# print(g.source)
g.view()