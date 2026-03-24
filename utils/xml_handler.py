# =============================================================================
#  xml_handler.py
#  Purpose : All XML read/write operations for the application.
#            Manages two XML files:
#              storage/users.xml       — registered user accounts
#              storage/login_logs.xml  — login/logout activity log
#  Used by : services/auth_service.py, ui/dashboard_ui.py
# =============================================================================

import xml.etree.ElementTree as ET     # Standard-library XML parser/writer
import os                               # File/directory existence checks
from datetime import datetime           # Timestamp generation


#  File paths (relative to project root where main.py is run from)
USERS_FILE = "storage/users.xml"
LOGS_FILE  = "storage/login_logs.xml"


def _ensure_dir():
    """Create the storage/ directory if it doesn't already exist."""
    os.makedirs("storage", exist_ok=True)

    
def _write_empty(path, root_tag):
    """
    Write a valid, non-empty XML file with a single root element.
    Uses encoding + xml_declaration so the file is never 0 bytes.
    """
    tree = ET.ElementTree(ET.Element(root_tag))
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


# =============================================================================
#  init_xml()
#  Called once at application startup.
#  Creates both XML files with their root elements if they don't exist
#  OR if they're empty/corrupted.
# =============================================================================
def init_xml():
    _ensure_dir()
 
    # Create or fix users.xml
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        _write_empty(USERS_FILE, "users")
 
    # Create or fix login_logs.xml
    if not os.path.exists(LOGS_FILE) or os.path.getsize(LOGS_FILE) == 0:
        _write_empty(LOGS_FILE, "logins")


# =============================================================================
#  safe_parse(file_path)
#  Safely parse an XML file, recreating it if it's empty or corrupted.
# =============================================================================
def safe_parse(file_path, default_root_tag):
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tree = ET.parse(file_path)
            return tree.getroot()
        else:
            # File doesn't exist or is empty - create fresh
            root = ET.Element(default_root_tag)
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            return root
    except (ET.ParseError, FileNotFoundError):
        # File is corrupted - recreate it
        root = ET.Element(default_root_tag)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        return root


# =============================================================================
#  read_users()
#  Parse users.xml and return the root <users> element.
#  Callers can iterate root.findall("user") to loop through every account.
# =============================================================================
def read_users():
    try:
        return ET.parse(USERS_FILE).getroot()
    except ET.ParseError:
        # File is corrupt — rebuild it and return an empty root element
        _write_empty(USERS_FILE, "users")
        return ET.Element("users")


# =============================================================================
#  add_user(username, password_hash)
#  Append a new <user> block to users.xml.
#  Structure written:
#    <user>
#      <username>alice</username>
#      <password>sha256hex...</password>
#      <created>2026-03-14 10:22</created>
#    </user>
# =============================================================================
# def add_user(username, password_hash):
    
#     # Ensure file exists and is valid first
#     init_xml()
    
#     tree = ET.parse(USERS_FILE)
#     root = tree.getroot()

#     # Count existing users
#     user_count = len(root) + 1

#     # Create dynamic tag (user1, user2...)
#     user = ET.SubElement(root, f"user{user_count}")

#     ET.SubElement(user, "username").text = username
#     ET.SubElement(user, "password").text = password_hash
#     ET.SubElement(user, "created").text  = datetime.now().strftime("%Y-%m-%d %H:%M")

#     ET.indent(tree, space="    ", level=0)
#     tree.write(USERS_FILE, encoding="utf-8", xml_declaration=True)

def add_user(username, password_hash):
    """
    Append a new <user> block to users.xml.
 
    XML written:
        <user>
            <username>alice</username>
            <password>sha256hex…</password>
            <created>2026-03-14 10:22</created>
        </user>
    """
    tree = ET.parse(USERS_FILE)
    root = tree.getroot()
 
    #  FIXED: use the constant tag name "user" (was f"user{user_count}")
    user = ET.SubElement(root, "user")
    ET.SubElement(user, "username").text = username
    ET.SubElement(user, "password").text = password_hash
    ET.SubElement(user, "created").text  = datetime.now().strftime("%Y-%m-%d %H:%M")
 
    ET.indent(tree, space="    ")
    tree.write(USERS_FILE, encoding="utf-8", xml_declaration=True)
 
# =============================================================================
#  user_exists(username) -> bool
#  Scan users.xml for a matching <username> element.
#  Used by register_user() to prevent duplicate registrations.
# =============================================================================
def user_exists(username):
    username = username.strip().lower()
    
    for u in read_users().findall("user"):
        uname = u.find("username")
        if uname is not None and uname.text == username:
            return True
    return False


# =============================================================================
#  get_all_users() -> list[dict]
#  Build enriched user records by joining users.xml with login_logs.xml.
#  Each returned dict contains:
#    username     : str  — account name
#    created      : str  — registration timestamp (or "N/A" for legacy accounts)
#    total_logins : int  — how many times this user has logged in
#    last_login   : str  — most recent login timestamp, or "Never"
#  Used by the dashboard table and the pie chart.
# =============================================================================
def get_all_users():
    root   = read_users()
    logs   = read_logs()
    result = []
 
    for u in root.findall("user"):          # "user" matches fixed tag name
        uname   = u.find("username").text
        created = u.find("created").text if u.find("created") is not None else "N/A"
 
        user_logs    = [l for l in logs.findall("login")
                        if l.find("username") is not None
                        and l.find("username").text == uname]
        total_logins = len(user_logs)
        times        = [l.find("login_time").text for l in user_logs
                        if l.find("login_time") is not None and l.find("login_time").text]
        last_login   = sorted(times)[-1][:16] if times else "Never"
 
        result.append({
            "username":     uname,
            "created":      created,
            "total_logins": total_logins,
            "last_login":   last_login,
        })
    return result


# =============================================================================
#  read_logs() -> Element
#  Parse login_logs.xml and return the root <logins> element.
#  Returns an empty <logins> element if the file doesn't exist yet.
# =============================================================================
def read_logs():
    if not os.path.exists(LOGS_FILE) or os.path.getsize(LOGS_FILE) == 0:
        return ET.Element("logins")
    try:
        return ET.parse(LOGS_FILE).getroot()
    except ET.ParseError:
        return ET.Element("logins")


# =============================================================================
#  log_login(username) -> str
#  Record the start of a login session in login_logs.xml.
#  Structure written:
#    <login>
#      <id>3</id>
#      <username>alice</username>
#      <login_time>2026-03-14 10:22:05</login_time>
#      <logout_time></logout_time>      ← filled in by log_logout()
#      <duration_min></duration_min>    ← filled in by log_logout()
#    </login>
#  Returns the entry_id (string) so the dashboard can pass it to log_logout().
# =============================================================================
def log_login(username):
    _ensure_dir()
    if not os.path.exists(LOGS_FILE) or os.path.getsize(LOGS_FILE) == 0:
        _write_empty(LOGS_FILE, "logins")
 
    tree     = ET.parse(LOGS_FILE)
    root     = tree.getroot()
    entry_id = str(len(root.findall("login")))
 
    entry = ET.SubElement(root, "login")
    ET.SubElement(entry, "id").text           = entry_id
    ET.SubElement(entry, "username").text     = username
    ET.SubElement(entry, "login_time").text   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(entry, "logout_time").text  = ""   # filled by log_logout()
    ET.SubElement(entry, "duration_min").text = ""   # filled by log_logout()
 
    ET.indent(tree, space="    ")
    tree.write(LOGS_FILE, encoding="utf-8", xml_declaration=True)
    return entry_id
 

# =============================================================================
#  log_logout(entry_id, login_time_str)
#  Fill in logout_time and duration_min for an existing log entry.
#  Called by DashboardWindow._logout() and DashboardWindow.closeEvent().
#  If the entry_id is not found (edge case), the function exits silently.
# =============================================================================
def log_logout(entry_id, login_time_str):
    if not os.path.exists(LOGS_FILE) or os.path.getsize(LOGS_FILE) == 0:
        return
    try:
        tree = ET.parse(LOGS_FILE)
    except ET.ParseError:
        return
 
    root = tree.getroot()
    for entry in root.findall("login"):
        eid = entry.find("id")
        if eid is not None and eid.text == str(entry_id):
            now = datetime.now()
            entry.find("logout_time").text = now.strftime("%Y-%m-%d %H:%M:%S")
            try:
                login_dt = datetime.strptime(login_time_str, "%Y-%m-%d %H:%M:%S")
                mins = round((now - login_dt).total_seconds() / 60, 1)
                entry.find("duration_min").text = str(mins)
            except Exception:
                entry.find("duration_min").text = "0"
            break
 
    ET.indent(tree, space="    ")
    tree.write(LOGS_FILE, encoding="utf-8", xml_declaration=True)


# =============================================================================
#  get_login_stats() -> dict[str, int]
#  Count how many times each user has logged in.
#  Returns: {"alice": 4, "bob": 1, ...}
#  Used by BarChart (login frequency per user).
# =============================================================================
def get_login_stats():
    counts = {}
    for entry in read_logs().findall("login"):
        u = entry.find("username")
        if u is not None:
            counts[u.text] = counts.get(u.text, 0) + 1
    return counts


# =============================================================================
#  get_daily_logins() -> dict[str, int]
#  Count logins grouped by calendar date.
#  Returns: {"2026-03-13": 3, "2026-03-14": 5, ...}
#  Used by LineChart (daily login trend).
# =============================================================================
def get_daily_logins():
    daily = {}
    for entry in read_logs().findall("login"):
        lt = entry.find("login_time")
        if lt is not None and lt.text:
            day = lt.text[:10]
            daily[day] = daily.get(day, 0) + 1
    return daily

def get_login_history():
    """Return complete login history with all session details."""
    history = []
    logs = read_logs()
    
    for entry in logs.findall("login"):
        login_entry = {
            'id': entry.find('id').text if entry.find('id') is not None else '',
            'username': entry.find('username').text if entry.find('username') is not None else '',
            'login_time': entry.find('login_time').text if entry.find('login_time') is not None else '',
            'logout_time': entry.find('logout_time').text if entry.find('logout_time') is not None else '',
            'duration_min': entry.find('duration_min').text if entry.find('duration_min') is not None else ''
        }
        history.append(login_entry)
    
    return history