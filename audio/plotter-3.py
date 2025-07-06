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
    """Fit polynomial curve and create plot"""
    
    print(f"Data range: X = {x_data.min():.1f} to {x_data.max():.1f}")
    print(f"Data range: Y = {y_data.min():.1f} to {y_data.max():.1f}")
    print(f"Will plot {len(x_data)} data points")
    
    # Debug: Print each data point
    for i, (x, y) in enumerate(zip(x_data, y_data)):
        print(f"Point {i+1}: x={x:.1f}, y={y:.1f}")
    
    # Only use polynomial fitting
    try:
        # Fit 2nd degree polynomial
        popt, _ = curve_fit(polynomial_func, x_data, y_data, maxfev=10000)
        
        # Calculate R-squared
        y_pred = polynomial_func(x_data, *popt)
        
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        
        if ss_tot == 0:  # All y values are the same
            r_squared = 1.0 if ss_res == 0 else 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)
        
        print(f"Polynomial (2nd degree): R² = {r_squared:.4f}")
        
        best_name = "Polynomial (2nd degree)"
        best_r_squared = r_squared
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x_data.min(), x_data.max(), 1000)
        y_smooth = polynomial_func(x_smooth, *popt)
        
    except Exception as e:
        print(f"Polynomial fitting failed: {e}")
        print("Using linear interpolation as fallback")
        best_name = "Linear Interpolation"
        best_r_squared = 0.0
        x_smooth = np.linspace(x_data.min(), x_data.max(), 1000)
        y_smooth = np.interp(x_smooth, x_data, y_data)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot original data points
    plt.scatter(x_data, y_data, color='red', s=100, zorder=5, label='Data Points', alpha=0.8)
    
    # Plot fitted curve
    plt.plot(x_smooth, y_smooth, 'b-', linewidth=2, label=f'Fitted Curve ({best_name})')
    
    # Set axis properties (fixed as in your original)
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
    
    # Force the plot to show and add debugging
    print(f"Plotting {len(x_data)} data points and {len(x_smooth)} curve points")
    print(f"X-axis range: {plt.xlim()}")
    print(f"Y-axis range: {plt.ylim()}")
    
    plt.show()
    print("Plot should now be displayed!")
    
    # Alternative: save to file as backup
    plt.savefig('curve_fit_plot.png', dpi=150, bbox_inches='tight')
    print("Plot also saved as 'curve_fit_plot.png'")
    
    return best_name, best_r_squared

def main():
    # Use hardcoded filename as in your version
    filename = "right-ear.csv"
    
    try:
        x_data, y_data = read_data(filename)
        
        if len(x_data) < 2:
            print("Error: Need at least 2 data points for plotting")
            sys.exit(1)
        
        print(f"Loaded {len(x_data)} data points from {filename}")
        print("Data points:")
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            print(f"  {i+1}: ({x:.1f}, {y:.1f})")
        
        print("\nUsing polynomial curve fitting...")
        fit_and_plot(x_data, y_data, filename)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
