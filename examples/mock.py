
with open('shachen2_ping_ip.txt') as f:
    lines = f.readlines()
    newlines = []
    new_f = open('shachen2_ping_new_ip.txt', "w")
    for line in lines:
        begin = line.find(",") + 1
        newline = line[:begin] + "[39.99652306,116.32674703]," + line[begin:]
        newlines.append(newline)
    new_f.writelines(newlines)
    new_f.close()
