# Writes a file in the format
# specified in the README to 
# a python 2D list.

def file_to_list(filename):

    line_list = []
    try:
        f = open(filename,"r")
        for line in f:

            list_ver = line.split("|")
            last_item = list_ver[len(list_ver)-1] 

            list_ver[len(list_ver)-1] = last_item[:len(last_item)-1]          
            line_list.append(list_ver)

        f.close()

    except Exception as e:
        print(e)
        print("Read error: " + filename + " doesn't exist")

    return line_list

# Writes a python 2D list to file
# in the format specified in the README.

def write_list_to_file(filename,line_list):

    try:
        f = open(filename,"w")
        for line in line_list:
            for x in range(0,len(line)):
                if x == (len(line)-1):
                    f.write(str(line[x]) + "\n")
                else:
                    f.write(str(line[x]) + "|")
        
        f.close()

    except Exception as e:
        print(e)
        print("Write error: " + filename + " doesn't exist")


# Gets the public channel ID.

def get_public_channel():

    bot_info_list = file_to_list("bot_info.dat")

    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    return int(bot_info_list[0][0])

# Gets the private channel ID.

def get_private_channel():

    bot_info_list = file_to_list("bot_info.dat")

    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    return int(bot_info_list[0][1])

# Gets the owner's ID.

def get_owner():

    bot_info_list = file_to_list("bot_info.dat")

    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])
        
    return int(bot_info_list[0][2])
