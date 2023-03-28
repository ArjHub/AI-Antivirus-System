# Arjun

def print_error(e):
    print("[ERROR] : ", end='')
    print(e)
    print("[LOG] : Waiting 10 seconds and trying again")
    time.sleep(10)

import virtualbox
import time 

vbox = virtualbox.VirtualBox()
session = virtualbox.Session()
'''
machine = vbox.find_machine("REMnux")

snapshot = machine.find_snapshot("ForTest")

try:
    machine.create_session(session=session)

    restoring = machine.restore_snapshot(snapshot)
    while restoring.operation_percent < 100:
        time.sleep(0.5)

    session.unlock_machine()
except Exception as e:
    print(e)
'''

progress = machine.launch_vm_process(session, "gui", [])
progress.wait_for_completion(-1)

# Execute a command in the guest OS
command = "/bin/ls"
while True:
    try:
        guest_session = session.console.guest.create_session("remnux", "malware")
        process, stdout, stderr = guest_session.execute(command)

        # Print the command output
        print(str(stdout, 'UTF-8'))
        break

    except Exception as e:
        print_error(e)


# Sending file from HOST to GUEST (Input)
host_path = "D:\\VIT\\Year3Sem2\\J_AI_Antivirus\\Code\\test.txt"
guest_path = "/home/remnux/Shared/test.txt"
while True:
    try:
        progess = guest_session.file_copy_to_guest(host_path, guest_path, [])
        progress.wait_for_completion(-1)

        if progress.result_code == 0:
            print("Copy successful from " + host_path + " to " + guest_path)
            break

    except Exception as e:
        print_error(e)

time.sleep(2)

# Sending file from GUEST to HOST (Output)
host_path = "D:\\VIT\\Year3Sem2\\J_AI_Antivirus\\Code\\test2.txt"
guest_path = "/home/remnux/Shared/test.txt"
while True:
    try:
        progess = guest_session.file_copy_from_guest(guest_path, host_path, [])
        progress.wait_for_completion(-1)

        if progress.result_code == 0:
            print("Copy successful from " + guest_path + " to " + host_path)
            break

    except Exception as e:
        print_error(e)

time.sleep(2)

# Power off the virtual machine
session.console.power_down()

time.sleep(2)