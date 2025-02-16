import paramiko
from secrets import SECRETS
from time import sleep

class PcController:
    def __init__(self):
        self.hostname = SECRETS['HOSTNAME']
        self.port = 22
        self.username = SECRETS['USERNAME']
        self.key_file_name = SECRETS['KEY_FILE_PATH']
        self.client = None
    
    def check_connection_is_active(self):
       # use the code below if is_active() returns True
        if self.client == None:
            return False
        try:
            self.client.exec_command('ps', timeout=5)
            return True
        except Exception as e:
            # connection is closed
            print("command could not be send")
            return False
    def ensure_connection(self):
        print("Ensuring SSH Connection")
        if not self.check_connection_is_active():
            print("No Connection alive. Starting Up connection now")
            try:
                # Create a new SSH client
                self.client = paramiko.SSHClient()
                # Automatically add untrusted hosts
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # Connect to the server
                self.client.connect(
                    hostname=self.hostname, 
                    port=self.port, 
                    username=self.username, 
                    key_filename=self.key_file_name, 
                    timeout=5
                )

                print("Connection succesfull")
                return "Connection succesfull"
            except Exception as e:
                print(str(e))
                return "Connection Error"

        print("Connection already found")
        return "Connection already available"
    
    def start_plex(self):
        print("Starting Plex")
        return self.execute_ssh_command("START-SCHEDULEDTASK -TaskName 'StartPlex'")
        
    def check_plex(self):
        print("Checking if Plex is running")
        result, error = self.execute_ssh_command("ps | select-string 'plex media server'")
        if error == "Connection Error":
           return "Error Connecting with SSH"
        elif len(result) > 0:
           return "Plex Media Server is running"
        else:
           return "Plex Media Server is NOT running"
   
    def restart_plex(self):
        print("Restarting Plex")
        print("...Stopping Plex")
        self.execute_ssh_command("Stop-Process -Name 'Plex Media Server' -F")
        print("...Sleeping")
        sleep(5)
        print("...Starting Plex")
        return self.start_plex()
    
    def start_fortnite(self):
        return self.execute_ssh_command("START-SCHEDULEDTASK -TaskName 'EpicGames'")
    
    #def check_update_fortnite():
    
    def stop_fortnite(self):
        return self.execute_ssh_command("Stop-Process -Name 'EpicGamesLauncher' -F")      
    
    def sleep_pc(self):
        print("Setting Sleep State PC")
        return self.execute_ssh_command("RUNDLL32.exe powrprof.dll, SetSuspendState Sleep")
        #self.client.close() ## todo: check of dit niet gewoon error geeft na slapen
    
    def execute_ssh_command(self,command):
        connection_result = self.ensure_connection()
        if (connection_result != "Connection Error"):
            try:
                # Execute the command
                stdin, stdout, stderr = self.client.exec_command(command)
                
                # Read the output and error
                output = stdout.read().decode()
                error = stderr.read().decode()
                
                if output != "":
                    print(output)
                if (error != ""):
                    print(error)
                return output, error
            except Exception as e:
                print(str(e))
                #return None, str(e)
        else:
            return None, connection_result
