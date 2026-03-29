# -*- coding: utf-8 -*-
import subprocess
import sys
import os

# ✅ Auto-install missing modules
def auto_install(package):
    try:
        __import__(package)
    except ModuleNotFoundError:
        print(f"📦 Installing missing package: {package} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed: {package}")

# Auto-install required modules
for mod in ["telebot", "psutil", "requests", "flask"]:
    auto_install(mod)

# --- After auto-install, import all modules safely ---
import telebot
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import logging
import threading
import re
import atexit
import requests
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'am EXR HOSTING BOT"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")

# --- Configuration ---
TOKEN = '8766865080:AAGXf20R8pusctGMV1aU7axP1wc5Apqkzbk'
OWNER_ID = 8379062893
ADMIN_ID = 8379062893
YOUR_USERNAME = '@EXUCODR'
UPDATE_CHANNEL = 'https://t.me/exucodex'

# --- Force Subscription Configuration ---
FORCE_SUB_CHANNEL = 'https://t.me/exucodex'
FORCE_SUB_CHANNEL_ID = '@exucodex'
FORCE_SUB_CHANNEL_NAME = '𝐄𝐗𝐔 𝐏𝐑𝐈𝐌𝐄 ⚡'

# --- Styled Button Names ---
BTN_UPDATES = "📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥"
BTN_UPLOAD = "📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐅𝐢𝐥𝐞"
BTN_CHECK = "📂 𝐂𝐡𝐞𝐜𝐤 𝐅𝐢𝐥𝐞𝐬"
BTN_SPEED = "⚡ 𝐁𝐨𝐭 𝐒𝐩𝐞𝐞𝐝"
BTN_STATS = "📊 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬"
BTN_CONTACT = "📞 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐎𝐰𝐧𝐞𝐫"
BTN_SUBS = "💳 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧𝐬"
BTN_BROADCAST = "📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭"
BTN_LOCK = "🔒 𝐋𝐨𝐜𝐤 𝐁𝐨𝐭"
BTN_RUN_ALL = "🟢 𝐑𝐮𝐧 𝐀𝐥𝐥 𝐒𝐜𝐫𝐢𝐩𝐭𝐬"
BTN_ADMIN = "👑 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥"
BTN_PENDING = "⏳ 𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐀𝐩𝐩𝐫𝐨𝐯𝐚𝐥𝐬"

# Folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')
PENDING_DIR = os.path.join(BASE_DIR, 'pending_approvals')

# File upload limits
FREE_USER_LIMIT = 3
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

# Create necessary directories
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "𝐆𝐨𝐨𝐝 𝐌𝐨𝐫𝐧𝐢𝐧𝐠"
    elif 12 <= hour < 17:
        return "𝐆𝐨𝐨𝐝 𝐀𝐟𝐭𝐞𝐫𝐧𝐨𝐨𝐧"
    elif 17 <= hour < 21:
        return "𝐆𝐨𝐨𝐝 𝐄𝐯𝐞𝐧𝐢𝐧𝐠"
    else:
        return "𝐆𝐨𝐨𝐝 𝐍𝐢𝐠𝐡𝐭"

# --- Command Button Layouts ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    [BTN_UPDATES],
    [BTN_UPLOAD, BTN_CHECK],
    [BTN_SPEED, BTN_STATS],
    [BTN_CONTACT]
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    [BTN_UPDATES],
    [BTN_UPLOAD, BTN_CHECK],
    [BTN_SPEED, BTN_STATS],
    [BTN_SUBS, BTN_BROADCAST],
    [BTN_LOCK, BTN_RUN_ALL],
    [BTN_PENDING, BTN_ADMIN],
    [BTN_CONTACT]
]

# --- Database Setup ---
def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_approvals
                     (pending_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER, file_name TEXT, file_path TEXT,
                      file_type TEXT, timestamp TEXT, is_zip INTEGER DEFAULT 0)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                pass

        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users")
    except Exception as e:
        logger.error(f"Error loading data: {e}")

init_db()
load_data()

# --- Force Subscription Check ---
def is_subscribed(user_id):
    if user_id == OWNER_ID or user_id in admin_ids:
        return True
    try:
        chat_member = bot.get_chat_member(FORCE_SUB_CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking subscription for {user_id}: {e}")
        return False

def force_subscribe_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=FORCE_SUB_CHANNEL),
        types.InlineKeyboardButton("✅ 𝐂𝐡𝐞𝐜𝐤 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧", callback_data='check_sub')
    )
    return markup

# --- User Functions ---
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID:
        return OWNER_LIMIT
    if user_id in admin_ids:
        return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except:
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
    return False

def save_user_file(user_id, file_name, file_type='py'):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                  (user_id, file_name, file_type))
        conn.commit()
        if user_id not in user_files:
            user_files[user_id] = []
        user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type))
        logger.info(f"Saved file: {file_name} for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
    finally:
        conn.close()

def remove_user_file_db(user_id, file_name):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
        conn.commit()
        if user_id in user_files:
            user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
            if not user_files[user_id]:
                del user_files[user_id]
        logger.info(f"Removed file: {file_name} for user {user_id}")
    except Exception as e:
        logger.error(f"Error removing file: {e}")
    finally:
        conn.close()

def add_active_user(user_id):
    if user_id in active_users:
        return
    active_users.add(user_id)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error adding active user: {e}")
    finally:
        conn.close()

def save_pending_approval(user_id, file_name, file_path, file_type, is_zip=0):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        timestamp = datetime.now().isoformat()
        c.execute('''INSERT INTO pending_approvals (user_id, file_name, file_path, file_type, timestamp, is_zip)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, file_name, file_path, file_type, timestamp, is_zip))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        logger.error(f"Error saving pending approval: {e}")
        return None
    finally:
        conn.close()

def get_pending_approvals():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('SELECT pending_id, user_id, file_name, file_type, timestamp, is_zip FROM pending_approvals ORDER BY timestamp DESC')
        return c.fetchall()
    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        return []
    finally:
        conn.close()

def delete_pending_approval(pending_id):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error deleting pending approval: {e}")
    finally:
        conn.close()

def save_subscription(user_id, expiry):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        expiry_str = expiry.isoformat()
        c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
        conn.commit()
        user_subscriptions[user_id] = {'expiry': expiry}
    except Exception as e:
        logger.error(f"Error saving subscription: {e}")
    finally:
        conn.close()

def remove_subscription_db(user_id):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
        conn.commit()
        if user_id in user_subscriptions:
            del user_subscriptions[user_id]
    except Exception as e:
        logger.error(f"Error removing subscription: {e}")
    finally:
        conn.close()

def add_admin_db(admin_id):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
        conn.commit()
        admin_ids.add(admin_id)
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
    finally:
        conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        return False
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
        conn.commit()
        removed = c.rowcount > 0
        if removed:
            admin_ids.discard(admin_id)
        return removed
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        return False
    finally:
        conn.close()

# --- Menu Creation ---
def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row in layout:
        markup.add(*[types.KeyboardButton(text) for text in row])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.add(
            types.InlineKeyboardButton("🔴 𝐒𝐭𝐨𝐩", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 𝐑𝐞𝐬𝐭𝐚𝐫𝐭", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.add(
            types.InlineKeyboardButton("🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 𝐋𝐨𝐠𝐬", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.add(
            types.InlineKeyboardButton("🟢 𝐒𝐭𝐚𝐫𝐭", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.add(types.InlineKeyboardButton("📜 𝐕𝐢𝐞𝐰 𝐋𝐨𝐠𝐬", callback_data=f'logs_{script_owner_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data='back_to_files'))
    return markup

def create_approval_buttons(pending_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞", callback_data=f'approve_{pending_id}'),
        types.InlineKeyboardButton("❌ 𝐑𝐞𝐣𝐞𝐜𝐭", callback_data=f'reject_{pending_id}')
    )
    return markup

# --- ZIP File Processing ---
def process_zip_file(zip_path, user_id, file_name):
    """Extract zip and find main script"""
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find all files
        all_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                all_files.append(os.path.join(root, file))
        
        # Look for main script files
        py_files = [f for f in all_files if f.endswith('.py')]
        js_files = [f for f in all_files if f.endswith('.js')]
        
        # Priority order for main script
        preferred_py = ['main.py', 'bot.py', 'app.py', 'run.py', 'index.py']
        preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js', 'server.js']
        
        main_script = None
        file_type = None
        
        # Check for preferred Python files
        for pref in preferred_py:
            for f in py_files:
                if os.path.basename(f) == pref:
                    main_script = f
                    file_type = 'py'
                    break
            if main_script:
                break
        
        # Check for preferred JS files
        if not main_script:
            for pref in preferred_js:
                for f in js_files:
                    if os.path.basename(f) == pref:
                        main_script = f
                        file_type = 'js'
                        break
                if main_script:
                    break
        
        # If no preferred, take first Python file
        if not main_script and py_files:
            main_script = py_files[0]
            file_type = 'py'
        
        # If no Python, take first JS file
        if not main_script and js_files:
            main_script = js_files[0]
            file_type = 'js'
        
        if not main_script:
            return None, None, None
        
        # Get the main script name
        main_script_name = os.path.basename(main_script)
        
        # Copy all files to user folder
        user_folder = get_user_folder(user_id)
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join(user_folder, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Also copy requirements.txt if exists
        req_file = os.path.join(temp_dir, 'requirements.txt')
        if os.path.exists(req_file):
            shutil.copy2(req_file, user_folder)
        
        # Also copy package.json if exists
        pkg_file = os.path.join(temp_dir, 'package.json')
        if os.path.exists(pkg_file):
            shutil.copy2(pkg_file, user_folder)
        
        return main_script_name, file_type, user_folder
        
    except Exception as e:
        logger.error(f"Error processing zip: {e}")
        return None, None, None
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

# --- Script Running Functions ---
def run_script(script_path, script_owner_id, user_folder, file_name, message):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE
        )
        
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name
        }
        
        bot.reply_to(message, f"✅ 𝐏𝐲𝐭𝐡𝐨𝐧 𝐬𝐜𝐫𝐢𝐩𝐭 `{file_name}` 𝐬𝐭𝐚𝐫𝐭𝐞𝐝! (PID: {process.pid})", parse_mode='Markdown')
        logger.info(f"Started Python script: {file_name} for user {script_owner_id}")
        
    except Exception as e:
        logger.error(f"Error running script: {e}")
        bot.reply_to(message, f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐬𝐜𝐫𝐢𝐩𝐭: {str(e)}")

def run_js_script(script_path, script_owner_id, user_folder, file_name, message):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        process = subprocess.Popen(
            ['node', script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE
        )
        
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name
        }
        
        bot.reply_to(message, f"✅ 𝐉𝐚𝐯𝐚𝐒𝐜𝐫𝐢𝐩𝐭 𝐬𝐜𝐫𝐢𝐩𝐭 `{file_name}` 𝐬𝐭𝐚𝐫𝐭𝐞𝐝! (PID: {process.pid})", parse_mode='Markdown')
        logger.info(f"Started JS script: {file_name} for user {script_owner_id}")
        
    except FileNotFoundError:
        bot.reply_to(message, "❌ 𝐍𝐨𝐝𝐞.𝐣𝐬 𝐢𝐬 𝐧𝐨𝐭 𝐢𝐧𝐬𝐭𝐚𝐥𝐥𝐞𝐝! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐢𝐧𝐬𝐭𝐚𝐥𝐥 𝐍𝐨𝐝𝐞.𝐣𝐬 𝐭𝐨 𝐫𝐮𝐧 𝐉𝐚𝐯𝐚𝐒𝐜𝐫𝐢𝐩𝐭 𝐟𝐢𝐥𝐞𝐬.")
    except Exception as e:
        logger.error(f"Error running JS script: {e}")
        bot.reply_to(message, f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐉𝐒 𝐬𝐜𝐫𝐢𝐩𝐭: {str(e)}")

# --- Welcome Message ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    
    if not is_subscribed(user_id):
        msg = (f"╔═══《 🎉 {get_greeting()}! 》═══╗\n\n"
               f"👤 𝐔𝐬𝐞𝐫: {user_name}\n"
               f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: `{user_id}`\n\n"
               f"╰═══════《 🤖 》═══════╝\n\n"
               f"⚠️ 𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭!\n\n"
               f"📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥: {FORCE_SUB_CHANNEL_NAME}")
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=force_subscribe_markup())
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, "⚠️ 𝐁𝐨𝐭 𝐥𝐨𝐜𝐤𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧. 𝐓𝐫𝐲 𝐥𝐚𝐭𝐞𝐫.")
        return
    
    if user_id not in active_users:
        add_active_user(user_id)
        try:
            bot.send_message(OWNER_ID, f"🎉 𝐍𝐞𝐰 𝐮𝐬𝐞𝐫!\n👤 {user_name}\n🆔 `{user_id}`", parse_mode='Markdown')
        except:
            pass
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝"
    
    if user_id == OWNER_ID:
        user_status = "𝐎𝐰𝐧𝐞𝐫"
        status_icon = "👑"
    elif user_id in admin_ids:
        user_status = "𝐀𝐝𝐦𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐭𝐨𝐫"
        status_icon = "🛡️"
    else:
        user_status = "𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫"
        status_icon = "🆓"
    
    welcome_msg = (f"╔═══《 🎉 {get_greeting()}! 》═══╗\n\n"
                  f"👤 𝐔𝐬𝐞𝐫: {user_name}\n"
                  f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: `{user_id}`\n"
                  f"{status_icon} 𝐒𝐭𝐚𝐭𝐮𝐬: {user_status}\n\n"
                  f"╰═══════《 🤖 》═══════╝\n\n"
                  f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐄𝐗𝐑 𝐄𝐗𝐔 | 𝐗𝐒𝐔\n\n"
                  f"📌 𝐀𝐛𝐨𝐮𝐭 𝐓𝐡𝐢𝐬 𝐁𝐨𝐭:\n"
                  f"• 🔐 𝐒𝐞𝐜𝐮𝐫𝐞 𝐅𝐢𝐥𝐞 𝐇𝐨𝐬𝐭\n"
                  f"• 📊 𝐙𝐈𝐏 & 𝐒𝐜𝐫𝐢𝐩𝐭 𝐇𝐨𝐬𝐭𝐢𝐧𝐠\n"
                  f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                  f"✅ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐆𝐫𝐚𝐧𝐭𝐞𝐝!\n\n"
                  f"📌 𝐐𝐮𝐢𝐜𝐤 𝐆𝐮𝐢𝐝𝐞:\n"
                  f"• 𝐔𝐬𝐞 𝐦𝐞𝐧𝐮 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐧𝐚𝐯𝐢𝐠𝐚𝐭𝐞\n"
                  f"• /𝐡𝐞𝐥𝐩 𝐟𝐨𝐫 𝐦𝐨𝐫𝐞 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
                  f"• 📁 𝐌𝐲 𝐅𝐢𝐥𝐞𝐬 𝐭𝐨 𝐯𝐢𝐞𝐰 𝐚𝐜𝐜𝐞𝐬𝐬𝐞𝐝 𝐟𝐢𝐥𝐞𝐬\n\n"
                  f"📁 𝐅𝐢𝐥𝐞𝐬 𝐔𝐩𝐥𝐨𝐚𝐝𝐞𝐝: {current_files} / {limit_str}\n\n"
                  f"⚠️ 𝐍𝐨𝐭𝐞: 𝐈𝐟 𝐲𝐨𝐮 𝐥𝐞𝐚𝐯𝐞 𝐚𝐧𝐲 𝐜𝐡𝐚𝐧𝐧𝐞𝐥/𝐠𝐫𝐨𝐮𝐩, 𝐲𝐨𝐮 𝐰𝐢𝐥𝐥 𝐥𝐨𝐬𝐞 𝐚𝐜𝐜𝐞𝐬𝐬 𝐢𝐦𝐦𝐞𝐝𝐢𝐚𝐭𝐞𝐥𝐲!")
    
    markup = create_reply_keyboard_main_menu(user_id)
    bot.send_message(chat_id, welcome_msg, reply_markup=markup, parse_mode='Markdown')

# --- Button Handlers ---
@bot.message_handler(func=lambda message: message.text == BTN_UPDATES)
def updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=UPDATE_CHANNEL))
    bot.reply_to(message, "𝐕𝐢𝐬𝐢𝐭 𝐨𝐮𝐫 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == BTN_UPLOAD)
def upload_file(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.reply_to(message, "⚠️ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!", reply_markup=force_subscribe_markup())
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐁𝐨𝐭 𝐥𝐨𝐜𝐤𝐞𝐝, 𝐜𝐚𝐧𝐧𝐨𝐭 𝐚𝐜𝐜𝐞𝐩𝐭 𝐟𝐢𝐥𝐞𝐬.")
        return
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝"
        bot.reply_to(message, f"⚠️ 𝐅𝐢𝐥𝐞 𝐥𝐢𝐦𝐢𝐭 ({current_files}/{limit_str}) 𝐫𝐞𝐚𝐜𝐡𝐞𝐝. 𝐃𝐞𝐥𝐞𝐭𝐞 𝐟𝐢𝐥𝐞𝐬 𝐟𝐢𝐫𝐬𝐭.")
        return
    
    bot.reply_to(message, "📤 𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐏𝐲𝐭𝐡𝐨𝐧 (`.py`), 𝐉𝐚𝐯𝐚𝐒𝐜𝐫𝐢𝐩𝐭 (`.js`), 𝐨𝐫 𝐙𝐈𝐏 (`.zip`) 𝐟𝐢𝐥𝐞.\n\n📌 𝐅𝐢𝐥𝐞 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐚𝐝𝐦𝐢𝐧 𝐟𝐨𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥 𝐛𝐞𝐟𝐨𝐫𝐞 𝐡𝐨𝐬𝐭𝐢𝐧𝐠.")

@bot.message_handler(func=lambda message: message.text == BTN_CHECK)
def check_files(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.reply_to(message, "⚠️ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!", reply_markup=force_subscribe_markup())
        return
    
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, "📂 𝐘𝐨𝐮𝐫 𝐟𝐢𝐥𝐞𝐬:\n\n(𝐍𝐨 𝐟𝐢𝐥𝐞𝐬 𝐮𝐩𝐥𝐨𝐚𝐝𝐞𝐝 𝐲𝐞𝐭)")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status = "🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠" if is_running else "🔴 𝐒𝐭𝐨𝐩𝐩𝐞𝐝"
        markup.add(types.InlineKeyboardButton(f"{file_name} ({file_type}) - {status}", callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, "📂 𝐘𝐨𝐮𝐫 𝐟𝐢𝐥𝐞𝐬:\n𝐂𝐥𝐢𝐜𝐤 𝐭𝐨 𝐦𝐚𝐧𝐚𝐠𝐞.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == BTN_SPEED)
def bot_speed(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.reply_to(message, "⚠️ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!", reply_markup=force_subscribe_markup())
        return
    
    start = time.time()
    msg = bot.reply_to(message, "🏃 𝐓𝐞𝐬𝐭𝐢𝐧𝐠 𝐬𝐩𝐞𝐞𝐝...")
    latency = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(f"⚡ 𝐁𝐨𝐭 𝐒𝐩𝐞𝐞𝐝 & 𝐒𝐭𝐚𝐭𝐮𝐬:\n\n⏱️ 𝐀𝐏𝐈 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 𝐓𝐢𝐦𝐞: {latency} ms", msg.chat.id, msg.message_id)

@bot.message_handler(func=lambda message: message.text == BTN_STATS)
def statistics(message):
    user_id = message.from_user.id
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    pending = len(get_pending_approvals())
    running = len(bot_scripts)
    
    stats = (f"📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬:\n\n"
             f"👥 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬: {total_users}\n"
             f"📂 𝐓𝐨𝐭𝐚𝐥 𝐅𝐢𝐥𝐞𝐬: {total_files}\n"
             f"🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠 𝐁𝐨𝐭𝐬: {running}\n"
             f"⏳ 𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐀𝐩𝐩𝐫𝐨𝐯𝐚𝐥𝐬: {pending}")
    bot.reply_to(message, stats)

@bot.message_handler(func=lambda message: message.text == BTN_CONTACT)
def contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📞 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐎𝐰𝐧𝐞𝐫", url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, "𝐂𝐥𝐢𝐜𝐤 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐎𝐰𝐧𝐞𝐫:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == BTN_SUBS)
def subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    bot.reply_to(message, "💳 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭\n\n"
                         "𝐔𝐬𝐞 𝐭𝐡𝐞𝐬𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
                         "/𝐚𝐝𝐝𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝> <𝐝𝐚𝐲𝐬>\n"
                         "/𝐫𝐞𝐦𝐨𝐯𝐞𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝>\n"
                         "/𝐜𝐡𝐞𝐜𝐤𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝>")

@bot.message_handler(func=lambda message: message.text == BTN_BROADCAST)
def broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    msg = bot.reply_to(message, "📢 𝐒𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭.\n/𝐜𝐚𝐧𝐜𝐞𝐥 𝐭𝐨 𝐚𝐛𝐨𝐫𝐭.")
    bot.register_next_step_handler(msg, process_broadcast)

@bot.message_handler(func=lambda message: message.text == BTN_LOCK)
def toggle_lock(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "𝐥𝐨𝐜𝐤𝐞𝐝" if bot_locked else "𝐮𝐧𝐥𝐨𝐜𝐤𝐞𝐝"
    bot.reply_to(message, f"🔒 𝐁𝐨𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 {status}.")

@bot.message_handler(func=lambda message: message.text == BTN_RUN_ALL)
def run_all_scripts(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    
    bot.reply_to(message, "⏳ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐚𝐥𝐥 𝐬𝐜𝐫𝐢𝐩𝐭𝐬...")
    started = 0
    for user_id, files in user_files.items():
        for file_name, file_type in files:
            if not is_bot_running(user_id, file_name):
                user_folder = get_user_folder(user_id)
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                        else:
                            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                        started += 1
                        time.sleep(0.5)
                    except:
                        pass
    bot.reply_to(message, f"✅ 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 {started} 𝐬𝐜𝐫𝐢𝐩𝐭𝐬!")

@bot.message_handler(func=lambda message: message.text == BTN_ADMIN)
def admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    bot.reply_to(message, "👑 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥\n\n"
                         "𝐔𝐬𝐞 𝐭𝐡𝐞𝐬𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
                         "/𝐚𝐝𝐝𝐚𝐝𝐦𝐢𝐧 <𝐢𝐝>\n"
                         "/𝐫𝐞𝐦𝐨𝐯𝐞𝐚𝐝𝐦𝐢𝐧 <𝐢𝐝>\n"
                         "/𝐥𝐢𝐬𝐭𝐚𝐝𝐦𝐢𝐧𝐬")

@bot.message_handler(func=lambda message: message.text == BTN_PENDING)
def pending_approvals(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    
    pending_list = get_pending_approvals()
    if not pending_list:
        bot.reply_to(message, "📭 𝐍𝐨 𝐩𝐞𝐧𝐝𝐢𝐧𝐠 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥𝐬.")
        return
    
    for pending_id, user_id, file_name, file_type, timestamp, is_zip in pending_list[:5]:
        zip_indicator = "📦 " if is_zip else ""
        markup = create_approval_buttons(pending_id)
        bot.send_message(message.chat.id, 
                        f"⏳ {zip_indicator}𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐅𝐢𝐥𝐞:\n"
                        f"👤 𝐔𝐬𝐞𝐫: `{user_id}`\n"
                        f"📄 𝐅𝐢𝐥𝐞: `{file_name}`\n"
                        f"📁 𝐓𝐲𝐩𝐞: {file_type.upper()}\n"
                        f"⏰ 𝐓𝐢𝐦𝐞: {timestamp[:19]}",
                        parse_mode='Markdown', reply_markup=markup)

# --- File Upload Handler ---
@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        bot.reply_to(message, "⚠️ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!", reply_markup=force_subscribe_markup())
        return
    
    doc = message.document
    file_name = doc.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Check file type
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, f"⚠️ 𝐔𝐧𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐟𝐢𝐥𝐞 𝐭𝐲𝐩𝐞: `{file_ext}`\n\n𝐎𝐧𝐥𝐲 `.py`, `.js`, `.zip` 𝐟𝐢𝐥𝐞𝐬 𝐚𝐫𝐞 𝐚𝐥𝐥𝐨𝐰𝐞𝐝!", parse_mode='Markdown')
        return
    
    if doc.file_size > 50 * 1024 * 1024:
        bot.reply_to(message, "⚠️ 𝐅𝐢𝐥𝐞 𝐭𝐨𝐨 𝐥𝐚𝐫𝐠𝐞! 𝐌𝐚𝐱𝐢𝐦𝐮𝐦 𝐬𝐢𝐳𝐞: 50 𝐌𝐁")
        return
    
    # Check file limit
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝"
        bot.reply_to(message, f"⚠️ 𝐅𝐢𝐥𝐞 𝐥𝐢𝐦𝐢𝐭 𝐫𝐞𝐚𝐜𝐡𝐞𝐝! ({current_files}/{limit_str})\n\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐝𝐞𝐥𝐞𝐭𝐞 𝐬𝐨𝐦𝐞 𝐟𝐢𝐥𝐞𝐬 𝐭𝐨 𝐮𝐩𝐥𝐨𝐚𝐝 𝐦𝐨𝐫𝐞.")
        return
    
    try:
        # Download file
        wait_msg = bot.reply_to(message, f"⏳ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 `{file_name}`...", parse_mode='Markdown')
        file_info = bot.get_file(doc.file_id)
        file_content = bot.download_file(file_info.file_path)
        
        # Save to pending directory
        timestamp = int(time.time())
        pending_path = os.path.join(PENDING_DIR, f"{user_id}_{timestamp}_{file_name}")
        with open(pending_path, 'wb') as f:
            f.write(file_content)
        
        # Determine file type
        if file_ext == '.py':
            file_type = 'py'
            is_zip = 0
        elif file_ext == '.js':
            file_type = 'js'
            is_zip = 0
        else:
            file_type = 'zip'
            is_zip = 1
        
        # Save to database
        pending_id = save_pending_approval(user_id, file_name, pending_path, file_type, is_zip)
        
        if pending_id:
            bot.edit_message_text(f"✅ 𝐅𝐢𝐥𝐞 `{file_name}` 𝐝𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐝! 𝐒𝐞𝐧𝐝𝐢𝐧𝐠 𝐟𝐨𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥...", 
                                 message.chat.id, wait_msg.message_id, parse_mode='Markdown')
            
            # Notify admins
            file_info_msg = f"📄 𝐍𝐞𝐰 𝐅𝐢𝐥𝐞 𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐀𝐩𝐩𝐫𝐨𝐯𝐚𝐥!\n\n"
            file_info_msg += f"👤 𝐔𝐬𝐞𝐫: `{user_id}`\n"
            file_info_msg += f"📄 𝐅𝐢𝐥𝐞: `{file_name}`\n"
            file_info_msg += f"📁 𝐓𝐲𝐩𝐞: {file_type.upper()}\n"
            if is_zip:
                file_info_msg += f"📦 𝐅𝐨𝐫𝐦𝐚𝐭: 𝐙𝐈𝐏 𝐀𝐫𝐜𝐡𝐢𝐯𝐞\n"
            file_info_msg += f"💾 𝐒𝐢𝐳𝐞: {doc.file_size / 1024:.2f} KB"
            
            for admin_id in admin_ids:
                try:
                    bot.send_message(admin_id, file_info_msg, parse_mode='Markdown')
                    with open(pending_path, 'rb') as f:
                        bot.send_document(admin_id, f, caption="𝐀𝐩𝐩𝐫𝐨𝐯𝐞 𝐨𝐫 𝐑𝐞𝐣𝐞𝐜𝐭:", reply_markup=create_approval_buttons(pending_id))
                except Exception as e:
                    logger.error(f"Error notifying admin {admin_id}: {e}")
            
            bot.send_message(message.chat.id, f"✅ 𝐅𝐢𝐥𝐞 `{file_name}` 𝐮𝐩𝐥𝐨𝐚𝐝𝐞𝐝!\n⏳ 𝐀𝐰𝐚𝐢𝐭𝐢𝐧𝐠 𝐚𝐝𝐦𝐢𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥...", parse_mode='Markdown')
        else:
            bot.edit_message_text(f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐬𝐚𝐯𝐢𝐧𝐠 𝐟𝐢𝐥𝐞 𝐭𝐨 𝐝𝐚𝐭𝐚𝐛𝐚𝐬𝐞.", message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        bot.reply_to(message, f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐟𝐢𝐥𝐞: {str(e)}")

# --- Callback Handlers ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data
    user_id = call.from_user.id
    
    # Check subscription for non-admin
    if data not in ['check_sub', 'back_to_files'] and not is_subscribed(user_id) and user_id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!", show_alert=True)
        return
    
    # Check subscription callback
    if data == 'check_sub':
        if is_subscribed(user_id):
            bot.answer_callback_query(call.id, "✅ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞𝐝! 𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭.")
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞𝐝 𝐲𝐞𝐭! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭.", show_alert=True)
        return
    
    # Approve file callback
    if data.startswith('approve_'):
        if user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐞 𝐟𝐢𝐥𝐞𝐬!", show_alert=True)
            return
        
        pending_id = int(data.split('_')[1])
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id, file_name, file_path, file_type, is_zip FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        result = c.fetchone()
        
        if result:
            user_id_pending, file_name, file_path, file_type, is_zip = result
            
            try:
                if is_zip:
                    # Process ZIP file
                    bot.send_message(call.message.chat.id, f"⏳ 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐙𝐈𝐏 𝐟𝐢𝐥𝐞 `{file_name}`...", parse_mode='Markdown')
                    main_script_name, extracted_type, user_folder = process_zip_file(file_path, user_id_pending, file_name)
                    
                    if main_script_name:
                        # Save the main script to user files
                        save_user_file(user_id_pending, main_script_name, extracted_type)
                        
                        # Start the script
                        script_path = os.path.join(user_folder, main_script_name)
                        fake_message = types.Message()
                        fake_message.chat = call.message.chat
                        fake_message.from_user = types.User(id=user_id_pending)
                        
                        if extracted_type == 'py':
                            threading.Thread(target=run_script, args=(script_path, user_id_pending, user_folder, main_script_name, fake_message)).start()
                        else:
                            threading.Thread(target=run_js_script, args=(script_path, user_id_pending, user_folder, main_script_name, fake_message)).start()
                        
                        # Delete the original zip file
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        # Delete from pending
                        c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
                        conn.commit()
                        
                        # Notify user
                        try:
                            bot.send_message(user_id_pending, 
                                f"✅ 𝐘𝐨𝐮𝐫 𝐙𝐈𝐏 𝐟𝐢𝐥𝐞 `{file_name}` 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃!\n\n"
                                f"📄 𝐌𝐚𝐢𝐧 𝐬𝐜𝐫𝐢𝐩𝐭: `{main_script_name}`\n"
                                f"🚀 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠", parse_mode='Markdown')
                        except:
                            pass
                        
                        bot.answer_callback_query(call.id, f"✅ 𝐙𝐈𝐏 𝐟𝐢𝐥𝐞 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝! 𝐌𝐚𝐢𝐧 𝐬𝐜𝐫𝐢𝐩𝐭: {main_script_name}")
                        bot.edit_message_text(f"✅ 𝐙𝐈𝐏 𝐟𝐢𝐥𝐞 `{file_name}` 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐚𝐧𝐝 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐞𝐝!\n📄 𝐌𝐚𝐢𝐧 𝐬𝐜𝐫𝐢𝐩𝐭: `{main_script_name}`", 
                                             call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                    else:
                        bot.answer_callback_query(call.id, "❌ 𝐍𝐨 𝐏𝐲𝐭𝐡𝐨𝐧/𝐉𝐚𝐯𝐚𝐒𝐜𝐫𝐢𝐩𝐭 𝐟𝐢𝐥𝐞 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐙𝐈𝐏!", show_alert=True)
                        bot.edit_message_text(f"❌ 𝐙𝐈𝐏 𝐟𝐢𝐥𝐞 `{file_name}` - 𝐍𝐨 𝐏𝐲𝐭𝐡𝐨𝐧/𝐉𝐚𝐯𝐚𝐒𝐜𝐫𝐢𝐩𝐭 𝐟𝐢𝐥𝐞 𝐟𝐨𝐮𝐧𝐝!", 
                                             call.message.chat.id, call.message.message_id)
                else:
                    # Process single file
                    user_folder = get_user_folder(user_id_pending)
                    final_path = os.path.join(user_folder, file_name)
                    shutil.move(file_path, final_path)
                    
                    save_user_file(user_id_pending, file_name, file_type)
                    
                    # Start the script
                    fake_message = types.Message()
                    fake_message.chat = call.message.chat
                    fake_message.from_user = types.User(id=user_id_pending)
                    
                    if file_type == 'py':
                        threading.Thread(target=run_script, args=(final_path, user_id_pending, user_folder, file_name, fake_message)).start()
                    else:
                        threading.Thread(target=run_js_script, args=(final_path, user_id_pending, user_folder, file_name, fake_message)).start()
                    
                    # Delete from pending
                    c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
                    conn.commit()
                    
                    # Notify user
                    try:
                        bot.send_message(user_id_pending, 
                            f"✅ 𝐘𝐨𝐮𝐫 𝐟𝐢𝐥𝐞 `{file_name}` 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐚𝐧𝐝 𝐡𝐨𝐬𝐭𝐞𝐝!\n\n🚀 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠", parse_mode='Markdown')
                    except:
                        pass
                    
                    bot.answer_callback_query(call.id, f"✅ 𝐅𝐢𝐥𝐞 {file_name} 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝!")
                    bot.edit_message_text(f"✅ 𝐅𝐢𝐥𝐞 `{file_name}` 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐚𝐧𝐝 𝐡𝐨𝐬𝐭𝐞𝐝!", 
                                         call.message.chat.id, call.message.message_id, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error approving file: {e}")
                bot.answer_callback_query(call.id, f"❌ 𝐄𝐫𝐫𝐨𝐫: {str(e)[:50]}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ 𝐅𝐢𝐥𝐞 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!")
        conn.close()
        return
    
    # Reject file callback
    if data.startswith('reject_'):
        if user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐫𝐞𝐣𝐞𝐜𝐭 𝐟𝐢𝐥𝐞𝐬!", show_alert=True)
            return
        
        pending_id = int(data.split('_')[1])
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id, file_name, file_path FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        result = c.fetchone()
        
        if result:
            user_id_pending, file_name, file_path = result
            
            # Delete the file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete from database
            c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
            conn.commit()
            
            # Notify user
            try:
                bot.send_message(user_id_pending, 
                    f"❌ 𝐘𝐨𝐮𝐫 𝐟𝐢𝐥𝐞 `{file_name}` 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐑𝐄𝐉𝐄𝐂𝐓𝐄𝐃 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧.\n\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧 𝐟𝐨𝐫 𝐦𝐨𝐫𝐞 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧.", parse_mode='Markdown')
            except:
                pass
            
            bot.answer_callback_query(call.id, f"❌ 𝐅𝐢𝐥𝐞 {file_name} 𝐫𝐞𝐣𝐞𝐜𝐭𝐞𝐝!")
            bot.edit_message_text(f"❌ 𝐅𝐢𝐥𝐞 `{file_name}` 𝐫𝐞𝐣𝐞𝐜𝐭𝐞𝐝!", call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "❌ 𝐅𝐢𝐥𝐞 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!")
        conn.close()
        return
    
    # File management callbacks
    if data.startswith('file_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            
            if user_id != owner_id and user_id not in admin_ids:
                bot.answer_callback_query(call.id, "⚠️ 𝐘𝐨𝐮 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐦𝐚𝐧𝐚𝐠𝐞 𝐲𝐨𝐮𝐫 𝐨𝐰𝐧 𝐟𝐢𝐥𝐞𝐬!", show_alert=True)
                return
            
            is_running = is_bot_running(owner_id, file_name)
            bot.edit_message_text(f"⚙️ 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬 𝐟𝐨𝐫: `{file_name}`\n𝐒𝐭𝐚𝐭𝐮𝐬: {'🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠' if is_running else '🔴 𝐒𝐭𝐨𝐩𝐩𝐞𝐝'}",
                                 call.message.chat.id, call.message.message_id,
                                 reply_markup=create_control_buttons(owner_id, file_name, is_running),
                                 parse_mode='Markdown')
            bot.answer_callback_query(call.id)
        return
    
    # Start script callback
    if data.startswith('start_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            
            if user_id != owner_id and user_id not in admin_ids:
                bot.answer_callback_query(call.id, "⚠️ 𝐏𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐝𝐞𝐧𝐢𝐞𝐝!", show_alert=True)
                return
            
            user_folder = get_user_folder(owner_id)
            file_path = os.path.join(user_folder, file_name)
            file_info = next((f for f in user_files.get(owner_id, []) if f[0] == file_name), None)
            
            if file_info and os.path.exists(file_path):
                bot.answer_callback_query(call.id, "⏳ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠...")
                if file_info[1] == 'py':
                    threading.Thread(target=run_script, args=(file_path, owner_id, user_folder, file_name, call.message)).start()
                else:
                    threading.Thread(target=run_js_script, args=(file_path, owner_id, user_folder, file_name, call.message)).start()
                time.sleep(1)
                is_running = is_bot_running(owner_id, file_name)
                bot.edit_message_text(f"⚙️ 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬 𝐟𝐨𝐫: `{file_name}`\n𝐒𝐭𝐚𝐭𝐮𝐬: {'🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠' if is_running else '🟡 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠...'}",
                                     call.message.chat.id, call.message.message_id,
                                     reply_markup=create_control_buttons(owner_id, file_name, is_running),
                                     parse_mode='Markdown')
            else:
                bot.answer_callback_query(call.id, "❌ 𝐅𝐢𝐥𝐞 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!", show_alert=True)
        return
    
    # Stop script callback
    if data.startswith('stop_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            script_key = f"{owner_id}_{file_name}"
            
            if script_key in bot_scripts:
                try:
                    proc = bot_scripts[script_key]['process']
                    proc.terminate()
                    time.sleep(1)
                    if proc.poll() is None:
                        proc.kill()
                    if 'log_file' in bot_scripts[script_key]:
                        bot_scripts[script_key]['log_file'].close()
                    del bot_scripts[script_key]
                    bot.answer_callback_query(call.id, "🛑 𝐒𝐜𝐫𝐢𝐩𝐭 𝐬𝐭𝐨𝐩𝐩𝐞𝐝!")
                except Exception as e:
                    bot.answer_callback_query(call.id, f"❌ 𝐄𝐫𝐫𝐨𝐫: {str(e)[:50]}")
            else:
                bot.answer_callback_query(call.id, "⚠️ 𝐒𝐜𝐫𝐢𝐩𝐭 𝐧𝐨𝐭 𝐫𝐮𝐧𝐧𝐢𝐧𝐠!", show_alert=True)
            
            bot.edit_message_text(f"⚙️ 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬 𝐟𝐨𝐫: `{file_name}`\n𝐒𝐭𝐚𝐭𝐮𝐬: 🔴 𝐒𝐭𝐨𝐩𝐩𝐞𝐝",
                                 call.message.chat.id, call.message.message_id,
                                 reply_markup=create_control_buttons(owner_id, file_name, False),
                                 parse_mode='Markdown')
        return
    
    # Restart script callback
    if data.startswith('restart_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            script_key = f"{owner_id}_{file_name}"
            
            # Stop if running
            if script_key in bot_scripts:
                try:
                    proc = bot_scripts[script_key]['process']
                    proc.terminate()
                    time.sleep(1)
                    if proc.poll() is None:
                        proc.kill()
                    if 'log_file' in bot_scripts[script_key]:
                        bot_scripts[script_key]['log_file'].close()
                    del bot_scripts[script_key]
                except:
                    pass
            
            # Start again
            user_folder = get_user_folder(owner_id)
            file_path = os.path.join(user_folder, file_name)
            file_info = next((f for f in user_files.get(owner_id, []) if f[0] == file_name), None)
            
            if file_info and os.path.exists(file_path):
                bot.answer_callback_query(call.id, "🔄 𝐑𝐞𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠...")
                if file_info[1] == 'py':
                    threading.Thread(target=run_script, args=(file_path, owner_id, user_folder, file_name, call.message)).start()
                else:
                    threading.Thread(target=run_js_script, args=(file_path, owner_id, user_folder, file_name, call.message)).start()
                time.sleep(1)
                is_running = is_bot_running(owner_id, file_name)
                bot.edit_message_text(f"⚙️ 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬 𝐟𝐨𝐫: `{file_name}`\n𝐒𝐭𝐚𝐭𝐮𝐬: {'🟢 𝐑𝐮𝐧𝐧𝐢𝐧𝐠' if is_running else '🟡 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠...'}",
                                     call.message.chat.id, call.message.message_id,
                                     reply_markup=create_control_buttons(owner_id, file_name, is_running),
                                     parse_mode='Markdown')
            else:
                bot.answer_callback_query(call.id, "❌ 𝐅𝐢𝐥𝐞 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝!", show_alert=True)
        return
    
    # Delete script callback
    if data.startswith('delete_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            script_key = f"{owner_id}_{file_name}"
            
            # Stop if running
            if script_key in bot_scripts:
                try:
                    proc = bot_scripts[script_key]['process']
                    proc.terminate()
                    time.sleep(1)
                    if proc.poll() is None:
                        proc.kill()
                    if 'log_file' in bot_scripts[script_key]:
                        bot_scripts[script_key]['log_file'].close()
                    del bot_scripts[script_key]
                except:
                    pass
            
            # Delete files
            user_folder = get_user_folder(owner_id)
            file_path = os.path.join(user_folder, file_name)
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(log_path):
                os.remove(log_path)
            
            remove_user_file_db(owner_id, file_name)
            bot.answer_callback_query(call.id, "🗑️ 𝐅𝐢𝐥𝐞 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!")
            bot.edit_message_text(f"🗑️ 𝐅𝐢𝐥𝐞 `{file_name}` 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!", call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        return
    
    # View logs callback
    if data.startswith('logs_'):
        parts = data.split('_')
        if len(parts) >= 3:
            owner_id = int(parts[1])
            file_name = '_'.join(parts[2:])
            user_folder = get_user_folder(owner_id)
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()[-3000:]  # Last 3000 characters
                    if not log_content.strip():
                        log_content = "(𝐋𝐨𝐠 𝐢𝐬 𝐞𝐦𝐩𝐭𝐲)"
                    bot.send_message(call.message.chat.id, f"📜 𝐋𝐨𝐠𝐬 𝐟𝐨𝐫 `{file_name}`:\n```\n{log_content}\n```", parse_mode='Markdown')
                    bot.answer_callback_query(call.id)
                except Exception as e:
                    bot.answer_callback_query(call.id, f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐫𝐞𝐚𝐝𝐢𝐧𝐠 𝐥𝐨𝐠𝐬: {str(e)[:50]}", show_alert=True)
            else:
                bot.answer_callback_query(call.id, "❌ 𝐍𝐨 𝐥𝐨𝐠𝐬 𝐟𝐨𝐮𝐧𝐝 𝐟𝐨𝐫 𝐭𝐡𝐢𝐬 𝐬𝐜𝐫𝐢𝐩𝐭!", show_alert=True)
        return
    
    # Back to files callback
    if data == 'back_to_files':
        check_files(call.message)
        bot.answer_callback_query(call.id)
        return

# --- Broadcast Function ---
def process_broadcast(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, "𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝.")
        return
    
    broadcast_text = message.text
    if not broadcast_text:
        bot.reply_to(message, "⚠️ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐞𝐦𝐩𝐭𝐲 𝐦𝐞𝐬𝐬𝐚𝐠𝐞.")
        return
    
    bot.reply_to(message, f"⏳ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐢𝐧𝐠 𝐭𝐨 {len(active_users)} 𝐮𝐬𝐞𝐫𝐬...")
    
    sent = 0
    failed = 0
    for user_id in list(active_users):
        try:
            bot.send_message(user_id, broadcast_text)
            sent += 1
        except:
            failed += 1
        time.sleep(0.05)
    
    bot.reply_to(message, f"📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞!\n\n✅ 𝐒𝐞𝐧𝐭: {sent}\n❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {failed}")

# --- Admin Commands ---
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ 𝐎𝐧𝐥𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐚𝐝𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    try:
        new_admin_id = int(message.text.split()[1])
        if new_admin_id == OWNER_ID:
            bot.reply_to(message, "⚠️ 𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!")
            return
        add_admin_db(new_admin_id)
        bot.reply_to(message, f"✅ 𝐔𝐬𝐞𝐫 `{new_admin_id}` 𝐢𝐬 𝐧𝐨𝐰 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧!", parse_mode='Markdown')
        try:
            bot.send_message(new_admin_id, "🎉 𝐂𝐨𝐧𝐠𝐫𝐚𝐭𝐮𝐥𝐚𝐭𝐢𝐨𝐧𝐬! 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐩𝐫𝐨𝐦𝐨𝐭𝐞𝐝 𝐭𝐨 𝐚𝐝𝐦𝐢𝐧.")
        except:
            pass
    except:
        bot.reply_to(message, "𝐔𝐬𝐚𝐠𝐞: /𝐚𝐝𝐝𝐚𝐝𝐦𝐢𝐧 <𝐮𝐬𝐞𝐫_𝐢𝐝>")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ 𝐎𝐧𝐥𝐲 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐫𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    try:
        admin_id = int(message.text.split()[1])
        if admin_id == OWNER_ID:
            bot.reply_to(message, "⚠️ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐫𝐞𝐦𝐨𝐯𝐞 𝐭𝐡𝐞 𝐨𝐰𝐧𝐞𝐫!")
            return
        if remove_admin_db(admin_id):
            bot.reply_to(message, f"✅ 𝐀𝐝𝐦𝐢𝐧 `{admin_id}` 𝐫𝐞𝐦𝐨𝐯𝐞𝐝!", parse_mode='Markdown')
            try:
                bot.send_message(admin_id, "ℹ️ 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐟𝐫𝐨𝐦 𝐚𝐝𝐦𝐢𝐧 𝐫𝐨𝐥𝐞.")
            except:
                pass
        else:
            bot.reply_to(message, f"❌ 𝐔𝐬𝐞𝐫 `{admin_id}` 𝐢𝐬 𝐧𝐨𝐭 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧!", parse_mode='Markdown')
    except:
        bot.reply_to(message, "𝐔𝐬𝐚𝐠𝐞: /𝐫𝐞𝐦𝐨𝐯𝐞𝐚𝐝𝐦𝐢𝐧 <𝐮𝐬𝐞𝐫_𝐢𝐝>")

@bot.message_handler(commands=['listadmins'])
def list_admins(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    
    admin_list = "👑 𝐀𝐝𝐦𝐢𝐧 𝐋𝐢𝐬𝐭:\n\n"
    for aid in sorted(admin_ids):
        if aid == OWNER_ID:
            admin_list += f"👑 `{aid}` - 𝐎𝐰𝐧𝐞𝐫\n"
        else:
            admin_list += f"🛡️ `{aid}` - 𝐀𝐝𝐦𝐢𝐧\n"
    bot.reply_to(message, admin_list, parse_mode='Markdown')

@bot.message_handler(commands=['addsub'])
def add_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        days = int(parts[2])
        new_expiry = datetime.now() + timedelta(days=days)
        save_subscription(user_id, new_expiry)
        bot.reply_to(message, f"✅ 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐚𝐝𝐝𝐞𝐝 𝐭𝐨 `{user_id}` 𝐟𝐨𝐫 {days} 𝐝𝐚𝐲𝐬!\n📅 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {new_expiry.strftime('%Y-%m-%d')}", parse_mode='Markdown')
        try:
            bot.send_message(user_id, f"🎉 𝐘𝐨𝐮𝐫 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐚𝐜𝐭𝐢𝐯𝐚𝐭𝐞𝐝 𝐟𝐨𝐫 {days} 𝐝𝐚𝐲𝐬!\n📅 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {new_expiry.strftime('%Y-%m-%d')}")
        except:
            pass
    except:
        bot.reply_to(message, "𝐔𝐬𝐚𝐠𝐞: /𝐚𝐝𝐝𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝> <𝐝𝐚𝐲𝐬>")

@bot.message_handler(commands=['removesub'])
def remove_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in user_subscriptions:
            remove_subscription_db(user_id)
            bot.reply_to(message, f"✅ 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐟𝐫𝐨𝐦 `{user_id}`!", parse_mode='Markdown')
            try:
                bot.send_message(user_id, "ℹ️ 𝐘𝐨𝐮𝐫 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧.")
            except:
                pass
        else:
            bot.reply_to(message, f"❌ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐡𝐚𝐬 𝐧𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧!", parse_mode='Markdown')
    except:
        bot.reply_to(message, "𝐔𝐬𝐚𝐠𝐞: /𝐫𝐞𝐦𝐨𝐯𝐞𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝>")

@bot.message_handler(commands=['checksub'])
def check_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ 𝐀𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in user_subscriptions:
            expiry = user_subscriptions[user_id]['expiry']
            if expiry > datetime.now():
                days_left = (expiry - datetime.now()).days
                bot.reply_to(message, f"✅ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐡𝐚𝐬 𝐚𝐧 𝐚𝐜𝐭𝐢𝐯𝐞 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧!\n📅 𝐄𝐱𝐩𝐢𝐫𝐞𝐬: {expiry.strftime('%Y-%m-%d')}\n⏳ 𝐃𝐚𝐲𝐬 𝐥𝐞𝐟𝐭: {days_left}", parse_mode='Markdown')
            else:
                bot.reply_to(message, f"⚠️ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐡𝐚𝐬 𝐚𝐧 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧!\n📅 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐨𝐧: {expiry.strftime('%Y-%m-%d')}", parse_mode='Markdown')
                remove_subscription_db(user_id)
        else:
            bot.reply_to(message, f"❌ 𝐔𝐬𝐞𝐫 `{user_id}` 𝐡𝐚𝐬 𝐧𝐨 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧!", parse_mode='Markdown')
    except:
        bot.reply_to(message, "𝐔𝐬𝐚𝐠𝐞: /𝐜𝐡𝐞𝐜𝐤𝐬𝐮𝐛 <𝐮𝐬𝐞𝐫_𝐢𝐝>")

# --- Cleanup ---
def cleanup():
    logger.warning("Shutting down... Cleaning up processes...")
    for script_key, script_info in bot_scripts.items():
        try:
            script_info['process'].terminate()
            if 'log_file' in script_info:
                script_info['log_file'].close()
        except:
            pass
    logger.warning("Cleanup completed.")

atexit.register(cleanup)

# --- Main Execution ---
if __name__ == '__main__':
    print("="*60)
    print("🤖 EXR HOSTING BOT STARTING...")
    print(f"📝 Bot Token: {TOKEN[:10]}...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"🛡️ Admin ID: {ADMIN_ID}")
    print(f"📢 Force Subscribe Channel: {FORCE_SUB_CHANNEL_NAME}")
    print("="*60)
    
    keep_alive()
    
    print("🚀 Bot is running! Press Ctrl+C to stop.")
    print("✅ File types supported: .py, .js, .zip")
    print("✅ ZIP files will be extracted and main script will be auto-detected")
    print("="*60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
