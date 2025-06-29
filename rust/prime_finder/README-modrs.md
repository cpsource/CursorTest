# What's in mod.rs - Complete Guide

## What is mod.rs?

`mod.rs` is a special file that tells Rust "this directory is a module." It's like Python's `__init__.py` but more explicit about what's exposed.

## Basic Example

### Directory structure:
```
src/
├── main.rs
└── algorithms/
    ├── mod.rs           # ← This file makes "algorithms" a module
    ├── sieve.rs
    ├── trial.rs
    └── helpers.rs
```

### Simple mod.rs:
```rust
// src/algorithms/mod.rs

// Declare submodules (tells Rust these files exist)
pub mod sieve;
pub mod trial;
pub mod helpers;
```

That's it! The minimal `mod.rs` just declares which files are part of this module.

## Advanced mod.rs Features

### 1. Re-exporting for Convenience
```rust
// src/algorithms/mod.rs

pub mod sieve;
pub mod trial;
mod helpers;  // Note: no "pub" - this is private to this module

// Re-export commonly used items
pub use sieve::sieve_of_eratosthenes;
pub use trial::trial_division;
pub use helpers::is_prime;  // Can re-export from private modules

// Create type aliases
pub type PrimeList = Vec<usize>;

// Re-export with different names
pub use sieve::sieve_of_eratosthenes as sieve;
```

**Now users can do:**
```rust
use algorithms::sieve;  // Instead of algorithms::sieve::sieve_of_eratosthenes
use algorithms::PrimeList;
```

### 2. Module-level Functions and Constants
```rust
// src/algorithms/mod.rs

pub mod sieve;
pub mod trial;

// Constants available to all submodules and external users
pub const MAX_PRIME_LIMIT: usize = 1_000_000;

// Module-level functions
pub fn get_algorithm_info() -> &'static str {
    "Prime finding algorithms v1.0"
}

pub fn compare_algorithms(limit: usize) {
    println!("Comparing algorithms up to {}", limit);
    
    let sieve_result = sieve::sieve_of_eratosthenes(limit);
    let trial_result = trial::trial_division(limit);
    
    println!("Sieve found: {} primes", sieve_result.len());
    println!("Trial found: {} primes", trial_result.len());
}
```

### 3. Controlling Visibility
```rust
// src/algorithms/mod.rs

pub mod sieve;          // Public - can be used outside this module
pub mod trial;          // Public
mod helpers;            // Private - only this module can use it
mod benchmarks;         // Private

// Re-export selected items
pub use helpers::is_prime;  // Make this one function public
// Note: helpers module itself stays private

// Create a public interface that hides implementation details
pub fn find_primes(method: &str, limit: usize) -> Vec<usize> {
    match method {
        "sieve" => sieve::sieve_of_eratosthenes(limit),
        "trial" => trial::trial_division(limit),
        _ => panic!("Unknown method: {}", method),
    }
}
```

## Real-World Example

### Complete algorithms/mod.rs:
```rust
// src/algorithms/mod.rs

//! Prime number algorithms module
//! 
//! This module provides different algorithms for finding prime numbers.
//! 
//! # Examples
//! 
//! ```
//! use algorithms::find_primes_fast;
//! 
//! let primes = find_primes_fast(100);
//! println!("Found {} primes", primes.len());
//! ```

// Submodule declarations
pub mod sieve;
pub mod trial;
mod utils;              // Private utilities
mod benchmarks;         // Private benchmarking

// Re-exports for convenience
pub use sieve::sieve_of_eratosthenes;
pub use trial::trial_division;

// Type definitions
pub type PrimeList = Vec<usize>;
pub type PrimeSet = std::collections::HashSet<usize>;

// Constants
pub const DEFAULT_LIMIT: usize = 1000;
pub const SMALL_PRIME_THRESHOLD: usize = 100;

// Public API functions
pub fn find_primes_fast(limit: usize) -> PrimeList {
    if limit < SMALL_PRIME_THRESHOLD {
        trial_division(limit)
    } else {
        sieve_of_eratosthenes(limit)
    }
}

pub fn benchmark_all(limit: usize) {
    benchmarks::run_comparison(limit);
}

// Helper function using private modules
pub fn validate_primes(primes: &[usize]) -> bool {
    primes.iter().all(|&n| utils::is_prime_simple(n))
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_find_primes_fast() {
        let primes = find_primes_fast(20);
        assert_eq!(primes, vec![2, 3, 5, 7, 11, 13, 17, 19]);
    }
}
```

## Comparison with Python

| Rust | Python | Purpose |
|------|--------|---------|
| `mod.rs` | `__init__.py` | Make directory a module |
| `pub mod submodule;` | Files auto-discovered | Declare submodules |
| `pub use submodule::item;` | `from submodule import item` | Re-export items |
| `mod private_mod;` | `_private.py` convention | Private submodules |

## Python Analogy

**Python __init__.py:**
```python
# algorithms/__init__.py
from .sieve import sieve_of_eratosthenes
from .trial import trial_division

# Convenience function
def find_primes_fast(limit):
    if limit < 100:
        return trial_division(limit)
    else:
        return sieve_of_eratosthenes(limit)

__all__ = ['sieve_of_eratosthenes', 'trial_division', 'find_primes_fast']
```

**Rust mod.rs equivalent:**
```rust
// algorithms/mod.rs
pub mod sieve;
pub mod trial;

pub use sieve::sieve_of_eratosthenes;
pub use trial::trial_division;

pub fn find_primes_fast(limit: usize) -> Vec<usize> {
    if limit < 100 {
        trial_division(limit)
    } else {
        sieve_of_eratosthenes(limit)
    }
}
```

## Key Rules

1. **`mod.rs` is required** for subdirectories to be modules
2. **Only declared modules are visible** (unlike Python's auto-discovery)
3. **`pub mod` makes submodules public**, `mod` keeps them private
4. **`pub use` re-exports items** for easier access
5. **You can mix code and declarations** in `mod.rs`

Think of `mod.rs` as the "public interface" for your module directory - it controls what the outside world can see and how they access it!

