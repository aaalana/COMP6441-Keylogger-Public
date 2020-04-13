import os, hashlib, sys, time

# Please remember to change the virus_list.txt to include the hash produced for the keylogger file 

# Collects all .pyw files from the OS
def collect_files():
    file_list = []
    rootdir = "C:\\"
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filepath = subdir + os.sep + file

            if filepath.endswith(".pyw"):
                file_list.append(filepath)
    return file_list

print("[+]Welcome to Keylogger Anti-virus[+]")
print("[+]Starting memory allocation. Please wait a few minutes...[+]")

file_list = collect_files()

print("[+]Memory allocation complete...[+]")
print("[+]Starting scan...[+]")

# Scans through the files to check if the keylogger virus is found in the files
def scan():
    infected_list = []
    for f in file_list:
        virus_defs = open("virus_list.txt", "r")
        print("\nscanning: {}".format(f))
        hasher = hashlib.md5()
        try:
            with open(f, "rb") as file:
                try:
                    buf = file.read()
                    hasher.update(buf)
                    file_signature = hasher.hexdigest()
                    print("File checksum/signature: {}".format(file_signature))
                    for line in virus_defs:
                        if file_signature == line.strip():
                            print("[!]Keylogger Detected[!] | File name: {}".format(f))
                            infected_list.append(f)
                except Exception as e:
                    print("Could not read file | Error: {}".format(e))
        except Exception as e:
            print("Error:", e)
            
    print("Infected files found: {}".format(infected_list))
    return infected_list

# Deletes all infected files is the user allows
def file_deletion(infected_list):
    if len(infected_list) == 0:
        print("The system is currently clean of pythonw keylogger viruses. :D")
        return

    delete_or_not = str(input("Would you like to delete all infected files (y/n): "))
    done = False
    while not done:
        if delete_or_not.upper() == "Y":
            for infected in infected_list:
                os.remove(infected)
                print("File removed: {}".format(infected))
            done = True
        elif delete_or_not.upper() == "N":
            print("File was not removed.")
            done = True
        else:
            delete_or_not = str(input("Would you like to delete the infected files (y/n): ")) 
    
# Allows the user to quit or continue the program
def quit_or_continue():
    quit = str(input("If you would like to quit the program, please type 'quit'.\nOtherwise, input anything else to continue... "))
    
    if quit.upper() == "QUIT":
        sys.exit()

# Running the all functions
while 1:
    infected_list = scan()
    file_deletion(infected_list)
    quit_or_continue()


