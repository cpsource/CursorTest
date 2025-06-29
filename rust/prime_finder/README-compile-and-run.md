# How to Compile and Run Rust Programs

## Method 1: Single File Compilation (Simple Programs)

### For a standalone .rs file:
```bash
# Compile the program
rustc main.rs

# Run the executable (on Linux/macOS)
./main

# Run the executable (on Windows)
main.exe
```

**Example:**
```bash
# Save the prime number code as "primes.rs"
rustc primes.rs
./primes  # or primes.exe on Windows
```

## Method 2: Using Cargo (Recommended for Projects)

Cargo is Rust's build system and package manager - think of it like Python's pip and virtualenv combined.

### Create a new Cargo project:
```bash
# Create a new project
cargo new prime_finder
cd prime_finder

# Or create in current directory
cargo init
```

### Project structure:
```
prime_finder/
├── Cargo.toml          # Project configuration (like Python's requirements.txt)
├── src/
│   └── main.rs         # Your code goes here
└── target/             # Compiled output (created after first build)
```

### Build and run with Cargo:
```bash
# Compile and run in one step (development mode)
cargo run

# Just compile (creates debug build)
cargo build

# Compile optimized version (for production)
cargo build --release

# Run tests
cargo test

# Check code without building (faster)
cargo check
```

## Step-by-Step Example

### 1. Install Rust (if not already installed):
Visit [rustup.rs](https://rustup.rs/) or run:
```bash
# On Unix-like systems
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts and restart your terminal
```

### 2. Create and run the prime number program:
```bash
# Create new project
cargo new prime_finder
cd prime_finder

# Replace contents of src/main.rs with the prime number code
# (copy the code from the previous artifact)

# Run the program
cargo run
```

### 3. Alternative - single file approach:
```bash
# Save code as primes.rs
rustc primes.rs
./primes  # Linux/macOS
# or
primes.exe  # Windows
```

## Key Differences Between Methods

| Feature | `rustc` (single file) | `cargo` (project) |
|---------|----------------------|-------------------|
| **Best for** | Simple scripts | Real projects |
| **Dependencies** | Manual management | Automatic via Cargo.toml |
| **Testing** | Manual | Built-in (`cargo test`) |
| **Optimization** | Manual flags | Easy (`--release`) |
| **Project structure** | Single file | Organized directories |

## Compilation Flags (for `rustc`)

```bash
# Basic compilation
rustc main.rs

# Optimized build
rustc -O main.rs

# Debug information
rustc -g main.rs

# Specify output name
rustc main.rs -o my_program

# Show warnings
rustc -W warnings main.rs
```

## Common Issues and Solutions

### Problem: "rustc: command not found"
**Solution:** Install Rust from [rustup.rs](https://rustup.rs/)

### Problem: "cargo: command not found" 
**Solution:** Cargo comes with Rust - restart terminal after installation

### Problem: Permission denied (Linux/macOS)
**Solution:** 
```bash
chmod +x ./program_name
./program_name
```

### Problem: External dependencies
**Solution:** Use Cargo and add dependencies to `Cargo.toml`:
```toml
[dependencies]
rand = "0.8"
```

## Pro Tips

1. **Use Cargo for anything beyond simple scripts** - it handles dependencies, testing, and project organization automatically
2. **`cargo check` is faster than `cargo build`** for syntax checking during development
3. **`cargo run --release`** for performance testing
4. **The `target/` directory can be safely deleted** - Cargo will rebuild everything
5. **Use `cargo fmt`** to automatically format your code
6. **Use `cargo clippy`** for additional linting and suggestions

Think of Cargo like Python's pip and setuptools combined - it manages your project structure, dependencies, and build process all in one tool!

