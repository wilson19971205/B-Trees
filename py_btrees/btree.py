import bisect
import math
from typing import Any, List, Optional, Tuple, Union, Dict, Generic, TypeVar, cast, NewType
from py_btrees.disk import DISK, Address
from py_btrees.btree_node import BTreeNode, KT, VT, get_node

"""
----------------------- Starter code for your B-Tree -----------------------

Helpful Tips (You will need these):
1. Your tree should be composed of BTreeNode objects, where each node has:
    - the disk block address of its parent node
    - the disk block addresses of its children nodes (if non-leaf)
    - the data items inside (if leaf)
    - a flag indicating whether it is a leaf

------------- THE ONLY DATA STORED IN THE `BTree` OBJECT SHOULD BE THE `M` & `L` VALUES AND THE ADDRESS OF THE ROOT NODE -------------
-------------              THIS IS BECAUSE THE POINT IS TO STORE THE ENTIRE TREE ON DISK AT ALL TIMES                    -------------

2. Create helper methods:
    - get a node's parent with DISK.read(parent_address)
    - get a node's children with DISK.read(child_address)
    - write a node back to disk with DISK.write(self)
    - check the health of your tree (makes debugging a piece of cake)
        - go through the entire tree recursively and check that children point to their parents, etc.
        - now call this method after every insertion in your testing and you will find out where things are going wrong
3. Don't fall for these common bugs:
    - Forgetting to update a node's parent address when its parent splits
        - Remember that when a node splits, some of its children no longer have the same parent
    - Forgetting that the leaf and the root are edge cases
    - FORGETTING TO WRITE BACK TO THE DISK AFTER MODIFYING / CREATING A NODE
    - Forgetting to test odd / even M values
    - Forgetting to update the KEYS of a node who just gained a child
    - Forgetting to redistribute keys or children of a node who just split
    - Nesting nodes inside of each other instead of using disk addresses to reference them
        - This may seem to work but will fail our grader's stress tests
4. USE THE DEBUGGER
5. USE ASSERT STATEMENTS AS MUCH AS POSSIBLE
    - e.g. `assert node.parent != None or node == self.root` <- if this fails, something is very wrong

--------------------------- BEST OF LUCK ---------------------------
"""

# Complete both the find and insert methods to earn full credit
class BTree:
    def __init__(self, M: int, L: int):
        """
        Initialize a new BTree.
        You do not need to edit this method, nor should you.
        """
        self.root_addr: Address = DISK.new() # Remember, this is the ADDRESS of the root node
        # DO NOT RENAME THE ROOT MEMBER -- LEAVE IT AS self.root_addr
        DISK.write(self.root_addr, BTreeNode(self.root_addr, None, None, True))
        self.M = M # M will fall in the range 2 to 99999
        self.L = L # L will fall in the range 1 to 99999

    def split(self, root):

        L_split_point = math.ceil(float(self.L)/2.0)-1
        M_split_point = math.ceil(float(self.M)/2.0)-1

        if root.parent_addr == None and root.is_leaf:

            new_root_addr = DISK.new()
            new_root = BTreeNode(new_root_addr, None, None, False)
            new_root.keys.insert(0, root.keys[L_split_point])
            
            left_addr = DISK.new()
            left = BTreeNode(left_addr, new_root_addr, 0, root.is_leaf)
            
            right_addr = DISK.new()
            right = BTreeNode(right_addr, new_root_addr, 1, root.is_leaf)

            new_root.children_addrs.insert(0,left_addr)
            new_root.children_addrs.insert(1,right_addr)

            if self.L == 1:
                for i in range(self.L+1):
                    if i <= L_split_point:
                        left.insert_data(root.keys[i], root.data[i])
                    else:
                        right.insert_data(root.keys[i], root.data[i])
            else:
                for i in range(self.L):
                    if i <= L_split_point:
                        left.insert_data(root.keys[i], root.data[i])
                    else:
                        right.insert_data(root.keys[i], root.data[i])

            DISK.write(left_addr, left)
            left.write_back()
            DISK.write(right_addr, right)
            right.write_back()
            DISK.write(new_root_addr, new_root)
            new_root.write_back()
            self.root_addr = new_root_addr

            return new_root

        elif root.parent_addr == None and root.is_leaf == False:

            new_root_addr = DISK.new()
            new_root = BTreeNode(new_root_addr, None, None, False)
            new_root.keys.insert(0, root.keys[M_split_point])

            right_addr = DISK.new()
            right = BTreeNode(right_addr, new_root_addr, 1, root.is_leaf)
            root.parent_addr = new_root_addr
            root.index_in_parent = 0

            new_root.children_addrs.insert(0,root.my_addr)
            new_root.children_addrs.insert(1,right_addr)

            count = 0
            for i in range(M_split_point+1, len(root.keys)+1):
                    if i < len(root.keys):
                        right.keys.insert(count, root.keys[i])
                    child_node = root.get_child(i)
                    right.children_addrs.insert(count,child_node.my_addr)
                    child_node.parent_addr = right_addr
                    child_node.index_in_parent = count
                    DISK.write(child_node.my_addr, child_node)
                    child_node.write_back()
                    count += 1

            del root.keys[M_split_point:len(root.keys)]
            del root.children_addrs[M_split_point+1:len(root.children_addrs)]

            DISK.write(root.my_addr, root)
            root.write_back()
            DISK.write(right_addr, right)
            right.write_back()
            DISK.write(new_root_addr, new_root)
            new_root.write_back()
            self.root_addr = new_root_addr

            return new_root

        elif root.parent_addr != None and root.is_leaf == False:

            parent = root.get_parent()

            for i in range(root.index_in_parent+1, len(parent.keys)+1):
                child_node = parent.get_child(i)
                child_node.index_in_parent = i+1
                DISK.write(child_node.my_addr, child_node)
                child_node.write_back()

            parent.keys.insert(root.index_in_parent, root.keys[M_split_point])
            
            right_addr = DISK.new()
            right = BTreeNode(right_addr, parent.my_addr, root.index_in_parent+1, root.is_leaf)

            parent.children_addrs.insert(root.index_in_parent+1, right_addr)

            count = 0
            for i in range(M_split_point+1, len(root.keys)+1):
                    if i < len(root.keys):
                        right.keys.insert(count, root.keys[i])
                    child_node = root.get_child(i)
                    right.children_addrs.insert(count,child_node.my_addr)
                    child_node.parent_addr = right_addr
                    child_node.index_in_parent = count
                    DISK.write(child_node.my_addr, child_node)
                    child_node.write_back()
                    count += 1

            del root.keys[M_split_point:len(root.keys)]
            del root.children_addrs[M_split_point+1:len(root.children_addrs)]

            DISK.write(root.my_addr, root)
            root.write_back()
            DISK.write(right_addr, right)
            right.write_back()
            DISK.write(parent.my_addr, parent)
            parent.write_back()

            if len(parent.keys) >= self.M:
                return self.split(parent)
            return parent

        else:
            parent = root.get_parent()
            child_amount = len(parent.keys) + 1
            idx = root.index_in_parent
            parent.keys.insert(idx, root.keys[L_split_point])

            for i in range(child_amount):
                if i > idx:
                    child = parent.get_child(i)
                    child.index_in_parent += 1
                    DISK.write(child.my_addr, child)
                    child.write_back()
            parent.children_addrs.insert(idx + 1, parent.children_addrs[idx])
            

            new_child_addr = DISK.new()
            new_child = BTreeNode(new_child_addr, parent.my_addr, idx + 1, root.is_leaf)

            if self.L == 1:
                for i in range(self.L+1):
                    if i > L_split_point:
                        new_child.insert_data(root.keys[i], root.data[i])
            else:
                for i in range(self.L):
                    if i > L_split_point:
                        new_child.insert_data(root.keys[i], root.data[i])

            parent.children_addrs[idx + 1] = new_child_addr

            del root.keys[L_split_point + 1:len(root.keys)]
            del root.data[L_split_point + 1:len(root.data)] 

            DISK.write(root.my_addr, root)
            root.write_back()
            DISK.write(new_child_addr, new_child)
            new_child.write_back()
            DISK.write(parent.my_addr, parent)
            parent.write_back()

        if len(parent.keys) >= self.M:
            return self.split(parent)
        return parent


    def _insert(self, key: KT, value: VT, root):

        # if root is leaf
        if root.is_leaf:
            # if the root is full
            if len(root.keys) == self.L:
                if self.L == 1:
                    if root.find_data(key) != None:
                        root.data[root.find_idx(key)] = value
                        root.write_back()
                    else:
                        root.insert_data(key, value)
                        root.write_back()
                        root = self.split(root)
                        root.write_back()
                else:
                    root = self.split(root)
                    root.write_back()
                    self._insert(key, value, root)
            else:
                if root.find_data(key) != None:
                    root.data[root.find_idx(key)] = value
                    root.write_back()
                else:
                    root.insert_data(key, value)
                    root.write_back()

        else:
            idx = root.find_idx(key)
            self._insert(key, value, root.get_child(idx))


    def insert(self, key: KT, value: VT) -> None:
        """
        Insert the key-value pair into your tree.
        It will probably be useful to have an internal
        _find_node() method that searches for the node
        that should be our parent (or finds the leaf
        if the key is already present).

        Overwrite old values if the key exists in the BTree.

        Make sure to write back all changes to the disk!
        """
        root = DISK.read(self.root_addr)
        self._insert(key, value, root)    

    def _find(self, key: KT, root):
        idx = root.find_idx(key)
        if root.is_leaf:
            return root.find_data(key)
        else:
            return self._find(key, root.get_child(idx))


    def find(self, key: KT) -> Optional[VT]:
        """
        Find a key and return the value associated with it.
        If it is not in the BTree, return None.

        This should be implemented with a logarithmic search
        in the node.keys array, not a linear search. Look at the
        BTreeNode.find_idx() method for an example of using
        the builtin bisect library to search for a number in 
        a sorted array in logarithmic time.
        """
        root = DISK.read(self.root_addr)
        return self._find(key, root)

    def delete(self, key: KT) -> None:
        raise NotImplementedError("Karma method delete()")
