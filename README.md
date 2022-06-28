# B-Trees
Using Python to implement B-tree structure

## How to run:
graph.py -> Draw how the B-trees looks like
print.py -> Change M, L to control the number of keys in each non-leaf node and items in leaf node
```
python3 print.py
```

## Introduction:
B-Trees are short and wide M-ary trees, where M is an integer ≥ 2 that is chosen to fit as many keys and pointers into a node as possible, where the size of each node is defined by the size of a disk block. Similarly, the constant L is chosen to pack as many data items as possible into a disk block.

## definition of a B-Tree:
• Each node has at most m children

• Each non-leaf and non-root node has at least math.ceiling(M / 2) children

• A non-leaf node with k children contains k − 1 comparable keys

• The root, if it isn’t a leaf, has at least 2 children

• Each leaf node holds between math.ceiling(L / 2) and L data items

• If the leaf is the root, it can have a minimum of zero data items

• All leaves reside at the same level

## Output:
M = 4, L = 20, Numbers = 100

![image](https://user-images.githubusercontent.com/43212302/175808891-ddecbe79-194c-4383-a7d1-de7bf844520f.png)
