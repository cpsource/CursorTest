# Cargo.toml Guide - When and How to Update

## What's in Cargo.toml Initially

When you run `cargo new prime_finder`, you get:

```toml
[package]
name = "prime_finder"
version = "0.1.0"
edition = "2021"

[dependencies]
```

## Common Updates You'll Make

### 1. Adding Dependencies (Most Common)

**Adding external crates:**
```toml
[dependencies]
rand = "0.8"                    # Random number generation
serde = { version = "1.0", features = ["derive"] }  # Serialization
clap = "4.0"                    # Command line argument parsing
tokio = { version = "1", features = ["full"] }      # Async runtime
```

**Different dependency types:**
```toml
[dependencies]
# From crates.io (default)
regex = "1.5"

# From git repository
my-lib = { git = "https://github.com/user/my-lib" }

# From local path
my-local-lib = { path = "../my-local-lib" }

# With specific features
serde = { version = "1.0", features = ["derive"], default-features = false }

[dev-dependencies]
# Only used for tests and examples
criterion = "0.5"       # Benchmarking
proptest = "1.0"        # Property-based testing

[build-dependencies]
# Used in build scripts
cc = "1.0"
```

### 2. Project Metadata Updates

```toml
[package]
name = "prime_finder"
version = "0.2.0"              # Update version for releases
edition = "2021"
authors = ["Your Name <you@example.com>"]
license = "MIT OR Apache-2.0"
description = "A fast prime number finder"
homepage = "https://github.com/yourusername/prime_finder"
repository = "https://github.com/yourusername/prime_finder"
readme = "README.md"
keywords = ["math", "primes", "algorithms"]
categories = ["algorithms", "mathematics"]
exclude = ["tests/large_files/", "docs/"]
```

### 3. Build Configuration

```toml
# Multiple binaries
[[bin]]
name = "prime_finder"
path = "src/main.rs"

[[bin]]
name = "prime_bench"
path = "src/bin/benchmark.rs"

# Library configuration
[lib]
name = "prime_algorithms"
path = "src/lib.rs"
crate-type = ["cdylib", "rlib"]  # For creating shared libraries

# Examples
[[example]]
name = "basic_usage"
path = "examples/basic.rs"

# Tests
[[test]]
name = "integration"
path = "tests/integration_test.rs"

# Benchmarks
[[bench]]
name = "prime_benchmarks"
path = "benches/prime_bench.rs"
harness = false  # Use criterion instead of built-in bencher
```

### 4. Compilation Profiles

```toml
# Optimize for different scenarios
[profile.release]
opt-level = 3               # Maximum optimization
lto = true                  # Link-time optimization
codegen-units = 1          # Better optimization, slower compile
panic = "abort"            # Smaller binaries
strip = true               # Remove debug symbols

[profile.dev]
opt-level = 0              # Fast compilation
debug = true               # Include debug info
panic = "unwind"           # Better for debugging

# Custom profile for profiling
[profile.profiling]
inherits = "release"
debug = 1                  # Some debug info for profilers
```

### 5. Features (Advanced)

```toml
[features]
default = ["std"]
std = []                           # Standard library support
parallel = ["rayon"]               # Parallel processing
gpu = ["opencl"]                   # GPU acceleration
extra-algorithms = ["num-bigint"]  # Additional algorithms

# Optional dependencies
[dependencies]
rayon = { version = "1.5", optional = true }
opencl = { version = "0.13", optional = true }
num-bigint = { version = "0.4", optional = true }
```

### 6. Workspace Configuration (Multi-Package Projects)

```toml
# In root Cargo.toml for workspace
[workspace]
members = [
    "prime_finder",
    "prime_algorithms",
    "prime_benchmarks",
]
exclude = ["old_versions/"]

# Shared dependencies for all workspace members
[workspace.dependencies]
serde = "1.0"
tokio = "1.0"
```

## Real-World Example: Updated Cargo.toml

```toml
[package]
name = "prime_finder"
version = "1.2.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
license = "MIT"
description = "High-performance prime number algorithms with CLI interface"
homepage = "https://github.com/yourusername/prime_finder"
repository = "https://github.com/yourusername/prime_finder"
readme = "README.md"
keywords = ["math", "primes", "algorithms", "cli"]
categories = ["command-line-utilities", "algorithms"]

[dependencies]
clap = { version = "4.0", features = ["derive"] }    # CLI argument parsing
rayon = { version = "1.7", optional = true }         # Parallel processing
serde = { version = "1.0", features = ["derive"] }   # Serialization
serde_json = "1.0"                                   # JSON support
num-format = "0.4"                                   # Number formatting
indicatif = "0.17"                                   # Progress bars

[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }
proptest = "1.0"
tempfile = "3.0"

[features]
default = ["parallel"]
parallel = ["dep:rayon"]
benchmark = []

[[bin]]
name = "prime_finder"
path = "src/main.rs"

[[bin]]
name = "prime_server"
path = "src/bin/server.rs"
required-features = ["serde"]

[[bench]]
name = "algorithm_benchmarks"
harness = false

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

## When to Update Cargo.toml

### Always update when:
- **Adding new dependencies** (`cargo add serde`)
- **Updating dependency versions** (`cargo update`)
- **Adding new binaries/examples/tests**
- **Preparing for release** (version bump)
- **Changing project metadata**

### Useful commands:
```bash
# Add dependency automatically
cargo add serde --features derive

# Add dev dependency
cargo add --dev criterion

# Update all dependencies
cargo update

# Check for outdated dependencies
cargo outdated

# Show dependency tree
cargo tree
```

## Python Analogy

| Python | Rust | Purpose |
|--------|------|---------|
| `requirements.txt` | `[dependencies]` | Runtime dependencies |
| `setup.py` | `[package]` | Project metadata |
| `pyproject.toml` | `Cargo.toml` | Everything in one file |
| `pip install package` | `cargo add package` | Add dependency |
| `pip install -e .` | `cargo install --path .` | Install locally |

Think of `Cargo.toml` as your project's control center - you'll be editing it regularly as your project grows and evolves!
