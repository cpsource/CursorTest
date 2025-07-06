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

def polynomial_func(x, a, b, c):
    """2nd degree polynomial function for curve fitting"""
    return a * x**2 + b * x + c

def linear_func(x, a, b):
    """Linear function for curve fitting"""
    return a * x + b

def power_func(x, a, b, c):
    """Power function for curve fitting"""
    return a * np.power(x, b) + c

def fit_and_plot(x_data, y_data, filename):
    """Fit curves and create plot"""
    
    print(f"Data range: X = {x_data.min():.1f} to {x_data.max():.1f}")
    print(f"Data range: Y = {y_data.min():.1f} to {y_data.max():.1f}")
    
    # Try different fitting functions (simpler ones first)
    functions = [
        (linear_func, "Linear"),
        (polynomial_func, "Polynomial (2nd degree)"),
        (power_func, "Power function")
    ]
    
    best_fit = None
    best_r_squared = -np.inf
    best_params = None
    best_func = None
    best_name = ""
    
    for func, name in functions:
        try:
            # Fit the curve with bounds to prevent extreme values
            if func == power_func:
                # For power function, bound the exponent to reasonable values
                bounds = ([-np.inf, -2, -np.inf], [np.inf, 2, np.inf])
                popt, _ = curve_fit(func, x_data, y_data, bounds=bounds, maxfev=10000)
            else:
                popt, _ = curve_fit(func, x_data, y_data, maxfev=10000)
            
            # Calculate R-squared
            y_pred = func(x_data, *popt)
            
            # Skip if prediction contains NaN or inf
            if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
                print(f"{name}: Failed (invalid predictions)")
                continue
            
            ss_res = np.sum((y_data - y_pred) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            
            if ss_tot == 0:  # All y values are the same
                r_squared = 1.0 if ss_res == 0 else 0.0
            else:
                r_squared = 1 - (ss_res / ss_tot)
            
            print(f"{name}: R² = {r_squared:.4f}")
            
            if r_squared > best_r_squared:
                best_r_squared = r_squared
                best_params = popt
                best_func = func
                best_name = name
                
        except Exception as e:
            print(f"Could not fit {name}: {e}")
    
    # If no curve fitting worked, use simple linear interpolation
    if best_func is None:
        print("No curve fits successful, using linear interpolation")
        best_name = "Linear Interpolation"
        best_r_squared = 0.0
        # Use numpy's interp for simple interpolation
        x_smooth = np.linspace(x_data.min(), x_data.max(), 1000)
        y_smooth = np.interp(x_smooth, x_data, y_data)
    else:
        print(f"\nBest fit: {best_name} with R² = {best_r_squared:.4f}")
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x_data.min(), x_data.max(), 1000)
        y_smooth = best_func(x_smooth, *best_params)
        
        # Remove any NaN or infinite values from the smooth curve
        valid_mask = np.isfinite(y_smooth)
        x_smooth = x_smooth[valid_mask]
        y_smooth = y_smooth[valid_mask]
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot original data points
    plt.scatter(x_data, y_data, color='red', s=100, zorder=5, label='Data Points', alpha=0.8)
    
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
    if best_r_squared > 0:
        plt.text(0.02, 0.98, f'R² = {best_r_squared:.4f}', 
                 transform=plt.gca().transAxes, 
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Force the plot to show
    plt.show()
    print("Plot should now be displayed!")
    
    return best_func, best_params, best_r_squared

def main():
    if len(sys.argv) != 2:
        print("Usage: python curve_fit.py <input_file.csv>")
        print("Input file should contain comma-separated x,y values")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        x_data, y_data = read_data(filename)
        
        if len(x_data) < 2:
            print("Error: Need at least 2 data points for plotting")
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
