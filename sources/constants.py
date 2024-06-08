#define modes
MODE_LRN = "Learning"           #identifier for learning mode
MODE_PRD = "Prodcution"         #identifier for production mode 

#define keystore
FILE_STORE = "keystore.json"    #file to store key press times

#define error messages

ERR_FILE_NOT_FOUND = "DB File not found."                                       #error message occurs when file not found
ERR_EMPTY_FILE = "DB File is empty. Initializing empty keystore."               #error message occurs when file is empty 
ERR_INVALID_PASSPHRASE = "Invalid passphrase, please try again."                #error message occurs when passphrase is invalid
ERR_PASSPHRASE_NOT_FOUND = "Passphrase not provided. Trying to read from file." #error message occurs when passphrase is not provided
ERR_EMPTY_PASSPHRASE = "Empty passphrase, starting with 'default'."             #error message occurs when passphrase is empty
ERR_USER_DEN = "User not identified, access denied."                            #error message occurs when user did not pass identification

#constants
COLLECTION_ATTEMPTS = 5         #number of attempts to collect key press times
SIG_LEVEL = 0.05                #significance level for hypothesis testing, basicly inferential statistic
