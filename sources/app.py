#!/usr/bin/env python3
from constants import *
from collector import Collector
from calc import getStatistics, checkIdentification
from json import dump, load, JSONDecodeError
import argparse
import logging
 

logger = logging.getLogger("APP LOGGER")
logging.basicConfig(level=logging.INFO)


def getKeyStore() -> dict:
    #load keystore from file, if file not found or empty, return empty dict
    #stores mean and variance for each control phrase in json format
    try:
        with open(FILE_STORE, "r") as file:
            try:
                return load(file)
            except JSONDecodeError:
                logger.error(ERR_EMPTY_FILE)
                return dict()
            
    except FileNotFoundError:
        logger.error(ERR_FILE_NOT_FOUND)
        return dict()


def setKeyStore(keystore: dict) -> None:
    #save keystore to file
    with open(FILE_STORE, "w") as file:
        dump(keystore, file)


def appRoutine(mode: str, frase: str) -> None:
    #main routine of the application
    logger.debug(f"Starting application in {mode} mode.")
    
    #load keystore
    keystore = getKeyStore()

    #if control phrase not found in keystore, we can't run prod mode, return
    if mode == MODE_PRD:
        if frase not in keystore:
            logger.error(ERR_INVALID_PASSPHRASE)
            return


    #if control phrase not provided, use first key in keystore
    if not frase:
        logger.error(ERR_PASSPHRASE_NOT_FOUND)
        try:
            frase = keystore.keys()[0]
        except KeyError:
            logger.error(ERR_EMPTY_PASSPHRASE)
            #if keystore is empty, start with "default"
            frase = "default"

    logger.info(f"Control phrase: {frase}")

    #intialize collector and collect key press times
    collector = Collector(COLLECTION_ATTEMPTS, frase)
    key_press_times = collector.collect()

    logger.debug("Key press times collected")
    logger.debug(f"Key press times: {key_press_times}")

    #calculate mean and variance of key press times
    mt, vt = getStatistics(key_press_times, len(key_press_times[0]))

    logger.debug("Statistics calculated")
    logger.debug(f"Mean: {mt}")
    logger.debug(f"Variance: {vt}")

    #if learning mode, save mean and variance to keystore and exit
    if mode == MODE_LRN:
        keystore[frase] = {"mean": mt, "variance": vt}
        setKeyStore(keystore)
        logger.info("Keystore saved")
        return

    #if production mode, load mean and variance from keystore and check identification
    mt_stored, vt_stored = keystore[frase]["mean"], keystore[frase]["variance"]

    
    res = checkIdentification(key_press_times, (mt_stored, vt_stored))

    #print identification result

    if res:
        logger.info("User identified, access granted.")
    else:
        logger.error(ERR_USER_DEN)

def main() -> None:
    #parse arguments to determine mode
    parser = argparse.ArgumentParser(description="CGW program")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-l", "--learning", action="store_true", help="learning mode")
    parser.add_argument("-p", "--production", action="store_true", help="production mode")
    parser.add_argument("-f", "--frase", type=str, help="control phrase")
    args = parser.parse_args()

    #verbose mode enabled
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("COLLECTOR LOGGER").setLevel(logging.DEBUG)
        logging.getLogger("CALC LOGGER").setLevel(logging.DEBUG)
    
    #determine mode
    mode = MODE_PRD if args.production else MODE_LRN

    #launch main routine
    appRoutine(mode, args.frase)        


if __name__ == "__main__":
    main()
