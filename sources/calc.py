from scipy.stats import t, f, f_oneway, ttest_ind
from math import sqrt
from constants import *
import logging

logger = logging.getLogger("CALC LOGGER")
logger.setLevel(logging.INFO)

def getStatistics(key_press_times:list, ph_len: int) -> tuple[list[float], list[float]]:
    """
    Get statistics for key press times
    :param key_press_times: List of key press times
    :param ph_len: Length of the passphrase
    :return: Tuple of mean and variance of key press times
    
    in general data would look like this:
    [
        [0.1799740791, 0.1698138713, 0.1883199214, 0.1741979122, ...., 0.1050920486], - timimngs for letters in first attempt 
        [0.1711528301, 0.1699109077, 0.1331260204, 0.1427738666, ...., 0.1071650981], - timings for letters in second attempt
        ............................................................................, 
        [0.1162168979, 0.1681020259, 0.1548230648, 0.1233329772, ...., 0.1316030025], - timings for letters in N attempt
    ]         ^             ^              ^            ^                    ^ 
        for letter 1   for letter 2  for letter 3  for letter 4        for letter M

    """

    #initialize mean and variance lists
    mt, vt = [0.0] * ph_len, [0.0] * ph_len

    #calculate mean and variance for each letter
    for i in range(ph_len):
        #iterate through phrase length
        lc = 0
        for j in range(len(key_press_times)):
            #iterate through collection attempts

            if key_press_times[j][i] != -1:
                #ignore insuficient data
                mt[i] += key_press_times[j][i]
                lc += 1
        #mean
        mt[i] /= lc
    


    for i in range(ph_len):
        #iterate through phrase length
        lc = 0
        for j in range(len(key_press_times)):
            #iterate through collection attempts
            if key_press_times[j][i] != -1:
                #ignore insuficient data
                vt[i] += pow(key_press_times[j][i] - mt[i], 2)
                lc += 1
        #variance
        vt[i] /= lc

    #return tuple of mean and variance
    return (mt, vt)


def sieve(item: list) -> list:
    """
    Sieve the data for outliers
    :param item: List of key press times
    :return: List of key press times with outliers marked as -1
    """
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
    """
    Check identification of user
    :param user_stats: List of key press times for user
    :param stored_stats: Tuple of mean and variance of key press times stored in keystore
    :return: True if user is identified, False otherwise
    """
    
    #get mean and variance for stored user stats, get length of passphrase
    mt_stored, vt_stored = stored_stats
    ph_len = len(mt_stored)

    logger.debug(f"Stored stats: {mt_stored = }, {vt_stored = }")
    logger.debug(f"User stats: {user_stats}")

    #sieve the data for outliers
    upd_user_stats = [[0.0]*ph_len for i in range(COLLECTION_ATTEMPTS)]
    for i in range(ph_len):
        tmp = sieve([j[i] for j in user_stats])
        for j in range(COLLECTION_ATTEMPTS):
            upd_user_stats[j][i] = tmp[j]


    logger.debug(f"Updated user stats: {upd_user_stats}")
    
    #calculate degrees of freedom
    df = COLLECTION_ATTEMPTS - 1

    #calculate critical values
    #table value for t-test, 

    # H0: there is no statisticly significant difference between user and stored stats
    tT = t.ppf(1 - SIG_LEVEL / 2, df = df*2) #two tailed, two-sampled t-test

    #short explanation:
    # if we are testing whether the means of two samples are different, 
    # a two-tailed test will consider both the possibility that the first mean 
    # is greater than the second mean and the possibility that the first mean 
    # is less than the second mean. We use one-sample t-test determine whether 
    # the mean of a single sample is significantly different from a known mean
     

    #table values for f-test
    f_critical_low = f.ppf(SIG_LEVEL / 2, df, df)
    f_critical_high = f.ppf(1 - SIG_LEVEL / 2, df, df)


    logger.info(f"Table values: {tT = :.6f}, {f_critical_low = :.6f}, {f_critical_high = :.6f}")

    #get fresh statistics for user
    mt_user, vt_user = getStatistics(upd_user_stats, ph_len)

    logger.debug(f"User stats: {mt_user = }, {vt_user = }")
    logger.debug(f"Stored stats: {mt_stored = }, {vt_stored = }")

    #perform f-test and t-test for each letter (bcs I am honestly not sure how to do it for the whole passphrase)
    for letter in range(ph_len):
        logger.info(f"Checking letter {letter + 1}")
        logger.debug(f"S1 {max(vt_user[letter], vt_stored[letter]):.6f}")
        logger.debug(f"S2 {min(vt_user[letter], vt_stored[letter]):.6f}")
        
        #f-test
        # H0: there is no statisticly significant difference between user and stored stats (comparing variances)
        fp = vt_user[letter] / vt_stored[letter] if vt_user[letter] > vt_stored[letter] else vt_stored[letter] / vt_user[letter]

        #p-value
        p_value = 2 * min(f.cdf(fp, df, df), 1 - f.cdf(fp, df, df))
        logger.info(f"P-value: {p_value:.6f}")
        logger.info(f"F-test Statistic: {fp:.6f}")
        if fp < f_critical_low or fp > f_critical_high:
            #if f-test fails, we can't perform t-test
            logger.info(f"F-test failed for letter {letter + 1}")
            return False
        
        #t-test
        # H0: there is no statisticly significant difference between user and stored stats (comparing means)
        tp = abs((mt_user[letter] - mt_stored[letter]) / sqrt(vt_user[letter] / COLLECTION_ATTEMPTS + vt_stored[letter] / COLLECTION_ATTEMPTS))
        logger.info(f"t-test Statistic: {tp:.6f}")

        if tp > tT:
            #if t-test fails, we can't identify user
            logger.info(f"t-test failed for letter {letter + 1}")
            return False

    #if all tests pass for each letter, user is identified
    return True    

