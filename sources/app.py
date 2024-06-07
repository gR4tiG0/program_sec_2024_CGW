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
    with open(FILE_STORE, "w") as file:
        dump(keystore, file)


def appRoutine(mode: str, frase: str) -> None:
    logger.debug(f"Starting application in {mode} mode.")
    
    keystore = getKeyStore()

    if mode == MODE_PRD:
        if frase not in keystore:
            logger.error(ERR_INVALID_PASSPHRASE)
            return

    if not frase:
        logger.error(ERR_PASSPHRASE_NOT_FOUND)
        try:
            frase = keystore["control_phrase"]
        except KeyError:
            logger.error(ERR_EMPTY_PASSPHRASE)
            frase = "default"

    logger.info(f"Control phrase: {frase}")

    collector = Collector(COLLECTION_ATTEMPTS, frase)
    key_press_times = collector.collect()
    # key_press_times = [[0.1567831039428711, 0.19681215286254883, 0.17332911491394043, 0.17327594757080078, 0.10070300102233887, 0.09225797653198242, 0.09938621520996094], [0.17194509506225586, 0.18021106719970703, 0.18733811378479004, 0.17404890060424805, 0.12795209884643555, 0.12884211540222168, 0.11377215385437012], [0.15682697296142578, 0.19086503982543945, 0.21119379997253418, 0.16853904724121094, 0.12201094627380371, 0.13383913040161133, 0.14722585678100586]]

    logger.debug("Key press times collected")
    logger.debug(f"Key press times: {key_press_times}")

    mt, vt = getStatistics(key_press_times, len(key_press_times[0]))

    logger.debug("Statistics calculated")
    logger.debug(f"Mean: {mt}")
    logger.debug(f"Variance: {vt}")

    
    if mode == MODE_LRN:
        keystore[frase] = {"mean": mt, "variance": vt}
        setKeyStore(keystore)
        logger.info("Keystore saved")
        return


    mt_stored, vt_stored = keystore[frase]["mean"], keystore[frase]["variance"]

    logger.debug(f"{vt_stored = }")
    res = checkIdentification(key_press_times, (mt_stored, vt_stored))

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
