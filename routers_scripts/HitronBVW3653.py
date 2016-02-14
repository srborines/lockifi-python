import sys
import telnetlib	 
if len(sys.argv) < 2:
    sys.exit('Usage: %s num of args' % sys.argv[0])
	
host="192.168.1.1"
user = "admin"
password = "36631310"
estado = sys.argv[1]
	
tn = telnetlib.Telnet(host)
tn.read_until("Username:")
tn.write(user+"\n")
tn.read_until("Password:")
tn.write(password+"\n")
tn.read_until("wifimedia-R>")
tn.write("conf ram_set /dev/ra0/volatile_enabled "+ estado_int +"\n")
tn.read_until("wifimedia-R>")
tn.write("conf set /dev/ra0/enabled "+ estado_int +"\n")
tn.read_until("wifimedia-R>")
tn.write("conf reconf 4"+"\n")
tn.read_until("wifimedia-R>")
tn.write("exit"+"\n")