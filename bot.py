import logging
import re
import os
import subprocess
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

load_dotenv(override=True)

RM_HOST = os.getenv("RM_HOST")
PORT = int(os.getenv("RM_PORT"))
USER = os.getenv("RM_USER")
PASSWORD = os.getenv("RM_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_DATABASE")

TOKEN = str(os.getenv("TOKEN"))

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def ssh_connect(command):
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=RM_HOST, username=USER, password=PASSWORD, port=PORT)

        stdin, stdout, stderr = client.exec_command(command)

        result = stdout.read().decode('utf-8')

    except Exception as e:
        result = str(e)

    finally:
        client.close()

    return result


def get_data_from_database(update: Update, context, query):
    try:
        with psycopg2.connect(user=DB_USER,
                              password=DB_PASSWORD,
                              host=DB_HOST,
                              port=DB_PORT,
                              database=DATABASE) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()

                if data:
                    formatted_data = '\n'.join([f'{i+1}. {row[0]}' for i, row in enumerate(data)])
                    update.message.reply_text(formatted_data)
                else:
                    update.message.reply_text("Данные не найдены.")

    except (Exception, Error) as error:
        update.message.reply_text(f"Произошла ошибка при выполнении запроса: {error}")

def get_emails(update: Update, context):
    query = "SELECT email FROM emails;"
    get_data_from_database(update, context, query)

def get_phone_numbers(update: Update, context):
    query = "SELECT phone_number FROM phones;"
    get_data_from_database(update, context, query)


import subprocess

def get_repl_logs(update: Update, context):
    update.message.reply_text("Ищу логи о репликации...")
    
    repl_logs_info = ssh_connect("sudo cat /var/log/postgresql/postgresql-15-main.log | grep repl")

    if len(repl_logs_info) > 4096:
        update.message.reply_text(repl_logs_info[:4096])
    else:
        update.message.reply_text(repl_logs_info)

def get_release(update: Update, context):
    release_info = ssh_connect("lsb_release -a")
    update.message.reply_text(release_info)

def get_uname(update: Update, context):
    uname_info = ssh_connect("uname -a")
    update.message.reply_text(uname_info)

def get_uptime(update: Update, context):
    uptime_info = ssh_connect("uptime")
    update.message.reply_text(uptime_info)

def get_df(update: Update, context):
    df_info = ssh_connect("df -h")
    update.message.reply_text(df_info)

def get_free(update: Update, context):
    free_info = ssh_connect("free -h")
    update.message.reply_text(free_info)

def get_mpstat(update: Update, context):
    mpstat_info = ssh_connect("mpstat")
    update.message.reply_text(mpstat_info)

def get_w(update: Update, context):
    w_info = ssh_connect("w")
    update.message.reply_text(w_info)

def get_auths(update: Update, context):
    auths_info = ssh_connect("last -n 10")
    update.message.reply_text(auths_info)

def get_critical(update: Update, context):
    critical_info = ssh_connect("journalctl -n 5 -p crit")
    update.message.reply_text(critical_info)

def get_ps(update: Update, context):
    ps_info = ssh_connect("ps aux | head -n 30")
    update.message.reply_text(ps_info)

def get_ss(update: Update, context):
    ss_info = ssh_connect("ss -tuln")
    update.message.reply_text(ss_info)


CHOOSING_ACTION, SEARCHING_PACKAGE = range(2)

def get_apt_list(update: Update, context):
    update.message.reply_text(
        "Выберите действие:\n"
        "1. Вывести все пакеты\n"
        "2. Поиск информации о пакете\n"
        "Отправьте соответствующую цифру."
    )

    return 'choose_action'

def choose_action(update: Update, context):
    action = update.message.text

    if action == "1":
        apt_list_info = ssh_connect("dpkg -l")
        if len(apt_list_info) > 4096:
            update.message.reply_text(apt_list_info[:4096])
        else:
            update.message.reply_text(apt_list_info)
        return ConversationHandler.END
    elif action == "2":
        update.message.reply_text("Введите название пакета для поиска:")
        return 'search_package'
    else:
        update.message.reply_text("Пожалуйста, выберите действие, отправив соответствующую цифру.")
        return 'choose_action'

def search_package(update: Update, context):
    package_name = update.message.text

    apt_package_info = ssh_connect(f"dpkg -l | grep {package_name}")
    
    if not apt_package_info.strip():
        update.message.reply_text("Ничего не найдено.")
    else:
        if len(apt_package_info) > 4096:
            update.message.reply_text(apt_package_info[:4096])
        else:
            update.message.reply_text(apt_package_info)

    return ConversationHandler.END


def get_services(update: Update, context):
    services_info = ssh_connect("systemctl list-units --type=service --state=running")

    update.message.reply_text(services_info)


def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите ваш пароль для проверки сложности')

    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*[A-Z])(?=.*[!\@\#\$\%\^\&\*\(\)\])(?=.*[a-zA-Z]).{8,}$')

    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    
    return ConversationHandler.END


def db_connect():
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DATABASE
        )
        return connection
    except (Exception, Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email-адреса')
    return 'findEmail'

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findEmail(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Email-адреса не были найдены')
        return ConversationHandler.END

    unique_emails = list(set(emailList))
    emails = ''
    for i, email in enumerate(unique_emails):
        emails += f'{i+1}. {email}\n'

    update.message.reply_text(emails)

    context.user_data['emails'] = unique_emails

    update.message.reply_text('Хотите сохранить найденные email-адреса в базе данных? Ответьте "Да" или "Нет".')
    return 'save_emails'

def save_emails(update: Update, context):
    user_input = update.message.text.lower()

    if user_input in ['да', 'yes', 'y']:
        connection = db_connect()
        if connection:
            try:
                cursor = connection.cursor()
                emails = context.user_data.get('emails', [])

                for email in emails:
                    cursor.execute("SELECT 1 FROM emails WHERE email = %s;", (email,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
                
                connection.commit()
                update.message.reply_text('Email-адреса успешно сохранены в базе данных.')
            except (Exception, Error) as error:
                logger.error(f"Error while inserting email addresses into the database: {error}")
                update.message.reply_text('Произошла ошибка при сохранении email-адресов в базу данных.')
            finally:
                cursor.close()
                connection.close()
        else:
            update.message.reply_text('Не удалось подключиться к базе данных. Пожалуйста, попробуйте позже.')
    else:
        update.message.reply_text('Email-адреса не будут сохранены в базе данных.')

    return ConversationHandler.END

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    unique_phone_numbers = list(set(phoneNumberList))
    phone_numbers = ''
    for i, number in enumerate(unique_phone_numbers):
        phone_numbers += f'{i+1}. {number}\n'

    update.message.reply_text(phone_numbers)

    context.user_data['phone_numbers'] = unique_phone_numbers

    update.message.reply_text('Хотите сохранить найденные телефонные номера в базе данных? Ответьте "Да" или "Нет".')
    return 'save_phone_numbers'

def save_phone_numbers(update: Update, context):
    user_input = update.message.text.lower()

    if user_input in ['да', 'yes', 'y']:
        connection = db_connect()
        if connection:
            try:
                cursor = connection.cursor()
                phone_numbers = context.user_data.get('phone_numbers', [])

                for number in phone_numbers:
                    cursor.execute("SELECT 1 FROM phones WHERE phone_number = %s;", (number,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO phones (phone_number) VALUES (%s);", (number,))
                
                connection.commit()
                update.message.reply_text('Телефонные номера успешно сохранены в базе данных.')
            except (Exception, Error) as error:
                logger.error(f"Error while inserting phone numbers into the database: {error}")
                update.message.reply_text('Произошла ошибка при сохранении телефонных номеров в базу данных.')
            finally:
                cursor.close()
                connection.close()
        else:
            update.message.reply_text('Не удалось подключиться к базе данных. Пожалуйста, попробуйте позже.')
    else:
        update.message.reply_text('Телефонные номера не будут сохранены в базе данных.')

    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher


    convHandlerCheckPassComplex = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )


    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('findEmail', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'save_emails': [MessageHandler(Filters.text & ~Filters.command, save_emails)],
        },
        fallbacks=[]
    )

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'save_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list)],
        states={
            'choose_action': [MessageHandler(Filters.text & ~Filters.command, choose_action)],
            'search_package': [MessageHandler(Filters.text & ~Filters.command, search_package)],
        },
        fallbacks=[]
    )

  	
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerCheckPassComplex)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerGetAptList)



    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))

    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
