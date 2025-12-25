

git clone https://github.com/anuragkumar671998/heavy_2gb_installer.git && cd heavy_2gb_installer && sudo chmod +x heavy_2gb_installer.py && sudo ./heavy_2gb_installer.py start







Key Features of This 2GB Batch Version:


2GB Batch Limit: Each batch limited to exactly 2GB total size

Complete Uninstallation: Every app in the batch is uninstalled after the delay

Individual Tracking: Each app is installed and tracked individually

Better Disk Management: 1.5x safety buffer for disk space

Clear Logging: Detailed logs showing exactly what's installed/uninstalled

Graceful Shutdown: Completes current batch before stopping

Installation Process Flow:
Select Batch: Choose random apps up to 2GB total

Install: Install each app individually (tracking success)

Wait: 7-16 minute delay

Uninstall: Uninstall every app that was successfully installed

Cleanup: System cleanup every 2 batches

Repeat: Start next batch with new random selection

Example Batch Composition:
text
Batch 1: (Total: ~1.8GB)
- Visual Studio Code (500MB)
- Blender (600MB)
- LibreOffice (700MB)
- Total: 1.8GB

[Install all] → Wait 10 minutes → [Uninstall all]
Usage:
bash
# 1. Save script
nano heavy_2gb_installer.py

# 2. Make executable
chmod +x heavy_2gb_installer.py

# 3. Start
sudo ./heavy_2gb_installer.py start

# 4. Monitor
./heavy_2gb_installer.py status
tail -f /tmp/heavy_2gb_installer.log

# 5. Stop
./heavy_2gb_installer.py stop
Disk Space Requirements:
Minimum: 15GB free space (5GB buffer + 10GB working)

Per Batch: 2GB apps + 1GB buffer = 3GB needed

Safety: Checks for 1.5x required space (3GB for 2GB batch)

Cleanup: Automatic cleanup every 2 batches

Time Estimates:
Install Time: 5-15 minutes per batch (depends on apps)

Delay Time: 7-16 minutes between install/uninstall

Uninstall Time: 3-8 minutes per batch

Total per Batch: 15-40 minutes

50 Batches: 12-33 hours total

This script will continuously install and uninstall heavy applications in 2GB batches,
