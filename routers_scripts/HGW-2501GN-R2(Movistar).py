import sys
import telnetlib	 
if len(sys.argv) < 2:
    sys.exit('Usage: %s num of args' % sys.argv[0])
	
host="192.168.1.1"
user = "1234"
password = "2adfe871"
estado = sys.argv[1]

if estado=="true" or estado=="True" or estado=="1":
	estado_label="up"
elif estado=="false" or estado=="False" or estado=="0":
	estado_label="down"
	
tn = telnetlib.Telnet(host)
tn.read_until("Login:")
tn.write(user+"\n")
tn.read_until("Password:")
tn.write(password+"\n")
tn.read_until(">")
tn.write("wlan config status "+ estado_label +"\n")
tn.read_until(">")
tn.write("exit"+"\n")