#!/usr/bin/python

import telnetlib
import sys
import getopt
import paramiko
import time
import socket

HELP = '''
usage: check_custom_env_cisco.py 
        -h, --help                              <help>
        -m, --mode              OPTIONAL        <mode=ssh|telnet>
        -H, --hostname          MANDATORY       <fqdn|ip>
        -P, --port              OPTIONAL        <port=22>
        -u, --username          OPTIONAL        <username>
        -p, --password          OPTIONAL        <password>
        -s, --service           MANDATORY       <service: fan|power|temperature>
        -a, --total-attempts    OPTIONAL        <total attempts=3>
'''
HOST = "" #mandatory ip or host
PORT = "22" #default ssh port
USERNAME = "" #default empty
PASSWORD = "" #default empty
MODE = "ssh" #default ssh mode
SERVICE = "" #mandatory service e.g fan|power|temperature
TOTAL_ATTEMPTS = 3
MAX_BUFFER = 65535

#Possible output associated to each service
poss_out = {
                "temperature": ["TEMPERATURE","SYSTEM TEMPERATURE"],
                "fan": ["FAN"],
                "power": ["POWER"],
        }

#Return values
ret_values = {
                "OK": 0,
                "WARNING": 1,
                "CRITICAL": 2,
                "UNKNOWN": 3 
}

'''
        Parse the output according to Icinga guide
        https://icinga.com/docs/icinga-2/latest/doc/05-service-monitoring/#output
        Print the output with the result of command and return the appropriate ret_values
'''
def parse_output(line):
        if "OK" in line:
                print("Result is: OK")
                sys.exit(ret_values["OK"])
        else:
                print("Result is: CRITICAL")
                sys.exit(ret_values["CRITICAL"])

        '''
        if "OK" in line:
                return ret_values["OK"] #return detto da frank
        #TODO: more cases
        else:
                return ret_values["CRITICAL"] 
        '''

'''
        Connect via telnet to the device and write command
'''
def connect_telnet(service):
        try_connection = True
        for attempt in range(TOTAL_ATTEMPTS):
                if try_connection:
                        time.sleep(0.8)
                        try:

                                tn = telnetlib.Telnet(HOST,PORT)
                                tn.read_until(b"Username: ")
                                tn.write(USERNAME.encode('ascii') + b"\r\n")
                                tn.read_until(b"Password: ")
                                tn.write(PASSWORD.encode('ascii') + b"\r\n")

                                tn.write(b"terminal length 0".encode("ascii") + b"\r\n")
                                tn.write(b"show env " + service + "\r\n")
                                tn.write(b"exit\r\n")
                                output = tn.read_all() #read all the output
                                for line in output.splitlines(): #for each line in the output...
                                        for value in poss_out[service]: #check if almost one of the possible value there is in the line...
                                                if value in line:
                                                        parse_output(line) #return string
                                try_connection = False
                                tn.close()
                        except socket.timeout:
                                print("Connection drop due to timeout")
                                sys.exit(108)
                        except Exception as e:
                                print(e)
                                sys.exit(106)

'''
        Retrieve all the data outputs from remote device. After call this method the buffer of received output is empty.
'''
def recv_all(connection):
        continue_recv = True
        output = ""
        while connection.recv_ready() and continue_recv:
                #recv() return a string representing the data received
                #if string length zero is returned, channel stream has closed
                return_string = connection.recv(MAX_BUFFER)
                if len(return_string) == 0:
                        #connection closed
                        continue_recv = False
                        return output
                else:
                        output += return_string
        return output


'''
        Connect via ssh to the device and write command
'''
def connect_ssh(service):
        try_connection = True
        connection = paramiko.SSHClient()
        # Load SSH host keys.
        #connection.load_system_host_keys()
        # Add SSH host key when missing.
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())


        for attempt in range(TOTAL_ATTEMPTS):
                if try_connection:
                        try:
                                #print("Attempt to connect: %d" % attempt)
                                # Connect to router using username/password authentication.
                                #print(HOST + " " + PORT + " " + USERNAME + " " + PASSWORD) #DEBUG
                                connection.connect(
                                                HOST,
                                                port=int(PORT),
                                                username=USERNAME,
                                                password=PASSWORD,
                                                allow_agent=False,
                                                look_for_keys=False )
                                # Run command.
                                '''for line in output.splitlines(): #for each line in the output...
                                        for value in poss_out[service]: #check if almost one of the possible value there is in the line...
                                if value in line:
                                        return line #return string
                                '''
                                shell = connection.invoke_shell()
                                recv_all(shell) #trash output
                                shell.send("terminal length 0\n")
                                time.sleep(0.5)
                                recv_all(shell) #trash output
                                command = "show env " + service + "\n"  
                                shell.send(command)
                                # Read output from command.
                                time.sleep(0.5) #!!!!!!!!!!! VERY IMPORTANT, OTHERWISE NOT WORK !!!!!!!!!!!!
                                output = recv_all(shell)
                                shell.send("exit\n")
                                recv_all(shell) #trash output
                                # Close connection.
                                shell.close()
                                try_connection = False
                                for line in output.splitlines(): #for each line in the output...
                                        for value in poss_out[service]: #check if almost one of the possible value there is in the line...
                                                if value in line:
                                                        parse_output(line) #parse output
                                if try_connection:
                                        time.sleep(0.8)
                        except socket.error:
                                print("Unable to connect using supplied IP address / port")
                                sys.exit(106)
                        except paramiko.AuthenticationException:
                                print("Authentication failed")
                                sys.exit(106)
                        except paramiko.SSHException:
                                print("Encounter error during connecting or establishing an SSH session")
                                sys.exit(106)
                        except Exception as e:
                                print(e)
                                traceback.print_exc()
                                sys.exit(106)


def parse_args(argv):
        global HOST 
        global PORT
        global USERNAME
        global PASSWORD
        global MODE
        global SERVICE
        global TOTAL_ATTEMPTS

        try:
                opts, args = getopt.getopt(
                                argv,
                                "h:m:H:P:p:u:s:a",
                                [       "help"
                                        "mode=",
                                        "hostname=",
                                        "port=",
                                        "password=",
                                        "username=",
                                        "service=",
                                        "total-attempts"

                                ]
                                )
        except getopt.GetoptError:
                print HELP
                sys.exit(100)

        if len(argv) < 2: #hostname & service mandatory 
                print HELP
                sys.exit(103)

        for opt, arg in opts:
                if opt in ("-h","--help"):
                        print HELP
                        sys.exit(101)
                if opt in ("-m", "--mode"):
                        if arg not in ("ssh","telnet"):
                                print("Possible value for mode: ssh | telnet")
                                sys.exit(104)
                        else:
                                MODE = arg
                                #print("mode " + arg)
                if opt in ("-H", "--hostname"):
                        HOST = arg
                        #print("hostname " + arg)
                if opt in ("-P", "--port"):
                        PORT = arg
                        #print("port " + arg)
                if opt in ("-u","--username"):
                        USERNAME = arg
                        #print("username " + arg)
                if opt in ("-p","--password"):
                        PASSWORD = arg
                        #print("password " + arg)
                if opt in ("-s","--service"):
                        if arg not in ("fan","power","temperature"):
                                print("Possible value for service: fan | power | temperature")
                                sys.exit(105)
                        else:
                                SERVICE = arg
                                #print("service " + arg)
                if opt in ("-a","--total-attempts"):
                        TOTAL_ATTEMPTS = arg
                        #print("total attempts " + arg)


if __name__ == "__main__":

        parse_args(sys.argv[1:])
        if MODE == "ssh":
                connect_ssh(SERVICE)
        elif MODE == "telnet":
                connect_telnet(SERVICE)
