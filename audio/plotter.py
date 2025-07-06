import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
import csv

def read_data(filename):
    """Read data points from CSV file"""
    x_data = []
    y_data = []
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                try:
                    x_data.append(float(row[0]))
                    y_data.append(float(row[1]))
                except ValueError:
                    continue  # Skip non-numeric rows
    
    return np.array(x_data), np.array(y_data)

def polynomial_func(x, a, b, c, d):
    """3rd degree polynomial function for curve fitting"""
    return a * x**3 + b * x**2 + c * x + d

def exponential_func(x, a, b, c):
    """Exponential function for curve fitting"""
    return a * np.exp(b * x) + c

def logarithmic_func(x, a, b, c):
    """Logarithmic function for curve fitting"""
    return a * np.log(b * x) + c

def fit_and_plot(x_data, y_data, filename):
    """Fit curves and create plot"""
    
    # Try different fitting functions
    functions = [
        (polynomial_func, "Polynomial (3rd degree)"),
        (exponential_func, "Exponential"),
        (logarithmic_func, "Logarithmic")
    ]
    
    best_fit = None
    best_r_squared = -np.inf
    best_params = None
    best_func = None
    best_name = ""
    
    for func, name in functions:
        try:
            # Fit the curve
            popt, _ = curve_fit(func, x_data, y_data, maxfev=10000)
            
            # Calculate R-squared
            y_pred = func(x_data, *popt)
            ss_res = np.sum((y_data - y_pred) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            
            print(f"{name}: R² = {r_squared:.4f}")
            
            if r_squared > best_r_squared:
                best_r_squared = r_squared
                best_params = popt
                best_func = func
                best_name = name
                
        except Exception as e:
            print(f"Could not fit {name}: {e}")
    
    if best_func is None:
        print("No successful curve fits found!")
        return
    
    print(f"\nBest fit: {best_name} with R² = {best_r_squared:.4f}")
    
    # Create smooth curve for plotting
    x_smooth = np.linspace(250, 8000, 1000)
    y_smooth = best_func(x_smooth, *best_params)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot original data points
    plt.scatter(x_data, y_data, color='red', s=100, zorder=5, label='Data Points')
    
    # Plot fitted curve
    plt.plot(x_smooth, y_smooth, 'b-', linewidth=2, label=f'Fitted Curve ({best_name})')
    
    # Set axis properties
    plt.xlim(250, 8000)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()  # Invert y-axis so 0 is at top
    
    # Set logarithmic scale for x-axis (typical for frequency)
    plt.xscale('log')
    
    # Set tick marks
    plt.xticks([250, 500, 1000, 2000, 4000, 8000], 
               ['250Hz', '500Hz', '1kHz', '2kHz', '4kHz', '8kHz'])
    plt.yticks(range(0, 101, 10))
    
    # Labels and title
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Level (dB)', fontsize=12)
    plt.title(f'Curve Fit Analysis - {filename}', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Add R-squared annotation
    plt.text(0.02, 0.98, f'R² = {best_r_squared:.4f}', 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.show()
    
    return best_func, best_params, best_r_squared

def main():
    if len(sys.argv) != 2:
        print("Usage: python curve_fit.py <input_file.csv>")
        print("Input file should contain comma-separated x,y values")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        x_data, y_data = read_data(filename)
        
        if len(x_data) < 3:
            print("Error: Need at least 3 data points for curve fitting")
            sys.exit(1)
        
        print(f"Loaded {len(x_data)} data points from {filename}")
        print("Data points:")
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            print(f"  {i+1}: ({x:.1f}, {y:.1f})")
        
        print("\nTrying different curve fitting methods...")
        fit_and_plot(x_data, y_data, filename)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

