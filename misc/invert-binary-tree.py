# Definition for a binary tree node
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode({self.val})"

def invert_tree(root):
    """
    Inverts a binary tree recursively.
    
    Think of it like looking at a tree in a mirror - everything flips horizontally.
    Each node's left child becomes its right child, and vice versa.
    
    Args:
        root: TreeNode - The root of the binary tree
    
    Returns:
        TreeNode - The root of the inverted tree
    """
    # Base case: if node is None, return None
    if not root:
        return None
    
    # Swap the left and right children
    root.left, root.right = root.right, root.left
    
    # Recursively invert the left and right subtrees
    invert_tree(root.left)
    invert_tree(root.right)
    
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
if __name__ == "__main__":
    # Create a sample binary tree:
    #       4
    #      / \
    #     2   7
    #    / \ / \
    #   1  3 6  9
    
    root = TreeNode(4)
    root.left = TreeNode(2)
    root.right = TreeNode(7)
    root.left.left = TreeNode(1)
    root.left.right = TreeNode(3)
    root.right.left = TreeNode(6)
    root.right.right = TreeNode(9)
    
    print("Original tree (level order):")
    print(print_tree_level_order(root))
    
    print("\nOriginal tree (inorder):")
    print(print_tree_inorder(root))
    
    # Invert the tree
    inverted_root = invert_tree(root)
    
    print("\nInverted tree (level order):")
    print(print_tree_level_order(inverted_root))
    
    print("\nInverted tree (inorder):")
    print(print_tree_inorder(inverted_root))
    
    # Expected result after inversion:
    #       4
    #      / \
    #     7   2
    #    / \ / \
    #   9  6 3  1

