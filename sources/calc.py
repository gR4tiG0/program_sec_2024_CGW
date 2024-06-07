from scipy.stats import t, f, f_oneway, ttest_ind
from math import sqrt
from constants import *
import logging

logger = logging.getLogger("CALC LOGGER")
logger.setLevel(logging.INFO)

def getStatistics(key_press_times:list, ph_len: int) -> tuple[list[float], list[float]]:
    mt, vt = [0.0] * ph_len, [0.0] * ph_len

    for i in range(ph_len):
        lc = 0
        for j in range(len(key_press_times)):
            if key_press_times[j][i] != -1:
                mt[i] += key_press_times[j][i]
                lc += 1
        mt[i] /= lc
    
    for i in range(ph_len):
        lc = 0
        for j in range(len(key_press_times)):
            if key_press_times[j][i] != -1:
                vt[i] += pow(key_press_times[j][i] - mt[i], 2)
                lc += 1
        vt[i] /= lc

    return (mt, vt)


def sieve(item: list) -> bool:
    res = list(item)
    for i in range(len(res)):
        item_ = item[:i] + item[i + 1:]
        mean = sum(item_) / len(item_)
        Si = sqrt(sum(pow(x - mean, 2) for x in item_) / (len(item_) - 1))
        tp = abs((item[i] - mean) / Si)
        tT = t.ppf(1 - SIG_LEVEL / 2, df = len(item_) - 1)
        if tp > tT:
            res[i] = -1
    return res    

def checkIdentification(user_stats: list[list[float]], stored_stats: tuple[list[float], list[float]]) -> bool:
    mt_stored, vt_stored = stored_stats
    ph_len = len(mt_stored)

    logger.debug(f"Stored stats: {mt_stored = }, {vt_stored = }")
    logger.debug(f"User stats: {user_stats}")

    upd_user_stats = [[0.0]*ph_len for i in range(COLLECTION_ATTEMPTS)]
    for i in range(ph_len):
        tmp = sieve([j[i] for j in user_stats])
        for j in range(COLLECTION_ATTEMPTS):
            upd_user_stats[j][i] = tmp[j]


    logger.debug(f"Updated user stats: {upd_user_stats}")
    df = COLLECTION_ATTEMPTS - 1

    tT = t.ppf(1 - SIG_LEVEL / 2, df = df) #two tailed
    #fT = f.ppf(1 - SIG_LEVEL, dfn= df, dfd=df)

    f_critical_low = f.ppf(SIG_LEVEL / 2, df, df)
    f_critical_high = f.ppf(1 - SIG_LEVEL / 2, df, df)


    logger.info(f"Table values: {tT = :.6f}, {f_critical_low = :.6f}, {f_critical_high = :.6f}")

    mt_user, vt_user = getStatistics(upd_user_stats, ph_len)

    logger.debug(f"User stats: {mt_user = }, {vt_user = }")
    logger.debug(f"Stored stats: {mt_stored = }, {vt_stored = }")


    for letter in range(ph_len):
        logger.info(f"Checking letter {letter + 1}")
        logger.debug(f"S1 {max(vt_user[letter], vt_stored[letter]):.6f}")
        logger.debug(f"S2 {min(vt_user[letter], vt_stored[letter]):.6f}")
        fp = vt_user[letter] / vt_stored[letter] if vt_user[letter] > vt_stored[letter] else vt_stored[letter] / vt_user[letter]

        p_value = 2 * min(f.cdf(fp, df, df), 1 - f.cdf(fp, df, df))
        logger.info(f"P-value: {p_value:.6f}")
        logger.info(f"F-test Statistic: {fp:.6f}")
        if fp < f_critical_low or fp > f_critical_high:
            logger.info(f"F-test failed for letter {letter + 1}")
            return False
        
        tp = abs((mt_user[letter] - mt_stored[letter]) / sqrt(vt_user[letter] / COLLECTION_ATTEMPTS + vt_stored[letter] / COLLECTION_ATTEMPTS))
        logger.info(f"t-test Statistic: {tp:.6f}")

        if tp > tT:
            logger.info(f"t-test failed for letter {letter + 1}")
            return False

    return True    

