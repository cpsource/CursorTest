fn main() {
    println!("Finding all prime numbers from 1 to 100...\n");
    
    let primes = sieve_of_eratosthenes(100);
    
    println!("Prime numbers from 1 to 100:");
    print_primes(&primes);
    
    println!("\nTotal count: {} primes found", primes.len());
    
    // Demonstrate with a different range
    println!("\n--- Bonus: Primes from 1 to 50 ---");
    let primes_50 = sieve_of_eratosthenes(50);
    print_primes(&primes_50);
    println!("\nTotal count: {} primes found", primes_50.len());
}

/// Finds all prime numbers up to n using the Sieve of Eratosthenes algorithm
fn sieve_of_eratosthenes(n: usize) -> Vec<usize> {
    if n < 2 {
        return Vec::new();
    }
    
    // Create a boolean array "prime[0..=n]" and initialize all entries as true
    let mut is_prime = vec![true; n + 1];
    is_prime[0] = false; // 0 is not prime
    is_prime[1] = false; // 1 is not prime
    
    let mut p = 2;
    while p * p <= n {
        // If is_prime[p] is not changed, then it's a prime
        if is_prime[p] {
            // Mark all multiples of p as not prime
            let mut multiple = p * p;
            while multiple <= n {
                is_prime[multiple] = false;
                multiple += p;
            }
        }
        p += 1;
    }
    
    // Collect all prime numbers
    (2..=n).filter(|&i| is_prime[i]).collect()
}

/// Alternative implementation: Simple trial division method
#[allow(dead_code)]
fn is_prime(n: usize) -> bool {
    if n < 2 {
        return false;
    }
    if n == 2 {
        return true;
    }
    if n % 2 == 0 {
        return false;
    }
    
    // Check odd divisors up to sqrt(n)
    let sqrt_n = (n as f64).sqrt() as usize;
    for i in (3..=sqrt_n).step_by(2) {
        if n % i == 0 {
            return false;
        }
    }
    true
}

/// Alternative function to find primes using trial division
#[allow(dead_code)]
fn find_primes_trial_division(limit: usize) -> Vec<usize> {
    (1..=limit).filter(|&n| is_prime(n)).collect()
}

/// Helper function to print primes in a formatted way
fn print_primes(primes: &[usize]) {
    const PRIMES_PER_ROW: usize = 10;
    
    for (i, &prime) in primes.iter().enumerate() {
        print!("{:3}", prime);
        
        // Add spacing or newline
        if (i + 1) % PRIMES_PER_ROW == 0 {
            println!();
        } else {
            print!(" ");
        }
    }
    
    // Add final newline if needed
    if primes.len() % PRIMES_PER_ROW != 0 {
        println!();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_sieve_small_numbers() {
        assert_eq!(sieve_of_eratosthenes(10), vec![2, 3, 5, 7]);
        assert_eq!(sieve_of_eratosthenes(20), vec![2, 3, 5, 7, 11, 13, 17, 19]);
    }
    
    #[test]
    fn test_is_prime() {
        assert!(!is_prime(1));
        assert!(is_prime(2));
        assert!(is_prime(3));
        assert!(!is_prime(4));
        assert!(is_prime(5));
        assert!(!is_prime(9));
        assert!(is_prime(97));
    }
    
    #[test]
    fn test_edge_cases() {
        assert_eq!(sieve_of_eratosthenes(0), Vec::<usize>::new());
        assert_eq!(sieve_of_eratosthenes(1), Vec::<usize>::new());
        assert_eq!(sieve_of_eratosthenes(2), vec![2]);
    }
    
    #[test]
    fn test_both_methods_agree() {
        let sieve_result = sieve_of_eratosthenes(50);
        let trial_result = find_primes_trial_division(50);
        assert_eq!(sieve_result, trial_result);
    }
}

