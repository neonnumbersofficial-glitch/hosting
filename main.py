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
import json
import logging
import signal
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

# --- Styled Button Names (Direct Unicode) ---
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
BTN_BACK = "🔙 𝐁𝐚𝐜𝐤"
BTN_CHECK_SUB = "✅ 𝐂𝐡𝐞𝐜𝐤 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧"
BTN_JOIN = "📢 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥"
BTN_APPROVE = "✅ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞"
BTN_REJECT = "❌ 𝐑𝐞𝐣𝐞𝐜𝐭"
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
pending_files = {}  # {pending_id: {'user_id': int, 'file_name': str, 'file_path': str, 'file_type': str, 'message_id': int, 'chat_id': int}}

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# --- Force Subscription Check Function ---
def is_subscribed(user_id):
    """Check if user is subscribed to the required channel"""
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
    """Create inline keyboard for force subscription"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(BTN_JOIN, url=FORCE_SUB_CHANNEL),
        types.InlineKeyboardButton(BTN_CHECK_SUB, callback_data='check_subscription_status')
    )
    return markup

# --- Database Setup ---
def init_db():
    """Initialize the database with required tables"""
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
                      file_type TEXT, timestamp TEXT)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
             c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    """Load data from database into memory"""
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"⚠️ Invalid expiry date format for user {user_id}: {expiry}")

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
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subscriptions, {len(admin_ids)} admins.")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

# Initialize DB and Load Data
init_db()
load_data()

# --- Helper Functions ---
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
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
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception as log_e:
                        logger.error(f"Error closing log file: {log_e}")
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                     script_info['log_file'].close()
                except Exception as log_e:
                     logger.error(f"Error closing log file: {log_e}")
            if script_key in bot_scripts:
                 del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Error checking process status: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    """Kill a process and all its children"""
    pid = None
    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
            except Exception as log_e:
                logger.error(f"Error closing log file: {log_e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
           pid = process.pid
           if pid: 
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            try: child.kill()
                            except: pass
                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        try: p.kill()
                        except: pass
                    try:
                        parent.terminate()
                        try: parent.wait(timeout=1)
                        except: parent.kill()
                    except:
                        pass
                except psutil.NoSuchProcess:
                    pass
    except Exception as e:
        logger.error(f"❌ Unexpected error killing process: {e}", exc_info=True)

# --- Database Operations ---
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
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
        except Exception as e:
            logger.error(f"❌ Error saving file: {e}")
        finally:
            conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]:
                    del user_files[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing file: {e}")
        finally:
            conn.close()

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error adding active user: {e}")
        finally:
            conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
        except Exception as e:
            logger.error(f"❌ Error saving subscription: {e}")
        finally:
            conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions:
                del user_subscriptions[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing subscription: {e}")
        finally:
            conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id)
        except Exception as e:
            logger.error(f"❌ Error adding admin: {e}")
        finally:
            conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        return False
    with DB_LOCK:
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
            logger.error(f"❌ Error removing admin: {e}")
            return False
        finally:
            conn.close()

def save_pending_approval(user_id, file_name, file_path, file_type):
    """Save pending approval to database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            timestamp = datetime.now().isoformat()
            c.execute('''INSERT INTO pending_approvals (user_id, file_name, file_path, file_type, timestamp)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, file_name, file_path, file_type, timestamp))
            conn.commit()
            pending_id = c.lastrowid
            return pending_id
        except Exception as e:
            logger.error(f"❌ Error saving pending approval: {e}")
            return None
        finally:
            conn.close()

def remove_pending_approval(pending_id):
    """Remove pending approval from database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error removing pending approval: {e}")
        finally:
            conn.close()

def get_pending_approvals():
    """Get all pending approvals from database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('SELECT pending_id, user_id, file_name, file_type, timestamp FROM pending_approvals ORDER BY timestamp DESC')
            return c.fetchall()
        except Exception as e:
            logger.error(f"❌ Error getting pending approvals: {e}")
            return []
        finally:
            conn.close()

# --- Script Running Functions ---
def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    """Run Python script"""
    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Running Python script: {script_path}")
    
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
        process = subprocess.Popen(
            [sys.executable, script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
            stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
            encoding='utf-8', errors='ignore'
        )
        
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id,
            'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
        }
        
        bot.reply_to(message_obj_for_reply, f"✅ {style_text('Python script')} `{file_name}` {style_text('started!')} (PID: {process.pid})")
        
    except Exception as e:
        if log_file and not log_file.closed:
            log_file.close()
        error_msg = f"❌ {style_text('Error starting script')}: {str(e)}"
        logger.error(error_msg)
        bot.reply_to(message_obj_for_reply, error_msg)

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    """Run JavaScript script"""
    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Running JS script: {script_path}")
    
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
        process = subprocess.Popen(
            ['node', script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
            stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
            encoding='utf-8', errors='ignore'
        )
        
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id,
            'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js', 'script_key': script_key
        }
        
        bot.reply_to(message_obj_for_reply, f"✅ {style_text('JS script')} `{file_name}` {style_text('started!')} (PID: {process.pid})")
        
    except Exception as e:
        if log_file and not log_file.closed:
            log_file.close()
        error_msg = f"❌ {style_text('Error starting JS script')}: {str(e)}"
        logger.error(error_msg)
        bot.reply_to(message_obj_for_reply, error_msg)

# --- Menu Creation ---
def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 𝐒𝐭𝐨𝐩", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 𝐑𝐞𝐬𝐭𝐚𝐫𝐭", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 𝐋𝐨𝐠𝐬", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 𝐒𝐭𝐚𝐫𝐭", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 𝐕𝐢𝐞𝐰 𝐋𝐨𝐠𝐬", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton(BTN_BACK, callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐀𝐝𝐦𝐢𝐧", callback_data='add_admin'),
        types.InlineKeyboardButton("➖ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐀𝐝𝐦𝐢𝐧", callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton("📋 𝐋𝐢𝐬𝐭 𝐀𝐝𝐦𝐢𝐧𝐬", callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton(BTN_BACK, callback_data='back_to_main'))
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧", callback_data='add_subscription'),
        types.InlineKeyboardButton("➖ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧", callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton("🔍 𝐂𝐡𝐞𝐜𝐤 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧", callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton(BTN_BACK, callback_data='back_to_main'))
    return markup

def create_approval_buttons(pending_id):
    """Create inline buttons for approval"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(BTN_APPROVE, callback_data=f'approve_file_{pending_id}'),
        types.InlineKeyboardButton(BTN_REJECT, callback_data=f'reject_file_{pending_id}')
    )
    return markup

# --- File Handling with Approval ---
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    """Handle ZIP file upload - send to admin for approval"""
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        zip_path = os.path.join(temp_dir, file_name_zip)
        
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)
            
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir)):
                    raise zipfile.BadZipFile(f"Zip has unsafe path: {member.filename}")
            zip_ref.extractall(temp_dir)
            
        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        
        main_script_name = None
        file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']
        preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        
        for p in preferred_py:
            if p in py_files:
                main_script_name = p
                file_type = 'py'
                break
        if not main_script_name:
            for p in preferred_js:
                if p in js_files:
                    main_script_name = p
                    file_type = 'js'
                    break
        if not main_script_name:
            if py_files:
                main_script_name = py_files[0]
                file_type = 'py'
            elif js_files:
                main_script_name = js_files[0]
                file_type = 'js'
                
        if not main_script_name:
            bot.reply_to(message, f"❌ {style_text('No .py or .js script found in archive!')}")
            return
            
        # Move files to pending directory
        pending_file_path = os.path.join(PENDING_DIR, f"{user_id}_{int(time.time())}_{main_script_name}")
        shutil.move(zip_path, pending_file_path)
        
        # Save to pending approvals
        pending_id = save_pending_approval(user_id, main_script_name, pending_file_path, file_type)
        
        if pending_id:
            # Notify admins
            admin_msg = (f"📦 {style_text('New File Pending Approval!')}\n\n"
                        f"👤 {style_text('User ID')}: `{user_id}`\n"
                        f"📄 {style_text('File')}: `{main_script_name}`\n"
                        f"📁 {style_text('Type')}: {style_text(file_type.upper())}\n"
                        f"🔄 {style_text('Format')}: {style_text('ZIP Archive')}")
            
            for admin_id in admin_ids:
                try:
                    bot.send_message(admin_id, admin_msg, parse_mode='Markdown')
                    bot.send_document(admin_id, open(pending_file_path, 'rb'), 
                                     caption=f"{style_text('Approve or Reject:')}", 
                                     reply_markup=create_approval_buttons(pending_id))
                except Exception as e:
                    logger.error(f"Error notifying admin {admin_id}: {e}")
                    
            bot.reply_to(message, f"✅ {style_text('File uploaded successfully!')}\n\n"
                        f"⏳ {style_text('Your file is pending approval from admin.')}\n"
                        f"{style_text('You will be notified once approved or rejected.')}")
        else:
            bot.reply_to(message, f"❌ {style_text('Error saving file for approval. Please try again.')}")
            
    except zipfile.BadZipFile as e:
        logger.error(f"Bad zip file from {user_id}: {e}")
        bot.reply_to(message, f"❌ {style_text('Invalid/corrupted ZIP file.')}")
    except Exception as e:
        logger.error(f"❌ Error processing zip for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ {style_text('Error processing zip:')} {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

def handle_single_file(file_content, file_name, file_type, message):
    """Handle single file upload - send to admin for approval"""
    user_id = message.from_user.id
    
    try:
        # Save file to pending directory
        pending_file_path = os.path.join(PENDING_DIR, f"{user_id}_{int(time.time())}_{file_name}")
        with open(pending_file_path, 'wb') as f:
            f.write(file_content)
            
        # Save to pending approvals
        pending_id = save_pending_approval(user_id, file_name, pending_file_path, file_type)
        
        if pending_id:
            # Notify admins
            admin_msg = (f"📄 {style_text('New File Pending Approval!')}\n\n"
                        f"👤 {style_text('User ID')}: `{user_id}`\n"
                        f"📄 {style_text('File')}: `{file_name}`\n"
                        f"📁 {style_text('Type')}: {style_text(file_type.upper())}")
            
            for admin_id in admin_ids:
                try:
                    bot.send_message(admin_id, admin_msg, parse_mode='Markdown')
                    bot.send_document(admin_id, open(pending_file_path, 'rb'),
                                     caption=f"{style_text('Approve or Reject:')}",
                                     reply_markup=create_approval_buttons(pending_id))
                except Exception as e:
                    logger.error(f"Error notifying admin {admin_id}: {e}")
                    
            bot.reply_to(message, f"✅ {style_text('File uploaded successfully!')}\n\n"
                        f"⏳ {style_text('Your file is pending approval from admin.')}\n"
                        f"{style_text('You will be notified once approved or rejected.')}")
        else:
            bot.reply_to(message, f"❌ {style_text('Error saving file for approval. Please try again.')}")
            
    except Exception as e:
        logger.error(f"❌ Error processing file {file_name} for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ {style_text('Error processing file:')} {str(e)}")

def approve_file(pending_id, admin_id):
    """Approve a pending file and host it"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('SELECT user_id, file_name, file_path, file_type FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        result = c.fetchone()
        
        if not result:
            return False, "Pending file not found"
            
        user_id, file_name, temp_path, file_type = result
        
        # Check file limit
        file_limit = get_user_file_limit(user_id)
        current_files = get_user_file_count(user_id)
        
        if current_files >= file_limit:
            limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
            return False, f"User file limit reached ({current_files}/{limit_str})"
        
        # Move file to user folder
        user_folder = get_user_folder(user_id)
        final_path = os.path.join(user_folder, file_name)
        shutil.move(temp_path, final_path)
        
        # Save to user files
        save_user_file(user_id, file_name, file_type)
        
        # Start the script
        message_obj = types.Message()
        message_obj.chat = types.User(id=user_id)
        message_obj.from_user = types.User(id=user_id)
        
        if file_type == 'py':
            threading.Thread(target=run_script, args=(final_path, user_id, user_folder, file_name, message_obj)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(final_path, user_id, user_folder, file_name, message_obj)).start()
        
        # Remove from pending
        c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        conn.commit()
        
        # Notify user
        try:
            bot.send_message(user_id, 
                f"✅ {style_text('Your file has been APPROVED and hosted!')}\n\n"
                f"📄 {style_text('File')}: `{file_name}`\n"
                f"🚀 {style_text('Status')}: {style_text('Running')}")
        except Exception as e:
            logger.error(f"Error notifying user {user_id}: {e}")
        
        # Notify admin
        bot.send_message(admin_id, f"✅ {style_text('File approved and hosted!')}\n📄 `{file_name}`\n👤 User: `{user_id}`", parse_mode='Markdown')
        
        return True, "File approved and hosted successfully"
        
    except Exception as e:
        logger.error(f"Error approving file {pending_id}: {e}")
        return False, str(e)
    finally:
        conn.close()

def reject_file(pending_id, admin_id):
    """Reject a pending file and delete it"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('SELECT user_id, file_name, file_path FROM pending_approvals WHERE pending_id = ?', (pending_id,))
        result = c.fetchone()
        
        if result:
            user_id, file_name, file_path = result
            
            # Delete the file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from database
            c.execute('DELETE FROM pending_approvals WHERE pending_id = ?', (pending_id,))
            conn.commit()
            
            # Notify user
            try:
                bot.send_message(user_id,
                    f"❌ {style_text('Your file has been REJECTED by admin.')}\n\n"
                    f"📄 {style_text('File')}: `{file_name}`\n"
                    f"{style_text('Please contact admin for more information.')}", parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error notifying user {user_id}: {e}")
            
            # Notify admin
            bot.send_message(admin_id, f"❌ {style_text('File rejected and deleted!')}\n📄 `{file_name}`\n👤 User: `{user_id}`", parse_mode='Markdown')
        
        return True
        
    except Exception as e:
        logger.error(f"Error rejecting file {pending_id}: {e}")
        return False
    finally:
        conn.close()

def list_pending_approvals(admin_id):
    """List all pending approvals for admin"""
    pending_list = get_pending_approvals()
    
    if not pending_list:
        bot.send_message(admin_id, f"📭 {style_text('No pending approvals.')}")
        return
    
    msg = f"⏳ {style_text('Pending Approvals')} ({len(pending_list)}):\n\n"
    for pending_id, user_id, file_name, file_type, timestamp in pending_list[:10]:
        msg += f"🆔 {style_text('ID')}: `{pending_id}`\n"
        msg += f"👤 {style_text('User')}: `{user_id}`\n"
        msg += f"📄 {style_text('File')}: `{file_name}`\n"
        msg += f"📁 {style_text('Type')}: {style_text(file_type.upper())}\n"
        msg += f"⏰ {style_text('Time')}: {timestamp[:19]}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(pending_list) > 10:
        msg += f"\n{style_text('And')} {len(pending_list) - 10} {style_text('more...')}"
    
    bot.send_message(admin_id, msg, parse_mode='Markdown')

# --- Logic Functions ---
def get_greeting():
    """Get greeting based on time of day"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "𝐆𝐨𝐨𝐝 𝐌𝐨𝐫𝐧𝐢𝐧𝐠"
    elif 12 <= hour < 17:
        return "𝐆𝐨𝐨𝐝 𝐀𝐟𝐭𝐞𝐫𝐧𝐨𝐨𝐧"
    elif 17 <= hour < 21:
        return "𝐆𝐨𝐨𝐝 𝐄𝐯𝐞𝐧𝐢𝐧𝐠"
    else:
        return "𝐆𝐨𝐨𝐝 𝐍𝐢𝐠𝐡𝐭"

def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username
    
    # Check subscription first
    if not is_subscribed(user_id):
        welcome_msg = (f"╔═══《 🎉 {get_greeting()}! 》═══╗\n\n"
                      f"👤 {style_text('User')}: {user_name}\n"
                      f"🆔 {style_text('User ID')}: `{user_id}`\n\n"
                      f"╰═══════《 🤖 》═══════╝\n\n"
                      f"⚠️ {style_text('You must join our channel to use this bot!')}\n\n"
                      f"📢 {style_text('Channel')}: {FORCE_SUB_CHANNEL_NAME}")
        bot.send_message(chat_id, welcome_msg, parse_mode='Markdown', reply_markup=force_subscribe_markup())
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, f"⚠️ {style_text('Bot locked by admin. Try later.')}")
        return
    
    if user_id not in active_users:
        add_active_user(user_id)
        try:
            owner_notification = (f"🎉 {style_text('New user!')}\n"
                                 f"👤 {style_text('Name')}: {user_name}\n"
                                 f"✳️ {style_text('User')}: @{user_username or 'N/A'}\n"
                                 f"🆔 {style_text('ID')}: `{user_id}`")
            bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to notify owner: {e}")
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝"
    
    # Determine user status
    if user_id == OWNER_ID:
        user_status = "𝐎𝐰𝐧𝐞𝐫"
        status_icon = "👑"
    elif user_id in admin_ids:
        user_status = "𝐀𝐝𝐦𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐭𝐨𝐫"
        status_icon = "🛡️"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            days_left = (expiry_date - datetime.now()).days
            user_status = f"𝐏𝐫𝐞𝐦𝐢𝐮𝐦 (𝐄𝐱𝐩𝐢𝐫𝐞𝐬 𝐢𝐧 {days_left} 𝐝𝐚𝐲𝐬)"
            status_icon = "⭐"
        else:
            user_status = "𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫 (𝐄𝐱𝐩𝐢𝐫𝐞𝐝)"
            status_icon = "🆓"
            remove_subscription_db(user_id)
    else:
        user_status = "𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫"
        status_icon = "🆓"
    
    welcome_msg = (f"╔═══《 🎉 {get_greeting()}! 》═══╗\n\n"
                  f"👤 {style_text('User')}: {user_name}\n"
                  f"🆔 {style_text('User ID')}: `{user_id}`\n"
                  f"{status_icon} {style_text('Status')}: {user_status}\n\n"
                  f"╰═══════《 🤖 》═══════╝\n\n"
                  f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐄𝐗𝐑 𝐄𝐗𝐔 | 𝐗𝐒𝐔\n\n"
                  f"📌 {style_text('About This Bot')}:\n"
                  f"• 🔐 {style_text('Secure File Host')}\n"
                  f"• 📊 {style_text('ZIP & Script Hosting')}\n"
                  f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                  f"✅ {style_text('Access Granted!')}\n"
                  f"{style_text('You have successfully joined')} {FORCE_SUB_CHANNEL_NAME}\n\n"
                  f"📌 {style_text('Quick Guide')}:\n"
                  f"• {style_text('Use menu buttons to navigate')}\n"
                  f"• /{style_text('help for more information')}\n"
                  f"• 📁 {style_text('My Files to view accessed files')}\n\n"
                  f"⚠️ {style_text('Note')}: {style_text('If you leave any channel/group, you will lose access immediately!')}")
    
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    bot.send_message(chat_id, welcome_msg, reply_markup=main_reply_markup, parse_mode='Markdown')

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(BTN_UPDATES, url=UPDATE_CHANNEL))
    bot.reply_to(message, f"{style_text('Visit our Updates Channel:')}", reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        bot.reply_to(message, f"⚠️ {style_text('Please join our channel first!')}", reply_markup=force_subscribe_markup())
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Bot locked by admin, cannot accept files.')}")
        return
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝"
        bot.reply_to(message, f"⚠️ {style_text('File limit')} ({current_files}/{limit_str}) {style_text('reached. Delete files first.')}")
        return
    
    bot.reply_to(message, f"📤 {style_text('Send your Python')} (`.py`), {style_text('JS')} (`.js`), {style_text('or ZIP')} (`.zip`) {style_text('file.')}\n\n{style_text('File will be sent to admin for approval before hosting.')}")

def _logic_check_files(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        bot.reply_to(message, f"⚠️ {style_text('Please join our channel first!')}", reply_markup=force_subscribe_markup())
        return
    
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, f"📂 {style_text('Your files:')}\n\n{style_text('(No files uploaded yet)')}")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢" if is_running else "🔴"
        status_text = style_text("Running") if is_running else style_text("Stopped")
        btn_text = f"{file_name} ({file_type}) - {status_icon} {status_text}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, f"📂 {style_text('Your files:')}\n{style_text('Click to manage.')}", reply_markup=markup, parse_mode='Markdown')

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not is_subscribed(user_id):
        bot.reply_to(message, f"⚠️ {style_text('Please join our channel first!')}", reply_markup=force_subscribe_markup())
        return
    
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, f"🏃 {style_text('Testing speed...')}")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🔓 𝐔𝐧𝐥𝐨𝐜𝐤𝐞𝐝" if not bot_locked else "🔒 𝐋𝐨𝐜𝐤𝐞𝐝"
        
        if user_id == OWNER_ID:
            user_level = "👑 𝐎𝐰𝐧𝐞𝐫"
        elif user_id in admin_ids:
            user_level = "🛡️ 𝐀𝐝𝐦𝐢𝐧"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "⭐ 𝐏𝐫𝐞𝐦𝐢𝐮𝐦"
        else:
            user_level = "🆓 𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫"
            
        speed_msg = (f"⚡ {style_text('Bot Speed & Status:')}\n\n"
                    f"⏱️ {style_text('API Response Time')}: {response_time} ms\n"
                    f"🚦 {style_text('Bot Status')}: {status}\n"
                    f"👤 {style_text('Your Level')}: {user_level}")
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id)
    except Exception as e:
        logger.error(f"Error during speed test: {e}")
        bot.edit_message_text(f"❌ {style_text('Error during speed test.')}", chat_id, wait_msg.message_id)

def _logic_statistics(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id) and user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Please join our channel first!')}", reply_markup=force_subscribe_markup())
        return
    
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())
    
    running_bots_count = 0
    user_running_bots = 0
    
    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots += 1
    
    pending_count = len(get_pending_approvals())
    
    stats_msg = (f"📊 {style_text('Bot Statistics:')}\n\n"
                f"👥 {style_text('Total Users')}: {total_users}\n"
                f"📂 {style_text('Total File Records')}: {total_files_records}\n"
                f"🟢 {style_text('Total Active Bots')}: {running_bots_count}\n"
                f"⏳ {style_text('Pending Approvals')}: {pending_count}\n"
                f"🤖 {style_text('Your Running Bots')}: {user_running_bots}")
    
    if user_id in admin_ids:
        stats_msg += f"\n🔒 {style_text('Bot Status')}: {'🔴 𝐋𝐨𝐜𝐤𝐞𝐝' if bot_locked else '🟢 𝐔𝐧𝐥𝐨𝐜𝐤𝐞𝐝'}"
    
    bot.reply_to(message, stats_msg)

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(BTN_CONTACT, url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, f"{style_text('Click to contact Owner:')}", reply_markup=markup)

def _logic_pending_approvals(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Admin permissions required.')}")
        return
    list_pending_approvals(user_id)

def _logic_subscriptions_panel(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Admin permissions required.')}")
        return
    bot.reply_to(message, f"💳 {style_text('Subscription Management')}\n{style_text('Use inline buttons to manage.')}", reply_markup=create_subscription_menu())

def _logic_broadcast_init(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Admin permissions required.')}")
        return
    msg = bot.reply_to(message, f"📢 {style_text('Send message to broadcast to all active users.')}\n/{style_text('cancel to abort.')}")
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Admin permissions required.')}")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "locked" if bot_locked else "unlocked"
    logger.warning(f"Bot {status} by Admin {user_id}")
    bot.reply_to(message, f"🔒 {style_text('Bot has been')} {style_text(status)}.")

def _logic_admin_panel(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Admin permissions required.')}")
        return
    bot.reply_to(message, f"👑 {style_text('Admin Panel')}\n{style_text('Manage admins.')}", reply_markup=create_admin_panel())

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
    else:
        return
    
    if admin_user_id not in admin_ids:
        reply_func(f"⚠️ {style_text('Admin permissions required.')}")
        return
    
    reply_func(f"⏳ {style_text('Starting process to run all user scripts...')}")
    logger.info(f"Admin {admin_user_id} initiated 'run all scripts'")
    
    started_count = 0
    attempted_users = 0
    
    all_user_files_snapshot = dict(user_files)
    
    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user:
            continue
        attempted_users += 1
        user_folder = get_user_folder(target_user_id)
        
        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, target_user_id, user_folder, file_name, message_or_call)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, target_user_id, user_folder, file_name, message_or_call)).start()
                            started_count += 1
                        time.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Error starting {file_name}: {e}")
    
    summary_msg = (f"✅ {style_text('All Users Scripts - Processing Complete:')}\n\n"
                  f"▶️ {style_text('Started')}: {started_count} {style_text('scripts')}\n"
                  f"👥 {style_text('Users processed')}: {attempted_users}")
    reply_func(summary_msg)

# --- Broadcast Functions ---
def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Not authorized.')}")
        return
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Broadcast cancelled.')}")
        return
    
    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video):
        bot.reply_to(message, f"⚠️ {style_text('Cannot broadcast empty message.')}")
        return
    
    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ 𝐂𝐨𝐧𝐟𝐢𝐫𝐦 & 𝐒𝐞𝐧𝐝", callback_data=f"confirm_broadcast_{message.message_id}"),
        types.InlineKeyboardButton("❌ 𝐂𝐚𝐧𝐜𝐞𝐥", callback_data="cancel_broadcast")
    )
    
    preview_text = broadcast_content[:500].strip() if broadcast_content else "(Media message)"
    bot.reply_to(message, f"⚠️ {style_text('Confirm Broadcast:')}\n\n```\n{preview_text}\n```\n"
                          f"{style_text('To')} **{target_count}** {style_text('users. Sure?')}", 
                          reply_markup=markup, parse_mode='Markdown')

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0
    failed_count = 0
    users_to_broadcast = list(active_users)
    
    for user_id_bc in users_to_broadcast:
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            failed_count += 1
        time.sleep(0.05)
    
    result_msg = (f"📢 {style_text('Broadcast Complete!')}\n\n"
                 f"✅ {style_text('Sent')}: {sent_count}\n"
                 f"❌ {style_text('Failed')}: {failed_count}\n"
                 f"👥 {style_text('Targets')}: {len(users_to_broadcast)}")
    bot.send_message(admin_chat_id, result_msg)

# --- Command Handlers ---
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    _logic_send_welcome(message)

@bot.message_handler(func=lambda message: message.text == BTN_UPDATES)
def button_updates(message):
    _logic_updates_channel(message)

@bot.message_handler(func=lambda message: message.text == BTN_UPLOAD)
def button_upload(message):
    _logic_upload_file(message)

@bot.message_handler(func=lambda message: message.text == BTN_CHECK)
def button_check(message):
    _logic_check_files(message)

@bot.message_handler(func=lambda message: message.text == BTN_SPEED)
def button_speed(message):
    _logic_bot_speed(message)

@bot.message_handler(func=lambda message: message.text == BTN_STATS)
def button_stats(message):
    _logic_statistics(message)

@bot.message_handler(func=lambda message: message.text == BTN_CONTACT)
def button_contact(message):
    _logic_contact_owner(message)

@bot.message_handler(func=lambda message: message.text == BTN_SUBS)
def button_subs(message):
    _logic_subscriptions_panel(message)

@bot.message_handler(func=lambda message: message.text == BTN_BROADCAST)
def button_broadcast(message):
    _logic_broadcast_init(message)

@bot.message_handler(func=lambda message: message.text == BTN_LOCK)
def button_lock(message):
    _logic_toggle_lock_bot(message)

@bot.message_handler(func=lambda message: message.text == BTN_RUN_ALL)
def button_run_all(message):
    _logic_run_all_scripts(message)

@bot.message_handler(func=lambda message: message.text == BTN_ADMIN)
def button_admin(message):
    _logic_admin_panel(message)

@bot.message_handler(func=lambda message: message.text == BTN_PENDING)
def button_pending(message):
    _logic_pending_approvals(message)

# --- Document Handler with Approval ---
@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        bot.reply_to(message, f"⚠️ {style_text('Please join our channel first!')}", reply_markup=force_subscribe_markup())
        return
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Bot locked, cannot accept files.')}")
        return
    
    doc = message.document
    file_name = doc.file_name
    
    if not file_name:
        bot.reply_to(message, f"⚠️ {style_text('No file name.')}")
        return
    
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, f"⚠️ {style_text('Unsupported type! Only')} `.py`, `.js`, `.zip` {style_text('allowed.')}")
        return
    
    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        bot.reply_to(message, f"⚠️ {style_text('File too large (Max: 20 MB).')}")
        return
    
    try:
        download_wait_msg = bot.reply_to(message, f"⏳ {style_text('Downloading')} `{file_name}`...")
        file_info = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info.file_path)
        bot.edit_message_text(f"✅ {style_text('Downloaded')} `{file_name}`. {style_text('Sending for approval...')}", 
                             message.chat.id, download_wait_msg.message_id)
        
        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_type = 'py' if file_ext == '.py' else 'js'
            handle_single_file(downloaded_file_content, file_name, file_type, message)
            
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        bot.reply_to(message, f"❌ {style_text('Error processing file:')} {str(e)}")

# --- Callback Query Handlers ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    # Check subscription for non-admin users
    if not is_subscribed(user_id) and user_id not in admin_ids and data not in ['check_subscription_status', 'back_to_main']:
        bot.answer_callback_query(call.id, f"⚠️ {style_text('Please join our channel first!')}", show_alert=True)
        return
    
    try:
        # Force subscription check
        if data == 'check_subscription_status':
            if is_subscribed(user_id):
                bot.answer_callback_query(call.id, f"✅ {style_text('You are subscribed! You can now use the bot.')}")
                _logic_send_welcome(call.message)
            else:
                bot.answer_callback_query(call.id, f"❌ {style_text('You are not subscribed yet. Please join the channel first.')}", show_alert=True)
            return
        
        # Approval callbacks
        if data.startswith('approve_file_'):
            pending_id = int(data.split('_')[2])
            success, msg = approve_file(pending_id, user_id)
            bot.answer_callback_query(call.id, msg)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
            
        if data.startswith('reject_file_'):
            pending_id = int(data.split('_')[2])
            success = reject_file(pending_id, user_id)
            bot.answer_callback_query(call.id, f"❌ {style_text('File rejected')}" if success else f"❌ {style_text('Error rejecting file')}")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
        
        # File management callbacks
        if data.startswith('file_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('You can only manage your own files.')}", show_alert=True)
                return
            
            is_running = is_bot_running(script_owner_id, file_name)
            status_text = '🟢 Running' if is_running else '🔴 Stopped'
            file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), '?')
            
            try:
                bot.edit_message_text(
                    f"⚙️ {style_text('Controls for')}: `{file_name}` ({file_type})\n{style_text('Status')}: {status_text}",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message: {e}")
            bot.answer_callback_query(call.id)
            return
        
        # Start, Stop, Restart, Delete, Logs callbacks
        if data.startswith('start_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Permission denied')}", show_alert=True)
                return
            
            user_folder = get_user_folder(script_owner_id)
            file_path = os.path.join(user_folder, file_name)
            file_info = next((f for f in user_files.get(script_owner_id, []) if f[0] == file_name), None)
            
            if not file_info or not os.path.exists(file_path):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('File not found')}", show_alert=True)
                return
            
            bot.answer_callback_query(call.id, f"⏳ {style_text('Starting script...')}")
            
            if file_info[1] == 'py':
                threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            else:
                threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            
            time.sleep(1)
            is_now_running = is_bot_running(script_owner_id, file_name)
            status_text = '🟢 Running' if is_now_running else '🟡 Starting...'
            
            try:
                bot.edit_message_text(
                    f"⚙️ {style_text('Controls for')}: `{file_name}`\n{style_text('Status')}: {status_text}",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running),
                    parse_mode='Markdown'
                )
            except:
                pass
            return
        
        if data.startswith('stop_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Permission denied')}", show_alert=True)
                return
            
            script_key = f"{script_owner_id}_{file_name}"
            
            if is_bot_running(script_owner_id, file_name):
                process_info = bot_scripts.get(script_key)
                if process_info:
                    kill_process_tree(process_info)
                    if script_key in bot_scripts:
                        del bot_scripts[script_key]
                bot.answer_callback_query(call.id, f"🛑 {style_text('Script stopped')}")
            else:
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Script not running')}")
            
            try:
                bot.edit_message_text(
                    f"⚙️ {style_text('Controls for')}: `{file_name}`\n{style_text('Status')}: 🔴 {style_text('Stopped')}",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, False),
                    parse_mode='Markdown'
                )
            except:
                pass
            return
        
        if data.startswith('restart_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Permission denied')}", show_alert=True)
                return
            
            script_key = f"{script_owner_id}_{file_name}"
            
            if is_bot_running(script_owner_id, file_name):
                process_info = bot_scripts.get(script_key)
                if process_info:
                    kill_process_tree(process_info)
                    if script_key in bot_scripts:
                        del bot_scripts[script_key]
                time.sleep(1)
            
            user_folder = get_user_folder(script_owner_id)
            file_path = os.path.join(user_folder, file_name)
            file_info = next((f for f in user_files.get(script_owner_id, []) if f[0] == file_name), None)
            
            bot.answer_callback_query(call.id, f"🔄 {style_text('Restarting script...')}")
            
            if file_info and file_info[1] == 'py':
                threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            elif file_info:
                threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            
            time.sleep(1)
            is_now_running = is_bot_running(script_owner_id, file_name)
            status_text = '🟢 Running' if is_now_running else '🟡 Starting...'
            
            try:
                bot.edit_message_text(
                    f"⚙️ {style_text('Controls for')}: `{file_name}`\n{style_text('Status')}: {status_text}",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running),
                    parse_mode='Markdown'
                )
            except:
                pass
            return
        
        if data.startswith('delete_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Permission denied')}", show_alert=True)
                return
            
            script_key = f"{script_owner_id}_{file_name}"
            
            if is_bot_running(script_owner_id, file_name):
                process_info = bot_scripts.get(script_key)
                if process_info:
                    kill_process_tree(process_info)
                    if script_key in bot_scripts:
                        del bot_scripts[script_key]
                time.sleep(0.5)
            
            user_folder = get_user_folder(script_owner_id)
            file_path = os.path.join(user_folder, file_name)
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(log_path):
                os.remove(log_path)
            
            remove_user_file_db(script_owner_id, file_name)
            
            bot.answer_callback_query(call.id, f"🗑️ {style_text('File deleted')}")
            
            try:
                bot.edit_message_text(
                    f"🗑️ {style_text('File')} `{file_name}` {style_text('deleted successfully!')}",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=None,
                    parse_mode='Markdown'
                )
            except:
                pass
            return
        
        if data.startswith('logs_'):
            _, script_owner_id_str, file_name = data.split('_', 2)
            script_owner_id = int(script_owner_id_str)
            
            if not (user_id == script_owner_id or user_id in admin_ids):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Permission denied')}", show_alert=True)
                return
            
            user_folder = get_user_folder(script_owner_id)
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            
            if not os.path.exists(log_path):
                bot.answer_callback_query(call.id, f"⚠️ {style_text('No logs found')}", show_alert=True)
                return
            
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                
                max_tg_msg = 4096
                if len(log_content) > max_tg_msg:
                    log_content = log_content[-max_tg_msg:]
                    log_content = "...\n" + log_content
                
                if not log_content.strip():
                    log_content = "(Empty log)"
                
                bot.send_message(call.message.chat.id, 
                               f"📜 {style_text('Logs for')} `{file_name}`:\n```\n{log_content}\n```",
                               parse_mode='Markdown')
                bot.answer_callback_query(call.id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ {style_text('Error reading logs')}", show_alert=True)
            return
        
        # Other callbacks
        if data == 'back_to_main':
            _logic_send_welcome(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'check_files':
            _logic_check_files(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'speed':
            _logic_bot_speed(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'stats':
            _logic_statistics(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'lock_bot':
            global bot_locked
            bot_locked = True
            bot.answer_callback_query(call.id, f"🔒 {style_text('Bot locked')}")
            return
        
        if data == 'unlock_bot':
            bot_locked = False
            bot.answer_callback_query(call.id, f"🔓 {style_text('Bot unlocked')}")
            return
        
        if data == 'run_all_scripts':
            _logic_run_all_scripts(call)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'broadcast':
            _logic_broadcast_init(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'admin_panel':
            _logic_admin_panel(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'subscription':
            _logic_subscriptions_panel(call.message)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'confirm_broadcast':
            handle_confirm_broadcast(call)
            return
        
        if data == 'cancel_broadcast':
            bot.answer_callback_query(call.id, f"{style_text('Broadcast cancelled.')}")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
        
        # Admin management callbacks
        if data == 'add_admin':
            if user_id != OWNER_ID:
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Owner only')}", show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, f"👑 {style_text('Enter User ID to promote to Admin.')}\n/{style_text('cancel to abort.')}")
            bot.register_next_step_handler(msg, process_add_admin_id)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'remove_admin':
            if user_id != OWNER_ID:
                bot.answer_callback_query(call.id, f"⚠️ {style_text('Owner only')}", show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, f"👑 {style_text('Enter User ID of Admin to remove.')}\n/{style_text('cancel to abort.')}")
            bot.register_next_step_handler(msg, process_remove_admin_id)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'list_admins':
            admin_list_str = "\n".join(f"- `{aid}` {'(Owner)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
            bot.send_message(call.message.chat.id, f"👑 {style_text('Current Admins:')}\n\n{admin_list_str}", parse_mode='Markdown')
            bot.answer_callback_query(call.id)
            return
        
        # Subscription management callbacks
        if data == 'add_subscription':
            msg = bot.send_message(call.message.chat.id, f"💳 {style_text('Enter User ID & days')} ({style_text('e.g., 12345678 30')}).\n/{style_text('cancel to abort.')}")
            bot.register_next_step_handler(msg, process_add_subscription)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'remove_subscription':
            msg = bot.send_message(call.message.chat.id, f"💳 {style_text('Enter User ID to remove subscription.')}\n/{style_text('cancel to abort.')}")
            bot.register_next_step_handler(msg, process_remove_subscription)
            bot.answer_callback_query(call.id)
            return
        
        if data == 'check_subscription':
            msg = bot.send_message(call.message.chat.id, f"💳 {style_text('Enter User ID to check subscription.')}\n/{style_text('cancel to abort.')}")
            bot.register_next_step_handler(msg, process_check_subscription)
            bot.answer_callback_query(call.id)
            return
        
        bot.answer_callback_query(call.id, f"⚠️ {style_text('Unknown action')}")
        
    except Exception as e:
        logger.error(f"Error handling callback: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, f"❌ {style_text('Error processing request')}", show_alert=True)
        except:
            pass

# --- Admin Management Functions ---
def process_add_admin_id(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, f"⚠️ {style_text('Owner only.')}")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Admin promotion cancelled.')}")
        return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0:
            raise ValueError
        if new_admin_id == OWNER_ID:
            bot.reply_to(message, f"⚠️ {style_text('Owner is already Owner.')}")
            return
        if new_admin_id in admin_ids:
            bot.reply_to(message, f"⚠️ {style_text('User already Admin.')}")
            return
        add_admin_db(new_admin_id)
        bot.reply_to(message, f"✅ {style_text('User promoted to Admin.')}")
        try:
            bot.send_message(new_admin_id, f"🎉 {style_text('You are now an Admin!')}")
        except:
            pass
    except ValueError:
        bot.reply_to(message, f"⚠️ {style_text('Invalid ID. Send numerical ID.')}")

def process_remove_admin_id(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, f"⚠️ {style_text('Owner only.')}")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Admin removal cancelled.')}")
        return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove <= 0:
            raise ValueError
        if admin_id_remove == OWNER_ID:
            bot.reply_to(message, f"⚠️ {style_text('Owner cannot remove self.')}")
            return
        if admin_id_remove not in admin_ids:
            bot.reply_to(message, f"⚠️ {style_text('User not Admin.')}")
            return
        if remove_admin_db(admin_id_remove):
            bot.reply_to(message, f"✅ {style_text('Admin removed.')}")
            try:
                bot.send_message(admin_id_remove, f"ℹ️ {style_text('You are no longer an Admin.')}")
            except:
                pass
        else:
            bot.reply_to(message, f"❌ {style_text('Failed to remove admin.')}")
    except ValueError:
        bot.reply_to(message, f"⚠️ {style_text('Invalid ID.')}")

# --- Subscription Management Functions ---
def process_add_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Not authorized.')}")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Subscription add cancelled.')}")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError
        sub_user_id = int(parts[0].strip())
        days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0:
            raise ValueError
        
        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date = datetime.now()
        if current_expiry and current_expiry > start_date:
            start_date = current_expiry
        new_expiry = start_date + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)
        
        bot.reply_to(message, f"✅ {style_text('Subscription added for')} `{sub_user_id}`\n{style_text('Expires')}: {new_expiry.strftime('%Y-%m-%d')}")
        try:
            bot.send_message(sub_user_id, f"🎉 {style_text('Your subscription has been activated/extended by')} {days} {style_text('days!')}\n{style_text('Expires')}: {new_expiry.strftime('%Y-%m-%d')}")
        except:
            pass
    except ValueError:
        bot.reply_to(message, f"⚠️ {style_text('Invalid format. Use: ID days')}")

def process_remove_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Not authorized.')}")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Subscription removal cancelled.')}")
        return
    try:
        sub_user_id = int(message.text.strip())
        if sub_user_id <= 0:
            raise ValueError
        if sub_user_id not in user_subscriptions:
            bot.reply_to(message, f"⚠️ {style_text('User has no active subscription.')}")
            return
        remove_subscription_db(sub_user_id)
        bot.reply_to(message, f"✅ {style_text('Subscription removed for')} `{sub_user_id}`")
        try:
            bot.send_message(sub_user_id, f"ℹ️ {style_text('Your subscription has been removed by admin.')}")
        except:
            pass
    except ValueError:
        bot.reply_to(message, f"⚠️ {style_text('Invalid ID.')}")

def process_check_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, f"⚠️ {style_text('Not authorized.')}")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, f"{style_text('Subscription check cancelled.')}")
        return
    try:
        sub_user_id = int(message.text.strip())
        if sub_user_id <= 0:
            raise ValueError
        if sub_user_id in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    bot.reply_to(message, f"✅ {style_text('User')} `{sub_user_id}` {style_text('has active subscription.')}\n{style_text('Expires')}: {expiry_dt.strftime('%Y-%m-%d %H:%M:%S')} ({days_left} {style_text('days left')})")
                else:
                    bot.reply_to(message, f"⚠️ {style_text('User')} `{sub_user_id}` {style_text('has expired subscription.')}\n{style_text('Expired on')}: {expiry_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    remove_subscription_db(sub_user_id)
            else:
                bot.reply_to(message, f"⚠️ {style_text('User in subscription list but expiry missing.')}")
        else:
            bot.reply_to(message, f"ℹ️ {style_text('User')} `{sub_user_id}` {style_text('has no active subscription.')}")
    except ValueError:
        bot.reply_to(message, f"⚠️ {style_text('Invalid ID.')}")

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    if user_id not in admin_ids:
        bot.answer_callback_query(call.id, f"⚠️ {style_text('Admin only.')}", show_alert=True)
        return
    try:
        original_message = call.message.reply_to_message
        if not original_message:
            raise ValueError("Could not retrieve original message.")
        
        broadcast_text = original_message.text if original_message.text else None
        broadcast_photo_id = original_message.photo[-1].file_id if original_message.photo else None
        broadcast_video_id = original_message.video.file_id if original_message.video else None
        caption = original_message.caption if (broadcast_photo_id or broadcast_video_id) else None
        
        bot.answer_callback_query(call.id, f"🚀 {style_text('Starting broadcast...')}")
        bot.edit_message_text(f"📢 {style_text('Broadcasting to')} {len(active_users)} {style_text('users...')}",
                             call.message.chat.id, call.message.message_id, reply_markup=None)
        
        thread = threading.Thread(target=execute_broadcast, args=(broadcast_text, broadcast_photo_id, broadcast_video_id, caption, call.message.chat.id))
        thread.start()
    except Exception as e:
        logger.error(f"Error in broadcast confirm: {e}")
        bot.edit_message_text(f"❌ {style_text('Error starting broadcast')}", call.message.chat.id, call.message.message_id)

# --- Cleanup Function ---
def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    script_keys_to_stop = list(bot_scripts.keys())
    for key in script_keys_to_stop:
        if key in bot_scripts:
            kill_process_tree(bot_scripts[key])
    logger.warning("Cleanup finished.")

atexit.register(cleanup)

# --- Main Execution ---
if __name__ == '__main__':
    logger.info("="*40 + "\n🤖 Bot Starting Up...\n" + "="*40)
    keep_alive()
    logger.info("🚀 Starting polling...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            logger.warning("Polling ReadTimeout. Restarting in 5s...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"Polling ConnectionError: {ce}. Retrying in 15s...")
            time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable polling error: {e}", exc_info=True)
            logger.info("Restarting polling in 30s...")
            time.sleep(30)
