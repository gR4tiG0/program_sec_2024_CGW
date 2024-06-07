#define modes
MODE_LRN = "Prodcution"
MODE_PRD = "Learning"

#define keystore
FILE_STORE = "keystore.json"

#define error messages

ERR_FILE_NOT_FOUND = "DB File not found."
ERR_EMPTY_FILE = "DB File is empty. Initializing empty keystore."
ERR_INVALID_PASSPHRASE = "Invalid passphrase, please try again."
ERR_PASSPHRASE_NOT_FOUND = "Passphrase not provided. Trying to read from file."
ERR_EMPTY_PASSPHRASE = "Empty passphrase, starting with 'default'."
ERR_USER_DEN = "User not identified, access denied."

#constants
COLLECTION_ATTEMPTS = 3
SIG_LEVEL = 0.05