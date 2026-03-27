from utils.xml_handler import read_users, add_user, user_exists, log_login
from utils.security import hash_password, verify_password


def register_user(username, password):

    # Normalize username (case-insensitive)
    username = username.strip().lower()

    # Check if user already exists in XML
    if user_exists(username):
        return False, "User already exists"

    # Hash the password for security
    password_hash = hash_password(password)

    # Save new user to XML
    add_user(username, password_hash)

    return True, "User created successfully"


def login_user(username, password):

    # Normalize username
    username = username.strip().lower()

    # Read all users from XML
    root = read_users()

    # Loop through each user record
    for user in root.findall("user"):

        # Fetch stored username and password
        stored_username = user.find("username").text
        stored_password = user.find("password").text

        # Check username match
        if str(stored_username).lower() == username:

            # Verify hashed password
            if verify_password(password, stored_password):
                entry_id = log_login(
                    username
                )  # Record the login event; capture the log entry ID
                return True, "Login successful", entry_id

            # Password incorrect
            return False, "Incorrect password", None

    # Username not found
    return False, "User not found", None
