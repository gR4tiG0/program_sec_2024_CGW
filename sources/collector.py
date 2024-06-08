from constants import *
from typing import Optional
import logging
import keyboard

logger = logging.getLogger("COLLECTOR LOGGER")
logger.setLevel(logging.INFO)

class Collector:
    """
    Class to collect key press timings from user
    """

    def __init__(self, collection_attempts:int, control_phrase: Optional[str] = None):
        """
        Initialize the collector
        :param collection_attempts: Number of collection attempts
        :param control_phrase: Control phrase to be used for verification
        """
        self.control_phrase = control_phrase
        self.collection_attempts = collection_attempts
        self.key_press_times = []

    def prompt(self) -> tuple[str, list[float]]:
        """
        Prompt the user to enter the control phrase
        :return: Tuple of control phrase and list of timings
        """

        logger.debug("Prompting user")
        logger.info("Enter passphrase: ")
        
        #start recording keyboard events
        keyboard.start_recording()
        inp_phrase = input("> ")
        events = keyboard.stop_recording()
        #stop recording keyboard events
        
        logger.debug(f"User entered events: {events}")
        logger.debug("Recording stopped")

        #parse the events to get the timings
        #initialize unacked dict to keep track of unacknowledged key presses
        unacked = {i: c for i, c in enumerate(self.control_phrase)}
        timings_l = [0.0] * len(self.control_phrase)
        key_down_time = {}



        for event in events:
            if isinstance(event, keyboard.KeyboardEvent):
                #checl if the event is a key press
                if event.event_type == keyboard.KEY_DOWN:
                    #if key pressed down, we save it's time
                    #we also save keyname here, because it is possible 
                    #that next key will be released before this one
                    key_down_time[event.name] = event.time
                elif event.event_type == keyboard.KEY_UP:
                    #if key is released, we calculate the time it was pressed
                    try:
                        #check if this key was pressed during this session
                        if key_down_time[event.name]:
                            logger.debug(f"Key {event.name} found. Was pressed for {event.time - key_down_time[event.name]} seconds")
                            
                            #calculate the time key was pressed
                            timing = event.time - key_down_time[event.name]
                            
                            #clear it from the dict
                            del key_down_time[event.name]

                            #check if this key is part of the control phrase
                            for key, char in unacked.items():
                                if char == event.name:
                                    timings_l[key] = timing
                                    del unacked[key]
                                    break
                    except KeyError:
                        continue
            
                #sometimes user can press enter before releasing last key of the phrase
                #in that case, we need to check if any key of phrase is still unacked
                #and calculate the time it was pressed with time of last button (always enter)
                if event.name == "enter" and event.event_type == keyboard.KEY_DOWN and unacked:
                    for key in unacked:
                        logger.debug(f"Key {unacked[key]} UP was not recorded.")
                        if unacked[key] in key_down_time: timings_l[key] = event.time - key_down_time[unacked[key]]
                    
                    #clear the unacked dict
                    key_down_time, unacked = {}, {}

        logger.debug(f"Timings: {timings_l}")

        return (inp_phrase, timings_l)


    def collect(self) -> list[list[float]]:
        logger.debug("Starting collector")
        att = 0
        while att < self.collection_attempts:
            logger.info(f"Attempt {att + 1}")
            #prompt the user to enter the control phrase
            phrase, timings_l = self.prompt()

            #we want to collect info only for valid control phrase
            if phrase != self.control_phrase:
                #skip if control phrase is invalid
                logger.error(ERR_INVALID_PASSPHRASE)
                continue
            
            #if control phrase is valid, save the timings
            self.key_press_times += [timings_l]
            att += 1

        return self.key_press_times