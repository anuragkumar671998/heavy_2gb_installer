#!/usr/bin/env python3
"""
Heavy App Batch Installer - 2GB Batches
Automatically runs in background - installs/uninstalls heavy apps in 2GB batches
Batch size: Max 2GB, Apps: 500MB+ each, Delay: 7-16 minutes
"""

import subprocess
import random
import time
import sys
import os
import logging
import atexit
import signal
from datetime import datetime

# Global flag for graceful shutdown
shutdown_flag = False
pid_file = "/tmp/heavy_2gb_installer.pid"
log_file = "/tmp/heavy_2gb_installer.log"

# Heavy applications (500MB+ each) for Ubuntu 24.04 - verified package names
HEAVY_APPS = [
    # Development IDEs & Tools (Large)
    'code',                          # Visual Studio Code ~500MB
    'intellij-idea-community',      # IntelliJ IDEA ~800MB
    'pycharm-community',            # PyCharm ~700MB
    'eclipse',                      # Eclipse IDE ~600MB
    'qtcreator',                    # Qt Creator ~500MB
    'android-studio',               # Android Studio ~2GB
    
    # Graphics & 3D Software
    'blender',                      # Blender ~600MB
    'krita',                        # Krita ~500MB
    'gimp',                         # GIMP ~500MB
    'inkscape',                     # Inkscape ~500MB
    'freecad',                      # FreeCAD ~700MB
    'openscad',                     # OpenSCAD ~500MB
    
    # Video Editing & Production
    'kdenlive',                     # Kdenlive ~600MB
    'shotcut',                      # Shotcut ~500MB
    'openshot',                     # OpenShot ~600MB
    'olive-editor',                 # Olive Editor ~500MB
    
    # Audio Production
    'ardour',                       # Ardour ~600MB
    'lmms',                         # LMMS ~500MB
    'mixxx',                        # Mixxx ~500MB
    'audacity',                     # Audacity ~500MB
    
    # Office Suites
    'libreoffice',                  # LibreOffice ~700MB
    
    # Virtualization & Containers
    'virtualbox',                   # VirtualBox ~200MB
    'virtualbox-ext-pack',          # VirtualBox Extension Pack ~50MB
    'qemu-system',                  # QEMU system ~500MB
    'qemu-kvm',                     # QEMU KVM ~300MB
    'libvirt-daemon-system',        # Libvirt ~400MB
    'virt-manager',                 # Virt Manager ~300MB
    'docker.io',                    # Docker ~300MB
    'docker-compose',               # Docker Compose ~50MB
    'podman',                       # Podman ~400MB
    
    # Databases
    'mysql-server',                 # MySQL Server ~500MB
    'postgresql',                   # PostgreSQL ~600MB
    'mariadb-server',               # MariaDB Server ~500MB
    
    # Web Servers
    'apache2',                      # Apache2 ~500MB
    'nginx',                        # Nginx ~400MB
    'tomcat9',                      # Tomcat9 ~600MB
    
    # Cloud & Big Data
    'hadoop',                       # Hadoop ~800MB
    'elasticsearch',                # Elasticsearch ~600MB
    
    # Games
    'steam-installer',              # Steam ~500MB
    'lutris',                       # Lutris ~300MB
    'wine',                         # Wine ~600MB
    
    # Emulators
    'retroarch',                    # RetroArch ~500MB
    'dolphin-emu',                  # Dolphin Emulator ~300MB
    
    # Browsers
    'firefox',                      # Firefox ~400MB
    'google-chrome-stable',         # Google Chrome ~300MB
    'chromium-browser',             # Chromium ~400MB
    
    # Communication
    'discord',                      # Discord ~200MB
    'slack',                        # Slack ~300MB
    
    # CAD & Engineering
    'freecad',                      # FreeCAD ~700MB
    'librecad',                     # LibreCAD ~500MB
    
    # Science & Research
    'octave',                       # Octave ~500MB
    'maxima',                       # Maxima ~400MB
    'geogebra',                     # GeoGebra ~500MB
    
    # Media Players
    'vlc',                          # VLC ~400MB
    'mpv',                          # MPV ~300MB
    
    # Security
    'clamav',                       # ClamAV ~300MB
    'wireshark',                    # Wireshark ~400MB
    
    # Network Tools
    'nmap',                         # Nmap ~200MB
    
    # Package Managers
    'snapd',                        # Snapd ~100MB
    'flatpak',                      # Flatpak ~200MB
    
    # Additional Heavy Packages
    'openjdk-17-jdk',               # OpenJDK 17 ~500MB
    'openjdk-21-jdk',               # OpenJDK 21 ~500MB
    'gcc-12',                       # GCC 12 ~500MB
    'g++-12',                       # G++ 12 ~500MB
    'llvm-14',                      # LLVM 14 ~700MB
    'rustc',                        # Rust Compiler ~800MB
    'golang-go',                    # Go Language ~500MB
    'nodejs',                       # Node.js ~300MB
    'npm',                          # NPM ~200MB
    'python3',                      # Python3 ~100MB
    'python3-pip',                  # Python pip ~50MB
    'mono-complete',                # Mono ~600MB
    'dotnet-sdk-6.0',               # .NET SDK ~500MB
    'dotnet-sdk-7.0',               # .NET SDK 7 ~500MB
]

# App size estimates in MB (approximate - for batch planning)
APP_SIZE_ESTIMATES = {
    'code': 500,
    'intellij-idea-community': 800,
    'pycharm-community': 700,
    'eclipse': 600,
    'qtcreator': 500,
    'android-studio': 2000,
    'blender': 600,
    'krita': 500,
    'gimp': 500,
    'inkscape': 500,
    'freecad': 700,
    'openscad': 500,
    'kdenlive': 600,
    'shotcut': 500,
    'openshot': 600,
    'olive-editor': 500,
    'ardour': 600,
    'lmms': 500,
    'mixxx': 500,
    'audacity': 500,
    'libreoffice': 700,
    'virtualbox': 200,
    'virtualbox-ext-pack': 50,
    'qemu-system': 500,
    'qemu-kvm': 300,
    'libvirt-daemon-system': 400,
    'virt-manager': 300,
    'docker.io': 300,
    'docker-compose': 50,
    'podman': 400,
    'mysql-server': 500,
    'postgresql': 600,
    'mariadb-server': 500,
    'apache2': 500,
    'nginx': 400,
    'tomcat9': 600,
    'hadoop': 800,
    'elasticsearch': 600,
    'steam-installer': 500,
    'lutris': 300,
    'wine': 600,
    'retroarch': 500,
    'dolphin-emu': 300,
    'firefox': 400,
    'google-chrome-stable': 300,
    'chromium-browser': 400,
    'discord': 200,
    'slack': 300,
    'freecad': 700,
    'librecad': 500,
    'octave': 500,
    'maxima': 400,
    'geogebra': 500,
    'vlc': 400,
    'mpv': 300,
    'clamav': 300,
    'wireshark': 400,
    'nmap': 200,
    'snapd': 100,
    'flatpak': 200,
    'openjdk-17-jdk': 500,
    'openjdk-21-jdk': 500,
    'gcc-12': 500,
    'g++-12': 500,
    'llvm-14': 700,
    'rustc': 800,
    'golang-go': 500,
    'nodejs': 300,
    'npm': 200,
    'python3': 100,
    'python3-pip': 50,
    'mono-complete': 600,
    'dotnet-sdk-6.0': 500,
    'dotnet-sdk-7.0': 500,
}

def daemonize():
    """Turn the script into a daemon that runs in background"""
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"First fork failed: {e}\n")
        sys.exit(1)
    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Second fork failed: {e}\n")
        sys.exit(1)
    
    # Write PID file
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    # Register cleanup
    atexit.register(cleanup_pid_file)
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    shutdown_flag = True

def cleanup_pid_file():
    """Remove PID file on exit"""
    if os.path.exists(pid_file):
        os.remove(pid_file)

def check_existing_process():
    """Check if another instance is already running"""
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)
                return True, pid
            except OSError:
                os.remove(pid_file)
                return False, None
        except:
            os.remove(pid_file)
            return False, None
    return False, None

def setup_logging():
    """Setup logging for background process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
        ]
    )
    return logging.getLogger(__name__)

def check_disk_space():
    """Check available disk space in GB"""
    try:
        result = subprocess.run(
            ['df', '/', '--output=avail'],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            available_kb = int(lines[1].strip())
            available_gb = available_kb / (1024 * 1024)
            return available_gb
    except:
        pass
    return 0

def select_batch_2gb():
    """Select apps for a batch with 2GB total size limit"""
    selected_apps = []
    total_size_mb = 0
    max_size_mb = 2000  # 2GB limit
    
    # Shuffle apps to get random selection
    shuffled_apps = HEAVY_APPS.copy()
    random.shuffle(shuffled_apps)
    
    for app in shuffled_apps:
        if app in APP_SIZE_ESTIMATES:
            app_size = APP_SIZE_ESTIMATES[app]
            
            # Check if adding this app would exceed 2GB limit
            if total_size_mb + app_size <= max_size_mb:
                selected_apps.append(app)
                total_size_mb += app_size
                
                # Stop when we reach close to 2GB
                if total_size_mb >= 1500:  # At least 1.5GB
                    break
            else:
                # Try to find smaller apps if current one is too big
                continue
    
    # If we don't have enough apps, add more smaller ones
    if total_size_mb < 1000:  # Less than 1GB
        for app in shuffled_apps:
            if app not in selected_apps and app in APP_SIZE_ESTIMATES:
                app_size = APP_SIZE_ESTIMATES[app]
                if total_size_mb + app_size <= max_size_mb:
                    selected_apps.append(app)
                    total_size_mb += app_size
                    
                    if total_size_mb >= 1500:
                        break
    
    return selected_apps, total_size_mb

def check_package_exists(package_name):
    """Check if a package exists in the repositories"""
    try:
        result = subprocess.run(
            ['apt-cache', 'show', package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except:
        return False

def get_installed_apps_from_batch(apps_list):
    """Get list of apps from batch that are actually installed"""
    installed_apps = []
    for app in apps_list:
        try:
            result = subprocess.run(
                ['dpkg', '-l', app],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and 'ii' in result.stdout:
                installed_apps.append(app)
        except:
            continue
    return installed_apps

def install_app_individually(app, logger):
    """Install a single app individually"""
    try:
        logger.info(f"  Installing {app}...")
        result = subprocess.run(
            ['apt', 'install', '-y', app],
            timeout=600,  # 10 minutes per app
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"  ✓ Successfully installed {app}")
            return True
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            logger.warning(f"  ✗ Failed to install {app}: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning(f"  ✗ Timeout installing {app}")
        return False
    except Exception as e:
        logger.warning(f"  ✗ Error installing {app}: {e}")
        return False

def install_batch_2gb(apps_list, batch_num, total_size_mb, logger):
    """Install a 2GB batch of heavy apps"""
    logger.info(f"\n{'='*60}")
    logger.info(f"INSTALLING BATCH {batch_num}")
    logger.info(f"Apps: {len(apps_list)}")
    logger.info(f"Estimated size: {total_size_mb/1024:.1f}GB")
    logger.info(f"App list: {', '.join(apps_list)}")
    logger.info('='*60)
    
    # Check disk space before installation
    available_gb = check_disk_space()
    required_gb = (total_size_mb * 1.5) / 1024  # Need 1.5x for safety
    
    logger.info(f"Disk space check: {available_gb:.1f}GB available, {required_gb:.1f}GB required")
    
    if available_gb < required_gb:
        logger.error(f"✗ Insufficient disk space. Need {required_gb:.1f}GB, have {available_gb:.1f}GB")
        return False, []
    
    # Validate packages exist
    valid_apps = []
    for app in apps_list:
        if check_package_exists(app):
            valid_apps.append(app)
        else:
            logger.warning(f"✗ Package not available: {app}")
    
    if not valid_apps:
        logger.error("✗ No valid packages to install")
        return False, []
    
    logger.info(f"Valid packages: {len(valid_apps)}/{len(apps_list)}")
    
    # Install apps individually for better tracking
    installed_apps = []
    success_count = 0
    
    for app in valid_apps:
        if install_app_individually(app, logger):
            success_count += 1
            installed_apps.append(app)
        
        # Small delay between individual installs
        time.sleep(5)
    
    logger.info(f"\nInstallation summary for batch {batch_num}:")
    logger.info(f"Successfully installed: {success_count}/{len(valid_apps)} apps")
    
    if success_count > 0:
        logger.info(f"✓ Batch {batch_num} installation completed")
        return True, installed_apps
    else:
        logger.error(f"✗ Batch {batch_num} installation failed")
        return False, []

def uninstall_app_individually(app, logger):
    """Uninstall a single app individually"""
    try:
        logger.info(f"  Uninstalling {app}...")
        
        # First check if app is installed
        check_result = subprocess.run(
            ['dpkg', '-l', app],
            capture_output=True,
            text=True
        )
        
        if check_result.returncode != 0 or 'ii' not in check_result.stdout:
            logger.info(f"  ⚠ {app} is not installed")
            return True
        
        # Remove with purge to clean everything
        result = subprocess.run(
            ['apt', 'remove', '-y', '--purge', app],
            timeout=300,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"  ✓ Successfully uninstalled {app}")
            return True
        else:
            logger.warning(f"  ✗ Failed to uninstall {app}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning(f"  ✗ Timeout uninstalling {app}")
        return False
    except Exception as e:
        logger.warning(f"  ✗ Error uninstalling {app}: {e}")
        return False

def uninstall_batch_completely(apps_list, batch_num, logger):
    """Completely uninstall all apps from batch"""
    logger.info(f"\n{'='*60}")
    logger.info(f"UNINSTALLING BATCH {batch_num}")
    logger.info(f"Apps to uninstall: {len(apps_list)}")
    logger.info(f"App list: {', '.join(apps_list)}")
    logger.info('='*60)
    
    success_count = 0
    
    for app in apps_list:
        if uninstall_app_individually(app, logger):
            success_count += 1
        
        # Small delay between uninstalls
        time.sleep(3)
    
    logger.info(f"\nUninstallation summary for batch {batch_num}:")
    logger.info(f"Successfully uninstalled: {success_count}/{len(apps_list)} apps")
    
    if success_count > 0:
        logger.info(f"✓ Batch {batch_num} uninstallation completed")
        return True
    else:
        logger.warning(f"⚠ Batch {batch_num} uninstallation had issues")
        return False

def cleanup_system(logger):
    """Clean up system after operations"""
    logger.info("\nPerforming system cleanup...")
    
    try:
        # Remove unnecessary packages
        subprocess.run(
            ['apt', 'autoremove', '-y'],
            timeout=300,
            capture_output=True
        )
        
        # Clean package cache
        subprocess.run(
            ['apt', 'autoclean'],
            timeout=180,
            capture_output=True
        )
        
        # Clean downloaded package files
        subprocess.run(
            ['apt', 'clean'],
            timeout=180,
            capture_output=True
        )
        
        # Clean temporary files
        subprocess.run(
            ['rm', '-rf', '/tmp/*', '/var/tmp/*'],
            capture_output=True
        )
        
        logger.info("✓ System cleanup completed")
        
        # Show disk space after cleanup
        available_gb = check_disk_space()
        logger.info(f"Available disk space: {available_gb:.1f}GB")
        
    except Exception as e:
        logger.warning(f"⚠ Cleanup had issues: {e}")

def main_installation():
    """Main installation process - runs in background"""
    global shutdown_flag
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("="*70)
    logger.info("HEAVY APP 2GB BATCH INSTALLER STARTED")
    logger.info(f"Start time: {datetime.now()}")
    logger.info("="*70)
    
    # Check initial disk space
    initial_disk = check_disk_space()
    logger.info(f"Initial disk space: {initial_disk:.1f}GB")
    
    if initial_disk < 15:
        logger.warning(f"⚠ Low disk space warning: {initial_disk:.1f}GB available")
        logger.warning("Recommended: At least 20GB free space")
    
    # Update system first
    logger.info("Updating package lists...")
    subprocess.run(['apt', 'update'], capture_output=True, timeout=300)
    
    # Process apps in 2GB batches
    batch_number = 0
    total_batches_processed = 0
    total_apps_installed = 0
    
    while not shutdown_flag:
        batch_number += 1
        
        # Check for shutdown
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            break
        
        # Select batch with 2GB limit
        batch_apps, batch_size_mb = select_batch_2gb()
        
        if not batch_apps:
            logger.warning("No apps available for batch selection")
            break
        
        logger.info(f"\n{'#'*70}")
        logger.info(f"PROCESSING BATCH {batch_number}")
        logger.info(f"Selected {len(batch_apps)} apps, estimated {batch_size_mb/1024:.1f}GB")
        logger.info(f"Total batches processed: {total_batches_processed}")
        logger.info(f"Total apps installed/uninstalled: {total_apps_installed}")
        logger.info('#'*70)
        
        # Check disk space
        current_disk = check_disk_space()
        logger.info(f"Current disk space: {current_disk:.1f}GB")
        
        if current_disk < 5:
            logger.error("✗ Critical: Less than 5GB disk space available")
            logger.info("Performing emergency cleanup...")
            cleanup_system(logger)
            current_disk = check_disk_space()
            
            if current_disk < 5:
                logger.error("✗ Insufficient disk space even after cleanup. Stopping.")
                break
        
        # Install the batch
        install_success, installed_apps = install_batch_2gb(
            batch_apps, batch_number, batch_size_mb, logger
        )
        
        if not install_success:
            logger.warning(f"⚠ Batch {batch_number} installation failed, skipping to next batch")
            time.sleep(60)
            continue
        
        total_apps_installed += len(installed_apps)
        
        # Check for shutdown before delay
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            # Uninstall what we just installed before exiting
            if installed_apps:
                logger.info("Uninstalling current batch before exit...")
                uninstall_batch_completely(installed_apps, batch_number, logger)
            break
        
        # Random delay between 7-16 minutes before uninstall
        delay_minutes = random.randint(7, 16)
        delay_seconds = delay_minutes * 60
        logger.info(f"\nWaiting {delay_minutes} minutes before uninstalling...")
        
        # Break delay into smaller chunks to check shutdown flag
        chunk_size = 30
        for i in range(0, delay_seconds, chunk_size):
            if shutdown_flag:
                break
            time.sleep(min(chunk_size, delay_seconds - i))
        
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            if installed_apps:
                logger.info("Uninstalling current batch before exit...")
                uninstall_batch_completely(installed_apps, batch_number, logger)
            break
        
        # UNINSTALL THE BATCH
        if installed_apps:
            uninstall_success = uninstall_batch_completely(
                installed_apps, batch_number, logger
            )
            
            if not uninstall_success:
                logger.warning(f"⚠ Batch {batch_number} uninstallation had issues")
        
        total_batches_processed += 1
        
        # Random delay before next batch (3-7 minutes)
        if not shutdown_flag:
            next_delay_minutes = random.randint(3, 7)
            next_delay_seconds = next_delay_minutes * 60
            logger.info(f"\nWaiting {next_delay_minutes} minutes before next batch...")
            
            for i in range(0, next_delay_seconds, chunk_size):
                if shutdown_flag:
                    break
                time.sleep(min(chunk_size, next_delay_seconds - i))
        
        # Perform cleanup every 2 batches
        if batch_number % 2 == 0 and not shutdown_flag:
            cleanup_system(logger)
        
        # Optional: Stop after certain number of batches
        if batch_number >= 50:  # Process up to 50 batches
            logger.info("Reached maximum batch limit (50)")
            break
    
    # Final cleanup and summary
    logger.info("\n" + "="*70)
    if shutdown_flag:
        logger.info("PROCESS STOPPED BY USER")
    else:
        logger.info("PROCESS COMPLETED")
    
    logger.info(f"Total batches processed: {total_batches_processed}")
    logger.info(f"Total apps installed/uninstalled: {total_apps_installed}")
    logger.info(f"Total batch cycles: {batch_number}")
    
    # Final cleanup
    cleanup_system(logger)
    
    # Final disk space report
    final_disk = check_disk_space()
    logger.info(f"Final disk space: {final_disk:.1f}GB")
    logger.info(f"Disk space change: {final_disk - initial_disk:+.1f}GB")
    
    logger.info(f"End time: {datetime.now()}")
    logger.info("="*70)
    
    if shutdown_flag:
        logger.info("Process stopped gracefully")
    else:
        logger.info("Heavy app 2GB batch process completed successfully!")

def show_status():
    """Show current status if running"""
    is_running, pid = check_existing_process()
    
    if is_running:
        print(f"✓ Heavy 2GB Batch Installer is RUNNING (PID: {pid})")
    else:
        print("✗ Heavy 2GB Batch Installer is NOT running")
    
    print(f"\nLog file: {log_file}")
    
    if os.path.exists(log_file):
        print("\nLast 20 lines of log:")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-20:]
                for line in lines:
                    print(line.strip())
        except Exception as e:
            print(f"Could not read log file: {e}")
        
        # Show disk space
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True
            )
            print(f"\nDisk space:")
            print(result.stdout.strip())
        except:
            pass
    else:
        print("\nLog file does not exist yet")

def stop_process():
    """Stop the running background process"""
    is_running, pid = check_existing_process()
    
    if not is_running:
        print("No background process is running")
        return
    
    try:
        # Send SIGTERM signal for graceful shutdown
        os.kill(pid, signal.SIGTERM)
        print(f"✓ Sent stop signal to process {pid}")
        print("Process will complete current batch and exit gracefully...")
        
        # Wait for process to terminate
        for i in range(15):
            try:
                os.kill(pid, 0)
                if i % 5 == 0:
                    print(f"Waiting for graceful shutdown... ({i+1}/15 seconds)")
                time.sleep(1)
            except OSError:
                print("✓ Process stopped successfully")
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                return
        
        # If still running after graceful wait, force kill
        print("Process not responding to graceful shutdown, forcing termination...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(2)
        
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("✓ Process terminated")
        
    except Exception as e:
        print(f"✗ Error stopping process: {e}")

def show_summary():
    """Show summary of what will happen"""
    print("\n" + "="*70)
    print("HEAVY APP 2GB BATCH INSTALLER - UBUNTU 24.04")
    print("="*70)
    print("This script will run in the background and:")
    print("1. Install heavy applications (500MB+ each)")
    print("2. Process apps in 2GB batches (max per batch)")
    print("3. For each batch:")
    print("   - Install heavy apps (2GB total)")
    print("   - Wait 7-16 minutes")
    print("   - UNINSTALL ALL APPS FROM THE BATCH")
    print("4. Continue processing batches")
    print("\nKEY FEATURES:")
    print("• 2GB per batch limit")
    print("• Individual app installation tracking")
    print("• Complete uninstallation after each batch")
    print("• Disk space monitoring")
    print("• Automatic cleanup")
    print("\nWARNINGS:")
    print("• Requires 15GB+ free disk space")
    print("• Uses high bandwidth for downloads")
    print("• Each batch takes 20-40 minutes")
    print("• System may be slow during installations")
    print(f"\nLog file: {log_file}")
    print(f"PID file: {pid_file}")
    print("="*70)
    print("\nCommands:")
    print(f"  Start:   sudo {sys.argv[0]} start")
    print(f"  Status:  {sys.argv[0]} status")
    print(f"  Stop:    {sys.argv[0]} stop")
    print(f"  Help:    {sys.argv[0]} help")
    print("="*70 + "\n")

def show_banner():
    """Show application banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         HEAVY APP 2GB BATCH INSTALLER - UBUNTU 24.04                 ║
║        2GB Batches • Individual Tracking • Complete Cleanup          ║
╚══════════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    # Show banner
    show_banner()
    
    # Check arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            # Check if already running
            is_running, pid = check_existing_process()
            if is_running:
                print(f"✗ Another instance is already running (PID: {pid})")
                print(f"Check log: tail -f {log_file}")
                print(f"Stop first: {sys.argv[0]} stop")
                sys.exit(1)
            
            # Show summary
            show_summary()
            
            # Check if running as root
            if os.geteuid() != 0:
                print("✗ This script requires sudo privileges!")
                print(f"Please run: sudo {sys.argv[0]} start")
                sys.exit(1)
            
            # Check disk space
            try:
                result = subprocess.run(
                    ['df', '-h', '/'],
                    capture_output=True,
                    text=True
                )
                print("\nCurrent disk space:")
                print(result.stdout.strip())
                print()
            except:
                pass
            
            # Confirm with warning
            print("WARNING: This will install and uninstall heavy applications.")
            print("It requires significant disk space and bandwidth.")
            response = input("\nStart Heavy 2GB Batch Installer in background? (yes/NO): ").strip().lower()
            if response != 'yes':
                print("Cancelled.")
                sys.exit(0)
            
            print("\n" + "="*70)
            print("STARTING HEAVY 2GB BATCH INSTALLER")
            print("="*70)
            print(f"✓ Check status:  {sys.argv[0]} status")
            print(f"✓ Stop anytime:  {sys.argv[0]} stop")
            print(f"✓ Watch logs:    tail -f {log_file}")
            print(f"✓ PID file:      {pid_file}")
            print("\nThe process will run in background.")
            print("You can close this terminal safely.")
            print("="*70)
            
            # Small delay before starting
            time.sleep(3)
            
            # Daemonize and start installation
            daemonize()
            main_installation()
            
        elif command == "stop":
            print("Stopping Heavy 2GB Batch Installer...")
            stop_process()
            
        elif command == "status":
            show_status()
            
        elif command in ["help", "--help", "-h"]:
            show_summary()
            
        else:
            print(f"✗ Unknown command: {command}")
            print(f"Usage: {sys.argv[0]} [start|stop|status|help]")
            sys.exit(1)
            
    else:
        # No arguments - show help
        show_summary()
