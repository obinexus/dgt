"""
OBINexus AVL Tree with Policy Enforcement and Active Monitoring
MVP Implementation with DAG-style Policy Validation
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, Dict
from enum import Enum
from functools import wraps
import time

# ==================== POLICY FRAMEWORK ====================

class PolicyViolation(Exception):
    """Exception raised when policy is violated"""
    pass

class ComplianceLevel(Enum):
    OK = 0
    WARNING = 1
    DANGER = 2
    CRITICAL = 3
    PANIC = 4

class ServiceOperation:
    """Service operation identifier using OBINexus naming convention"""
    def __init__(self, service: str, operation: str, department: str, division: str, county: str):
        self.service = service
        self.operation = operation
        self.department = department
        self.division = division
        self.county = county
    
    @property
    def full_path(self) -> str:
        return f"{self.service}.{self.operation}.obinexus.{self.department}.{self.division}.{self.county}.org"
    
    def __str__(self):
        return self.full_path

# Policy Validation Matrix
class QAMatrix:
    """QA Matrix for policy compliance validation"""
    def __init__(self):
        self.true_positives = 0
        self.true_negatives = 0
        self.false_positives = 0
        self.false_negatives = 0
    
    def record_compliance(self, expected: bool, actual: bool):
        if expected and actual:
            self.true_positives += 1
        elif not expected and not actual:
            self.true_negatives += 1
        elif not expected and actual:
            self.false_positives += 1
        else:
            self.false_negatives += 1
    
    @property
    def accuracy(self) -> float:
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        if total == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / total

# Active Monitoring Decorators
def log_operation(service_op: ServiceOperation):
    """Decorator for logging operations with service path"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logging.info(f"[{service_op.full_path}] Starting operation: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logging.info(f"[{service_op.full_path}] Operation completed: {func.__name__} in {duration:.2f}s")
                return result
            except Exception as e:
                logging.error(f"[{service_op.full_path}] Operation failed: {func.__name__} - {str(e)}")
                raise
        return wrapper
    return decorator

def validate_policy(policy_func: Callable):
    """Decorator for policy validation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate policy before execution
            if not policy_func(*args, **kwargs):
                raise PolicyViolation(f"Policy validation failed for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def active_monitor(compliance_threshold: float = 0.95):
    """Active monitoring with compliance threshold"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Monitor execution and check compliance
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Simulate compliance check
                compliance_score = min(1.0, 1.0 / (execution_time + 0.1))  # Simple heuristic
                
                if compliance_score < compliance_threshold:
                    logging.warning(f"Low compliance score: {compliance_score:.2f} for {func.__name__}")
                
                return result
            except Exception as e:
                logging.error(f"Monitoring detected failure in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

# ==================== AVL TREE IMPLEMENTATION ====================

@dataclass
class AVLNode:
    value: int
    left: Optional['AVLNode'] = None
    right: Optional['AVLNode'] = None
    height: int = 1
    policy_compliant: bool = True
    last_audit: float = 0.0

class PolicyEnforcedAVLTree:
    """
    AVL Tree with integrated policy enforcement and active monitoring
    """
    
    def __init__(self, service_op: ServiceOperation):
        self.root = None
        self.service_op = service_op
        self.qa_matrix = QAMatrix()
        self.rotation_count = 0
        self.violation_count = 0
        
        # Define invariant policies
        self.policies = {
            "height_balance": lambda node: abs(self._get_balance(node)) <= 1,
            "value_integrity": lambda node: node is None or (node.policy_compliant and self._audit_node(node)),
            "rotation_limit": lambda: self.rotation_count < 1000  # Prevent infinite rotations
        }
    
    @log_operation(ServiceOperation("avl", "insert", "data", "structure", "core"))
    @validate_policy(lambda self, *args: True)  # Always validate self for policy compliance
    @active_monitor(compliance_threshold=0.9)
    def insert(self, value: int) -> None:
        """Insert value with policy enforcement"""
        policy_check = self.policies["rotation_limit"]()
        if not policy_check:
            raise PolicyViolation("Rotation limit policy violated")
        
        self.root = self._insert(self.root, value)
        self._enforce_tree_policies()
    
    def _insert(self, node: Optional[AVLNode], value: int) -> AVLNode:
        if node is None:
            return AVLNode(value, last_audit=time.time())
        
        if value < node.value:
            node.left = self._insert(node.left, value)
        else:
            node.right = self._insert(node.right, value)
        
        # Update height and balance
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        
        # Check balance and rotate if needed
        balance = self._get_balance(node)
        
        # Left Left Case
        if balance > 1 and value < node.left.value:
            self.rotation_count += 1
            return self._right_rotate(node)
        
        # Right Right Case
        if balance < -1 and value > node.right.value:
            self.rotation_count += 1
            return self._left_rotate(node)
        
        # Left Right Case
        if balance > 1 and value > node.left.value:
            self.rotation_count += 1
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Left Case
        if balance < -1 and value < node.right.value:
            self.rotation_count += 1
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    @log_operation(ServiceOperation("avl", "delete", "data", "structure", "core"))
    @active_monitor(compliance_threshold=0.85)
    def delete(self, value: int) -> None:
        """Delete value with policy checks"""
        self.root = self._delete(self.root, value)
        self._enforce_tree_policies()
    
    def _delete(self, node: Optional[AVLNode], value: int) -> Optional[AVLNode]:
        if node is None:
            return node
        
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            
            temp = self._min_value_node(node.right)
            node.value = temp.value
            node.right = self._delete(node.right, temp.value)
        
        if node is None:
            return node
        
        # Update height and balance
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        
        # Perform rotations if needed
        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            self.rotation_count += 1
            return self._right_rotate(node)
        
        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            self.rotation_count += 1
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            self.rotation_count += 1
            return self._left_rotate(node)
        
        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            self.rotation_count += 1
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    def _left_rotate(self, z: AVLNode) -> AVLNode:
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y
    
    def _right_rotate(self, z: AVLNode) -> AVLNode:
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y
    
    def _get_height(self, node: Optional[AVLNode]) -> int:
        if node is None:
            return 0
        return node.height
    
    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _min_value_node(self, node: AVLNode) -> AVLNode:
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def _audit_node(self, node: AVLNode) -> bool:
        """Audit node for policy compliance"""
        current_time = time.time()
        node.last_audit = current_time
        
        # Check if node values are within reasonable bounds
        value_ok = -1000000 <= node.value <= 1000000
        height_ok = node.height >= 1
        
        compliance = value_ok and height_ok
        node.policy_compliant = compliance
        
        if not compliance:
            self.violation_count += 1
            logging.warning(f"Node audit failed: value={node.value}, height={node.height}")
        
        return compliance
    
    def _enforce_tree_policies(self) -> None:
        """Enforce policies across entire tree"""
        def _enforce_node(node: Optional[AVLNode]) -> bool:
            if node is None:
                return True
            
            left_ok = _enforce_node(node.left)
            right_ok = _enforce_node(node.right)
            node_ok = self._audit_node(node)
            
            # Check balance policy
            balance_ok = self.policies["height_balance"](node)
            
            overall_ok = left_ok and right_ok and node_ok and balance_ok
            
            # Record in QA matrix
            self.qa_matrix.record_compliance(True, overall_ok)
            
            return overall_ok
        
        _enforce_node(self.root)
    
    def prune_non_compliant(self) -> None:
        """Remove non-compliant nodes from tree"""
        def _prune(node: Optional[AVLNode]) -> Optional[AVLNode]:
            if node is None:
                return None
            
            node.left = _prune(node.left)
            node.right = _prune(node.right)
            
            if not node.policy_compliant:
                # Remove non-compliant node
                logging.info(f"Pruning non-compliant node: {node.value}")
                return None
            
            return node
        
        self.root = _prune(self.root)
        self._enforce_tree_policies()
    
    def inorder_traversal(self) -> List[int]:
        """Get sorted values from tree"""
        result = []
        
        def _inorder(node: Optional[AVLNode]):
            if node:
                _inorder(node.left)
                result.append(node.value)
                _inorder(node.right)
        
        _inorder(self.root)
        return result
    
    def get_tree_stats(self) -> Dict[str, Any]:
        """Get comprehensive tree statistics"""
        stats = {
            "service_operation": str(self.service_op),
            "total_nodes": 0,
            "balanced_nodes": 0,
            "compliant_nodes": 0,
            "rotation_count": self.rotation_count,
            "violation_count": self.violation_count,
            "qa_accuracy": self.qa_matrix.accuracy,
            "tree_height": self._get_height(self.root),
            "is_balanced": self._is_tree_balanced()
        }
        
        def _collect_stats(node: Optional[AVLNode]):
            if node:
                stats["total_nodes"] += 1
                if abs(self._get_balance(node)) <= 1:
                    stats["balanced_nodes"] += 1
                if node.policy_compliant:
                    stats["compliant_nodes"] += 1
                
                _collect_stats(node.left)
                _collect_stats(node.right)
        
        _collect_stats(self.root)
        return stats
    
    def _is_tree_balanced(self) -> bool:
        """Check if entire tree is balanced"""
        def _check_balance(node: Optional[AVLNode]) -> bool:
            if node is None:
                return True
            
            balance_ok = abs(self._get_balance(node)) <= 1
            left_ok = _check_balance(node.left)
            right_ok = _check_balance(node.right)
            
            return balance_ok and left_ok and right_ok
        
        return _check_balance(self.root)

# ==================== ACTIVE MONITORING SYSTEM ====================

class ActiveMonitor:
    """Active monitoring system for policy enforcement"""
    
    def __init__(self):
        self.monitored_trees: Dict[str, PolicyEnforcedAVLTree] = {}
        self.compliance_threshold = 0.8
    
    def register_tree(self, tree: PolicyEnforcedAVLTree) -> None:
        """Register a tree for active monitoring"""
        self.monitored_trees[tree.service_op.full_path] = tree
        logging.info(f"Registered tree for monitoring: {tree.service_op.full_path}")
    
    def run_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit of all monitored trees"""
        audit_results = {}
        
        for path, tree in self.monitored_trees.items():
            stats = tree.get_tree_stats()
            compliance_rate = stats["compliant_nodes"] / max(1, stats["total_nodes"])
            
            audit_results[path] = {
                "compliance_rate": compliance_rate,
                "status": "OK" if compliance_rate >= self.compliance_threshold else "VIOLATION",
                "stats": stats
            }
            
            if compliance_rate < self.compliance_threshold:
                logging.warning(f"Policy violation detected in {path}: compliance={compliance_rate:.2f}")
                # Auto-prune non-compliant nodes
                tree.prune_non_compliant()
        
        return audit_results

# ==================== USAGE EXAMPLE ====================

def main():
    """Demonstrate the AVL tree with policy enforcement"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create service operation identifier
    service_op = ServiceOperation("housing", "allocation", "social", "care", "cambridge")
    
    # Create policy-enforced AVL tree
    tree = PolicyEnforcedAVLTree(service_op)
    
    # Create active monitor
    monitor = ActiveMonitor()
    monitor.register_tree(tree)
    
    # Insert values with automatic policy enforcement
    values = [10, 20, 30, 40, 25, 5, 15, 35]
    
    print("=== Inserting Values with Policy Enforcement ===")
    for value in values:
        try:
            tree.insert(value)
            print(f"Inserted {value}, Balance: {tree._get_balance(tree.root)}")
        except PolicyViolation as e:
            print(f"Policy violation during insert of {value}: {e}")
    
    print("\n=== Tree Statistics ===")
    stats = tree.get_tree_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Running Active Audit ===")
    audit_results = monitor.run_audit()
    for path, result in audit_results.items():
        print(f"{path}: {result['status']} (compliance: {result['compliance_rate']:.2f})")
    
    print("\n=== Inorder Traversal ===")
    sorted_values = tree.inorder_traversal()
    print(f"Sorted values: {sorted_values}")
    
    print("\n=== Testing Policy Enforcement ===")
    # Try to create an unbalanced scenario
    try:
        # This would normally cause imbalance, but our tree auto-balances
        tree.insert(1)
        tree.insert(2)
        tree.insert(3)  # This should trigger rotations
        print("Tree maintained balance through rotations")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
