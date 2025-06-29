# Adding Multiple Files to Rust Projects

## Basic Project Structure

```
prime_finder/
├── Cargo.toml
└── src/
    ├── main.rs          # Entry point (like Python's if __name__ == "__main__")
    ├── lib.rs           # Library root (optional)
    ├── primes.rs        # Custom module
    ├── math_utils.rs    # Another module
    └── algorithms/      # Submodule directory
        ├── mod.rs       # Module declaration file
        ├── sieve.rs     # Sieve algorithm
        └── trial.rs     # Trial division algorithm
```

## Method 1: Simple Additional Files (Modules)

### Step 1: Create the module file
Create `src/primes.rs`:
```rust
// src/primes.rs
pub fn sieve_of_eratosthenes(n: usize) -> Vec<usize> {
    if n < 2 {
        return Vec::new();
    }
    
    let mut is_prime = vec![true; n + 1];
    is_prime[0] = false;
    is_prime[1] = false;
    
    let mut p = 2;
    while p * p <= n {
        if is_prime[p] {
            let mut multiple = p * p;
            while multiple <= n {
                is_prime[multiple] = false;
                multiple += p;
            }
        }
        p += 1;
    }
    
    (2..=n).filter(|&i| is_prime[i]).collect()
}

pub fn is_prime(n: usize) -> bool {
    if n < 2 { return false; }
    if n == 2 { return true; }
    if n % 2 == 0 { return false; }
    
    let sqrt_n = (n as f64).sqrt() as usize;
    for i in (3..=sqrt_n).step_by(2) {
        if n % i == 0 {
            return false;
        }
    }
    true
}
```

### Step 2: Declare and use the module in main.rs
```rust
// src/main.rs
mod primes;  // This tells Rust to include the primes.rs file

fn main() {
    println!("Finding primes using external module...");
    
    // Use functions from the primes module
    let primes = primes::sieve_of_eratosthenes(100);
    println!("Found {} primes: {:?}", primes.len(), primes);
    
    // Test individual numbers
    println!("Is 17 prime? {}", primes::is_prime(17));
    println!("Is 20 prime? {}", primes::is_prime(20));
}
```

## Method 2: Organized Submodules

### Create subdirectory structure:
```
src/
├── main.rs
├── math_utils.rs
└── algorithms/
    ├── mod.rs           # Required for subdirectories
    ├── sieve.rs
    └── trial.rs
```

### Step 1: Create the submodule files

**src/algorithms/mod.rs** (module declaration):
```rust
// src/algorithms/mod.rs
pub mod sieve;      // Declares sieve.rs
pub mod trial;      // Declares trial.rs

// Re-export commonly used items for convenience
pub use sieve::sieve_of_eratosthenes;
pub use trial::trial_division_primes;
```

**src/algorithms/sieve.rs**:
```rust
// src/algorithms/sieve.rs
pub fn sieve_of_eratosthenes(n: usize) -> Vec<usize> {
    // Implementation here (same as before)
    if n < 2 { return Vec::new(); }
    
    let mut is_prime = vec![true; n + 1];
    is_prime[0] = false;
    is_prime[1] = false;
    
    let mut p = 2;
    while p * p <= n {
        if is_prime[p] {
            let mut multiple = p * p;
            while multiple <= n {
                is_prime[multiple] = false;
                multiple += p;
            }
        }
        p += 1;
    }
    
    (2..=n).filter(|&i| is_prime[i]).collect()
}
```

**src/algorithms/trial.rs**:
```rust
// src/algorithms/trial.rs
pub fn trial_division_primes(limit: usize) -> Vec<usize> {
    (2..=limit).filter(|&n| is_prime(n)).collect()
}

fn is_prime(n: usize) -> bool {
    if n < 2 { return false; }
    if n == 2 { return true; }
    if n % 2 == 0 { return false; }
    
    let sqrt_n = (n as f64).sqrt() as usize;
    for i in (3..=sqrt_n).step_by(2) {
        if n % i == 0 {
            return false;
        }
    }
    true
}
```

**src/math_utils.rs**:
```rust
// src/math_utils.rs
pub fn print_primes(primes: &[usize]) {
    const PRIMES_PER_ROW: usize = 10;
    
    for (i, &prime) in primes.iter().enumerate() {
        print!("{:3}", prime);
        if (i + 1) % PRIMES_PER_ROW == 0 {
            println!();
        } else {
            print!(" ");
        }
    }
    if primes.len() % PRIMES_PER_ROW != 0 {
        println!();
    }
}

pub fn benchmark_algorithm<F>(name: &str, f: F, limit: usize) 
where 
    F: Fn(usize) -> Vec<usize>
{
    let start = std::time::Instant::now();
    let primes = f(limit);
    let duration = start.elapsed();
    
    println!("{}: Found {} primes in {:?}", name, primes.len(), duration);
}
```

### Step 2: Use everything in main.rs
```rust
// src/main.rs
mod algorithms;     // Include the algorithms subdirectory
mod math_utils;     // Include math_utils.rs

use algorithms::{sieve_of_eratosthenes, trial_division_primes};
use math_utils::{print_primes, benchmark_algorithm};

fn main() {
    println!("Comparing different prime finding algorithms:\n");
    
    let limit = 1000;
    
    // Benchmark both algorithms
    benchmark_algorithm("Sieve of Eratosthenes", sieve_of_eratosthenes, limit);
    benchmark_algorithm("Trial Division", trial_division_primes, limit);
    
    // Show first 100 primes nicely formatted
    println!("\nFirst 100 primes:");
    let primes = sieve_of_eratosthenes(100);
    print_primes(&primes);
}
```

## Method 3: Using lib.rs (Library Structure)

For larger projects, you might want a library structure:

**src/lib.rs** (library root):
```rust
// src/lib.rs
pub mod algorithms;
pub mod math_utils;

// Re-export main functionality
pub use algorithms::sieve::sieve_of_eratosthenes;
pub use math_utils::print_primes;
```

**src/main.rs** (binary using the library):
```rust
// src/main.rs
use prime_finder::{sieve_of_eratosthenes, print_primes};

fn main() {
    let primes = sieve_of_eratosthenes(100);
    print_primes(&primes);
}
```

## Key Rules and Tips

### Module Declaration Rules:
1. **`mod module_name;`** - looks for `module_name.rs` or `module_name/mod.rs`
2. **Functions/structs must be `pub`** to be used outside their module
3. **Subdirectories need `mod.rs`** to be recognized as modules
4. **Use `use` statements** to bring items into scope (like Python imports)

### Python Analogy:
```rust
mod algorithms;                    // like: import algorithms
use algorithms::sieve;             // like: from algorithms import sieve
use algorithms::sieve::*;          // like: from algorithms.sieve import *
```

### Best Practices:
1. **One module per file** - keeps code organized
2. **Use `pub` sparingly** - only expose what others need
3. **Group related functionality** in the same module
4. **Use `mod.rs`** to control what's exported from subdirectories
5. **Re-export common items** in `mod.rs` for convenience

This structure scales really well - think of each module like a Python file, and subdirectories like Python packages with `__init__.py` files (that's what `mod.rs` is)!

