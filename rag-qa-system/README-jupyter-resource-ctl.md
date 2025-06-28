Great question! Resource control in systemd services happens through **systemd directives** in the service file and **cgroups** (control groups) under the hood. Think of it like setting **speed limits and guardrails** for your Jupyter service.

## Resource Limits in the Service File

Here's where you control resources in `/etc/systemd/system/jupyter.service`:

```ini
[Service]
# Memory limits
MemoryHigh=2G          # Soft limit - warns when exceeded
MemoryMax=4G           # Hard limit - kills process if exceeded
MemorySwapMax=1G       # Limit swap usage

# CPU limits  
CPUQuota=200%          # Max 200% CPU (2 cores worth)
CPUWeight=100          # CPU scheduling priority (1-10000)

# File descriptor limits
LimitNOFILE=65536      # Max open files
LimitNPROC=1024        # Max processes/threads

# Time limits
TimeoutStartSec=60     # Kill if doesn't start in 60s
TimeoutStopSec=30      # Force kill if doesn't stop in 30s
RuntimeMaxSec=86400    # Auto-restart after 24 hours

# I/O limits
IOWeight=100           # I/O scheduling priority
BlockIOWeight=100      # Block device I/O weight

# Network (if systemd supports it)
IPAccounting=yes       # Enable network accounting
```

Think of these like **circuit breakers** in electrical systems - they prevent one component from taking down the whole system.

## Complete Service File with Resource Controls:

```ini
[Unit]
Description=Jupyter Lab Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=jupyter
Group=jupyter
WorkingDirectory=/home/jupyter/notebooks
ExecStart=/home/jupyter/venv/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# Restart policy
Restart=always
RestartSec=10
StartLimitBurst=3      # Only restart 3 times
StartLimitIntervalSec=60  # In a 60-second window

# Memory Management
MemoryHigh=2G          # Start warning/throttling at 2GB
MemoryMax=4G           # Hard kill at 4GB
MemorySwapMax=512M     # Limit swap to 512MB

# CPU Management  
CPUQuota=150%          # Limit to 1.5 CPU cores
CPUWeight=100          # Normal CPU priority

# Process/File Limits
LimitNOFILE=65536      # Max 65K open files
LimitNPROC=512         # Max 512 processes
LimitCORE=0            # No core dumps

# Time Limits
TimeoutStartSec=120    # 2 minutes to start
TimeoutStopSec=30      # 30 seconds to stop gracefully
RuntimeMaxSec=0        # No runtime limit (0 = infinite)

# I/O Limits
IOWeight=100           # Normal I/O priority

# Security + Resource isolation
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/jupyter

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jupyter

[Install]
WantedBy=multi-user.target
```

## Monitor Resource Usage

### **Real-time Monitoring:**
```bash
# Watch systemd resource usage
sudo systemctl status jupyter

# Detailed resource stats
sudo systemd-cgtop

# Specific service resources
sudo systemctl show jupyter --property=MemoryCurrent,CPUUsageNSec,TasksCurrent

# Watch memory usage live
watch -n 1 'sudo systemctl show jupyter --property=MemoryCurrent'
```

### **Historical Data:**
```bash
# Memory usage over time
journalctl -u jupyter | grep -i memory

# Check if limits were hit
journalctl -u jupyter | grep -i "killed\|oom\|limit"
```

## Advanced: Custom Resource Monitoring Script

```bash
#!/bin/bash
# /home/jupyter/monitor_resources.sh

LOG_FILE="/var/log/jupyter-resources.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get current resource usage
    MEMORY=$(sudo systemctl show jupyter --property=MemoryCurrent --value)
    CPU_TIME=$(sudo systemctl show jupyter --property=CPUUsageNSec --value)
    TASKS=$(sudo systemctl show jupyter --property=TasksCurrent --value)
    
    # Convert memory to MB
    MEMORY_MB=$((MEMORY / 1024 / 1024))
    
    # Log if usage is high
    if [ $MEMORY_MB -gt 1500 ]; then
        echo "$TIMESTAMP: HIGH MEMORY USAGE: ${MEMORY_MB}MB" >> $LOG_FILE
        
        # Optional: Alert
        if [ $MEMORY_MB -gt 3000 ]; then
            echo "CRITICAL: Jupyter using ${MEMORY_MB}MB" | mail -s "Jupyter Alert" admin@company.com
        fi
    fi
    
    # Check task count
    if [ $TASKS -gt 100 ]; then
        echo "$TIMESTAMP: HIGH TASK COUNT: $TASKS" >> $LOG_FILE
    fi
    
    sleep 60  # Check every minute
done
```

Make it a service too:
```ini
# /etc/systemd/system/jupyter-monitor.service
[Unit]
Description=Jupyter Resource Monitor
After=jupyter.service
Requires=jupyter.service

[Service]
Type=simple
ExecStart=/home/jupyter/monitor_resources.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

## Kernel-Level Resource Controls

For even more control, use cgroups directly:

```bash
# Create custom cgroup for Jupyter
sudo mkdir -p /sys/fs/cgroup/memory/jupyter
sudo mkdir -p /sys/fs/cgroup/cpu/jupyter

# Set memory limit (2GB)
echo 2147483648 | sudo tee /sys/fs/cgroup/memory/jupyter/memory.limit_in_bytes

# Set CPU limit (50% of one core)
echo 50000 | sudo tee /sys/fs/cgroup/cpu/jupyter/cpu.cfs_quota_us
echo 100000 | sudo tee /sys/fs/cgroup/cpu/jupyter/cpu.cfs_period_us

# Move Jupyter process to cgroup
JUPYTER_PID=$(pgrep -f "jupyter lab")
echo $JUPYTER_PID | sudo tee /sys/fs/cgroup/memory/jupyter/cgroup.procs
echo $JUPYTER_PID | sudo tee /sys/fs/cgroup/cpu/jupyter/cgroup.procs
```

## Python-Level Resource Limits

You can also add Python-level limits in your Jupyter config:

```python
# /home/jupyter/.jupyter/jupyter_lab_config.py

import resource
import signal
import os

# Limit memory per process (2GB)
def limit_memory():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024*1024*1024, 2*1024*1024*1024))

# Limit CPU time per process (1 hour)
def limit_cpu_time():
    resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))

# Limit number of processes
def limit_processes():
    resource.setrlimit(resource.RLIMIT_NPROC, (100, 100))

# Apply limits when kernels start
c.KernelManager.kernel_cmd = ['python', '-c', 
    'import resource; '
    'resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024)); '
    'exec(open("/home/jupyter/venv/bin/ipython").read())'
]
```

## Emergency Controls

Set up emergency stops:

```bash
# Emergency kill script
#!/bin/bash
# /home/jupyter/emergency_stop.sh

echo "Emergency stop triggered!"
sudo systemctl stop jupyter
sudo pkill -f jupyter
sudo pkill -f ipython
echo "All Jupyter processes stopped"
```

## Testing Resource Limits

Create a test notebook to verify limits work:

```python
# Test memory limit
import numpy as np

try:
    # Try to allocate 5GB of memory
    big_array = np.zeros((5000, 1000, 1000), dtype=np.float64)
    print("ERROR: Should have been killed!")
except MemoryError:
    print("Good: Memory limit working")

# Test CPU limit  
import time
start = time.time()
while time.time() - start < 10:
    pass  # Busy loop
```

The key insight is that **resource control happens at multiple layers**:

1. **systemd service limits** (recommended approach)
2. **cgroups** (lower-level control)
3. **Python process limits** (per-kernel control)
4. **Monitoring scripts** (alerting and logging)

Think of it like **having multiple safety systems on an airplane** - if one fails, the others keep you safe!

