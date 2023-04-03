# Arjun VK
import virtualbox
import time 

def print_error(e):
    print("[ERROR] : ", end='')
    print(e)
    print("[LOG] : Waiting 10 seconds and trying again")
    time.sleep(10)

# Function to
#   1. Take input file path
#   2. Copy the file to the VM
#   3. Extract info 
#   4. Copy the extracted info out of VM

def extractLogsFromVirtualBox(machine_name, username, password, input_file_path, output_main_path):

    # Opening the VM
    vbox = virtualbox.VirtualBox()
    session = virtualbox.Session()

    machine = vbox.find_machine(machine_name)

    # Snapshot not working --> Function not defined
    '''
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
            guest_session = session.console.guest.create_session(username, password)
            process, stdout, stderr = guest_session.execute(command)
            
            # Print the command output
            print(str(stdout, 'UTF-8'))
            break

        except Exception as e:
            print_error(e)

    # 2. Sending file (malware file) from HOST to GUEST VM
    guest_main_path = "/home/remnux/Shared/"
    guest_file_path = guest_main_path + "malware.exe"

    while True:
        try:
            progess = guest_session.file_copy_to_guest(input_file_path, guest_file_path, [])
            progress.wait_for_completion(-1)

            if progress.result_code == 0:
                print("[LOG] Copy successful from " + input_file_path + " to " + guest_file_path)
                break

        except Exception as e:
            print_error(e)

    time.sleep(2)

    # Execute a command in the guest OS
    while True:
        try:
            process, stdout, stderr = guest_session.execute("/bin/python3", ["/home/remnux/Shared/MA_DataCollection.py"])
            time.sleep(10)
            # Print the command output
            print(str(stdout, 'UTF-8'))
            break

        except Exception as e:
            print_error(e)

    # 4. Sending back the output file from GUEST to HOST (Output)
    guest_output_main_path = "/home/remnux/Shared/"
    output_file_paths = ['Manalyze.json', 'Strings.txt', 'DIE.json', 'PEframe.json']
    
    for f in output_file_paths:
        while True:
            try:
                progess = guest_session.file_copy_from_guest(guest_output_main_path + f, output_main_path + f, [])
                progress.wait_for_completion(-1)

                if progress.result_code == 0:
                    print("[LOG] Copy successful from " + guest_main_path + f + " to " + output_main_path + f)
                    break

            except Exception as e:
                print_error(e)

        time.sleep(2)

    # Power off the virtual machine
    # session.console.power_down()

    time.sleep(2)


if __name__ == "__main__":
    malware_file_path = "D:\\VIT\\Year3Sem2\\J_AI_Antivirus\\Code\\pestudio.exe"
    output_destination_path = "D:\\VIT\\Year3Sem2\\J_AI_Antivirus\\Code\\"
    extractLogsFromVirtualBox("REMnux", "remnux", "malware", malware_file_path, output_destination_path)