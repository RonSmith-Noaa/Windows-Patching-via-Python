import paramiko
from gssapi import Name, Credentials
import csv

def get_kerberos_ticket(hostname):
    try:
        # Obtain Kerberos credentials
        name = Name("host@" + hostname)
        creds = Credentials(usage='initiate', name=name)
        return creds
    except Exception as e:
        print(f"Error obtaining Kerberos ticket for {hostname}: {e}")
        return None


def connect_with_kerberos(hostname, kerberos_creds):
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect with Kerberos authentication
        client.connect(hostname, gss_auth=True, gss_kex=True, gss_deleg_creds=True, gss_host=hostname,
                       gss_trust_dns=True, gss_creds=kerberos_creds)

        # Execute PowerShell remoting command to enter PSSession
        powershell_command = "Enter-PSSession"
        stdin, stdout, stderr = client.exec_command("powershell.exe -Command \"" + powershell_command + "\"")

        # Optionally, you can read the stdout and stderr streams for feedback
        for line in stdout:
            print(line.strip())
        for line in stderr:
            print(line.strip())

        return client
    except Exception as e:
        print(f"Error connecting to {hostname} with Kerberos authentication: {e}")
        return None


def read_systems_from_csv(csv_file):
    systems = []
    try:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                systems.extend(row)
        return systems
    except Exception as e:
        print(f"Error reading systems from CSV file: {e}")
        return systems


def connect_to_system(hostname, kerberos_client, KBs):
    try:
        # Execute SSH commands
        if kerberos_client:
            print(f"Connecting to {hostname}...")

            # Check and install PSWindowsUpdate module
            check_and_install_pswindowsupdate(kerberos_client)

            # Install KBs
            for kb in KBs:
                install_kb_with_pswindowsupdate(kerberos_client, kb)

            return kerberos_client
        else:
            print("Kerberos authentication failed. Unable to connect to the system.")
            return None
    except Exception as e:
        print(f"Error connecting to {hostname}: {e}")
        return None


def check_and_install_pswindowsupdate(client):
    try:
        # Check if PSWindowsUpdate module is installed
        stdin, stdout, stderr = client.exec_command("Get-Module -Name PSWindowsUpdate -ListAvailable")
        module_info = stdout.read().decode('utf-8')

        if "PSWindowsUpdate" in module_info:
            print("PSWindowsUpdate module is already installed.")
        else:
            # Install PSWindowsUpdate module
            print("Installing PSWindowsUpdate module...")
            stdin, stdout, stderr = client.exec_command("Install-Module -Name PSWindowsUpdate -Force -Confirm:$false -Scope AllUsers")
            print(stdout.read().decode('utf-8'))
            print(stderr.read().decode('utf-8'))
    except Exception as e:
        print(f"Error checking/installing PSWindowsUpdate module: {e}")


def install_kb_with_pswindowsupdate(client, kb):
    try:
        # Install KB using PSWindowsUpdate module
        command = f"Install-WindowsUpdate -KBArticleID {kb} -AcceptAll -AutoReboot"
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if output:
            print(f"KB {kb} installed successfully.")
        elif error:
            print(f"Error installing KB {kb}: {error}")
        else:
            print(f"Installation of KB {kb} completed.")
    except Exception as e:
        print(f"Error installing KB {kb}: {e}")

        # Attempt to rename SoftwareDistribution folder
        try:
            print("Renaming SoftwareDistribution folder...")
            client.exec_command("Rename-Item -Path C:\\Windows\\SoftwareDistribution -NewName SoftwareDistribution.old -Force")
        except Exception as e:
            print(f"Error renaming SoftwareDistribution folder: {e}")

        # Attempt to download and install latest Windows Store components
        try:
            print("Downloading and installing latest Windows Store components...")
            client.exec_command("Start-Process -FilePath 'wsreset.exe' -Wait")
        except Exception as e:
            print(f"Error downloading and installing Windows Store components: {e}")


def test_kerberos_connection(hostname):
    try:
        # Get Kerberos ticket
        kerberos_creds = get_kerberos_ticket(hostname)
        if kerberos_creds:
            print("Kerberos ticket obtained successfully.")
        else:
            print("Failed to obtain Kerberos ticket.")
            return

        # Connect with Kerberos
        client = connect_with_kerberos(hostname, kerberos_creds)
        if client:
            print("Successfully connected to the system with Kerberos authentication.")
        else:
            print("Failed to connect to the system with Kerberos authentication.")
            return

        # Check for PSWindowsUpdate module
        check_and_install_pswindowsupdate(client)
    except Exception as e:
        print(f"Error testing Kerberos connection: {e}")


# csv_file = # Set the path to csv file that is the list of hosts you need to update
# List all the KB's you want to install on the hosts
# KBs = []

test_kerberos_connection("edith.pmel.noaa.gov")