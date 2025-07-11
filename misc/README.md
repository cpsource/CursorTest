Here's Python code to invert a binary tree:I've provided two approaches to invert a binary tree:

## **Recursive Approach (Most Common):**
- **Like flipping a photo**: At each node, swap left and right children, then recursively do the same for all children
- **Time Complexity**: O(n) - visit each node once
- **Space Complexity**: O(h) - where h is the height (due to recursion stack)

## **Iterative Approach:**
- **Like processing a stack of papers**: Use a stack to keep track of nodes to process
- **Same time/space complexity** but avoids recursion

## **Key Concept:**
Think of inversion like looking at the tree in a mirror - everything flips horizontally. A left child becomes a right child, and vice versa, at every level.

## **Example:**
```
Original:    Inverted:
    4            4
   / \          / \
  2   7        7   2
 / \ / \      / \ / \
1  3 6  9    9  6 3  1
```

The recursive solution is typically preferred in interviews because it's cleaner and more intuitive. Both approaches modify the tree in-place and return the root of the inverted tree.

Would you like me to explain any specific part of the algorithm or show how to handle edge cases?

