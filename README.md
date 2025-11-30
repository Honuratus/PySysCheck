PySysCheck

A lightweight, dependency-free Linux system profiler. It probes hardware details by parsing kernel interfaces (/proc, /sys) and executing low-level system commands, without relying on heavy abstraction libraries like psutil.

Designed with SOLID principles in mind, featuring a modular architecture.

Features

Zero Dependencies: Runs on standard Python 3 libraries (os, subprocess, json, decimal). No pip install required.

Storage Probing: Detects SSD/HDD types via rotational checks and calculates exact capacity from sector counts.

CPU Topology: Extracts physical vs. logical core counts and virtualization support (SVM/VMX) from /proc/cpuinfo.

Hotplug Detection: Analyzes Kernel Ring Buffer (dmesg) for recent USB attach/detach events.

Hybrid Graphics: Detects multiple GPUs (e.g., Integrated + Discrete) via lspci parsing.

JSON Output: Exports strictly typed data for easy integration.

Installation & Usage

Just clone and run. Since it interacts with kernel logs (dmesg) and hardware interfaces, root privileges are recommended for full detail.

git clone [https://github.com/Honuratus/PySysCheck.git](https://github.com/Honuratus/PySysCheck.git)
cd PySysCheck

# Run full system probe
sudo python3 pysyscheck.py

# Run specific probe with verbose output (no file save)
sudo python3 pysyscheck.py --check cpu --verbose --no-file


CLI Arguments

Argument

Description

--check, -c

Specific hardware to probe: cpu, memory, disk, network, usb, gpu, os (Default: all)

--output, -o

Custom output filename (Default: report_YYYYMMDD_HHMMSS.json)

--no-file

Print to console only, do not save JSON file.

--verbose, -v

Print output to console even if saving to file.

Architecture

The project follows a Manager-Worker pattern to ensure separation of concerns:

src/probes/: Contains isolated classes for each hardware component (e.g., CpuProbe, DiskProbe). Each probe implements a common interface.

pysyscheck.py: Acts as the orchestrator, handling CLI arguments and delegating tasks to specific probes.

src/core/utils.py: Shared utilities for safe file reading and subprocess execution.

Sample Output

{
    "device_info": {
        "cpu": {
            "model_name": "AMD Ryzen 5 6600H",
            "topology": { "physical_cores": 6, "logical_threads": 12 },
            "virtualization_support": true
        },
        "disk": {
            "nvme0n1": {
                "model": "HFS512GEJ9X125N",
                "type": "SSD",
                "size": "476.94 GB"
            }
        },
        "hotplug_analysis": {
            "status": "Active",
            "recent_events": [
                "[11470.74] usb 3-2: new full-speed USB device number 4..."
            ]
        }
    },
    "test_results": {
        "usb_subsystem_active": "PASS",
        "ssd_present": "PASS"
    }
}


Why this project?

I built PySysCheck to demonstrate a deep understanding of Linux system internals (procfs, sysfs) and defensive programming. Instead of using ready-made libraries, I wanted to handle raw system data, parsing logic, and error handling manually.


