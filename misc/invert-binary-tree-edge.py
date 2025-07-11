# Definition for a binary tree node
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode({self.val})"

def invert_tree(root, visited=None):
    """
    Inverts a binary tree recursively with cycle detection.
    
    Think of it like looking at a tree in a mirror - everything flips horizontally.
    Each node's left child becomes its right child, and vice versa.
    
    Args:
        root: TreeNode - The root of the binary tree
        visited: set - Tracks visited nodes to detect cycles
    
    Returns:
        TreeNode - The root of the inverted tree
    
    Raises:
        ValueError: If a cycle is detected in the tree
        RecursionError: If tree depth exceeds Python's recursion limit
    """
    # Initialize visited set for cycle detection
    if visited is None:
        visited = set()
    
    # Base case: if node is None, return None
    if not root:
        return None
    
    # Check for cycles
    if id(root) in visited:
        raise ValueError("Cycle detected in tree - not a valid binary tree")
    
    # Add current node to visited set
    visited.add(id(root))
    
    # Swap the left and right children
    root.left, root.right = root.right, root.left
    
    # Recursively invert the left and right subtrees
    invert_tree(root.left, visited)
    invert_tree(root.right, visited)
    
    # Remove from visited set when backtracking (for shared subtrees)
    visited.remove(id(root))
    
    return root

def invert_tree_iterative(root):
    """
    Inverts a binary tree iteratively using a stack.
    
    Like processing a to-do list - keep a stack of nodes to process,
    swap each node's children, then add children to the stack.
    """
    if not root:
        return None
    
    stack = [root]
    
    while stack:
        node = stack.pop()
        
        # Swap left and right children
        node.left, node.right = node.right, node.left
        
        # Add children to stack for processing
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    
    return root

def print_tree_inorder(root):
    """Helper function to print tree in-order for visualization"""
    if not root:
        return []
    
    result = []
    result.extend(print_tree_inorder(root.left))
    result.append(root.val)
    result.extend(print_tree_inorder(root.right))
    return result

def print_tree_level_order(root):
    """Helper function to print tree level by level"""
    if not root:
        return []
    
    from collections import deque
    queue = deque([root])
    result = []
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val if node else None)
            
            if node:
                queue.append(node.left)
                queue.append(node.right)
        
        # Only add level if it contains non-None values
        if any(val is not None for val in level):
            result.append(level)
    
    return result

# Example usage and testing
def invert_tree_safe(root, max_depth=1000):
    """
    Invert tree with depth limit to prevent stack overflow.
    
    Like the recursive version but with a safety net - stops if tree
    gets too deep to prevent stack overflow errors.
    """
    def invert_helper(node, depth):
        if not node:
            return None
            
        if depth > max_depth:
            raise RecursionError(f"Tree depth exceeds maximum allowed depth of {max_depth}")
        
        # Swap children
        node.left, node.right = node.right, node.left
        
        # Recursively invert with depth tracking
        invert_helper(node.left, depth + 1)
        invert_helper(node.right, depth + 1)
        
        return node
    
    return invert_helper(root, 0)

# Add comprehensive test cases
def test_edge_cases():
    """Test various edge cases for tree inversion"""
    
    # Test 1: Empty tree
    assert invert_tree(None) is None
    print("✅ Empty tree test passed")
    
    # Test 2: Single node
    single = TreeNode(42)
    inverted_single = invert_tree(single)
    assert inverted_single.val == 42
    assert inverted_single.left is None
    assert inverted_single.right is None
    print("✅ Single node test passed")
    
    # Test 3: Left-heavy tree
    left_heavy = TreeNode(1)
    left_heavy.left = TreeNode(2)
    left_heavy.left.left = TreeNode(3)
    
    invert_tree(left_heavy)
    assert left_heavy.right.val == 2
    assert left_heavy.right.right.val == 3
    print("✅ Left-heavy tree test passed")
    
    # Test 4: Cycle detection
    try:
        cyclic_root = TreeNode(1)
        cyclic_child = TreeNode(2)
        cyclic_root.left = cyclic_child
        cyclic_child.left = cyclic_root  # Creates cycle
        
        invert_tree(cyclic_root)
        print("❌ Cycle detection failed - should have raised error")
    except ValueError as e:
        print("✅ Cycle detection test passed")
    
    # Test 5: Maximum depth
    try:
        # Create very deep tree
        deep_root = TreeNode(0)
        current = deep_root
        for i in range(2000):  # Deeper than default recursion limit
            current.left = TreeNode(i)
            current = current.left
            
        invert_tree_safe(deep_root, max_depth=100)
        print("❌ Depth limit test failed - should have raised error")
    except RecursionError:
        print("✅ Maximum depth test passed")

if __name__ == "__main__":
    print("Running edge case tests...\n")
    test_edge_cases()

