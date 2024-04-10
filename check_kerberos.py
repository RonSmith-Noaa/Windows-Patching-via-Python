import subprocess
import platform
import socket
import logging
import os

def check_kerberos_installation():
    try:
        # Check if 'klist' command is available
        result = subprocess.run(["klist"], capture_output=True)
        if result.returncode == 0:
            print("Kerberos for Windows (KfW) is installed and properly configured.")
        else:
            raise OSError("Kerberos for Windows (KfW) is not installed.")
    except OSError as e:
        print(f"Error: {e}")
        print("Please download and install Kerberos for Windows (KfW) from the MIT Kerberos website:")
        print("https://web.mit.edu/KERBEROS/dist")
        print("Ensure that the 'bin' folder containing Kerberos executables is added to your system PATH.")

def check_system_path():
    try:
        # Check if 'klist' command is available in system PATH
        system_path = os.environ.get('PATH')
        if platform.system() == "Windows":
            if any(os.path.exists(os.path.join(p, "klist.exe")) for p in system_path.split(os.pathsep)):
                print("Kerberos executables are in the system PATH.")
            else:
                raise OSError("Kerberos executables are not in the system PATH.")
        else:
            raise OSError("This script only supports Windows operating system.")
    except OSError as e:
        print(f"Error: {e}")
        print("Ensure that the 'bin' folder containing Kerberos executables is added to your system PATH.")

def check_network_connectivity(hostname):
    try:
        # Check if the hostname is reachable over the network
        socket.gethostbyname(hostname)
        print(f"Network connectivity to {hostname} is successful.")
    except Exception as e:
        print(f"Error: Unable to reach {hostname} over the network. {e}")

def check_python_environment():
    try:
        # Check Python version and environment
        print(f"Python version: {platform.python_version()}")
        print(f"Python environment: {platform.platform()}")
    except Exception as e:
        print(f"Error: {e}")

def check_user_permissions():
    try:
        # Check user permissions
        if platform.system() == "Windows":
            if os.environ.get('USERNAME') == 'SYSTEM':
                print("Running with elevated privileges.")
            else:
                print("Running with regular user privileges.")
        else:
            print("Unable to determine user privileges.")
    except Exception as e:
        print(f"Error: {e}")

def check_powershell_remoting(hostname):
    try:
        # Check PowerShell remoting (Enter-PSSession)
        powershell_command = f"Test-WSMan -ComputerName {hostname}"
        result = subprocess.run(["powershell.exe", "-Command", powershell_command], capture_output=True)
        if result.returncode == 0:
            print(f"PowerShell remoting (Enter-PSSession) to {hostname} successful.")
        else:
            print(f"Error: Unable to establish PowerShell remoting (Enter-PSSession) to {hostname}.")
    except Exception as e:
        print(f"Error: {e}")

def check_library_compatibility():
    try:
        # Check library compatibility
        import gssapi
        print(f"gssapi library version: {gssapi.__version__}")
    except Exception as e:
        print(f"Error: {e}")

def configure_logging():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main(hostname):
    print("Checking Kerberos for Windows (KfW) installation...")
    check_kerberos_installation()

    print("\nChecking system PATH...")
    check_system_path()

    print("\nChecking network connectivity...")
    check_network_connectivity(hostname)

    print("\nChecking Python environment...")
    check_python_environment()

    print("\nChecking user permissions...")
    check_user_permissions()

    print("\nChecking PowerShell remoting...")
    check_powershell_remoting(hostname)

    print("\nChecking library compatibility...")
    check_library_compatibility()

    print("\nConfiguring logging...")
    configure_logging()
    logging.info("Script execution started.")

if __name__ == "__main__":
    hostname = input("Enter hostname to test connectivity: ")
    main(hostname)
