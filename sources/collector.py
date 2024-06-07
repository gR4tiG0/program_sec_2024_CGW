from constants import *
from typing import Optional
import logging
import keyboard

logger = logging.getLogger("COLLECTOR LOGGER")
logger.setLevel(logging.INFO)

class Collector:
    def __init__(self, collection_attempts:int, control_phrase: Optional[str] = None):
        self.control_phrase = control_phrase
        self.collection_attempts = collection_attempts
        self.key_press_times = []

    def prompt(self) -> tuple[str, list[float]]:
        logger.debug("Prompting user")
        logger.info("Enter passphrase: ")
        keyboard.start_recording()
        inp_phrase = input("> ")
        events = keyboard.stop_recording()
        logger.debug(f"User entered events: {events}")
        logger.debug("Recording stopped")

        unacked = {i: c for i, c in enumerate(self.control_phrase)}
        timings_l = [0.0] * len(self.control_phrase)
        key_down_time = {}

        for event in events:
            if isinstance(event, keyboard.KeyboardEvent):
                if event.event_type == keyboard.KEY_DOWN:
                    key_down_time[event.name] = event.time
                elif event.event_type == keyboard.KEY_UP:
                    try:
                        if key_down_time[event.name]:
                            logger.debug(f"Key {event.name} found. Was pressed for {event.time - key_down_time[event.name]} seconds")
                            timing = event.time - key_down_time[event.name]
                            del key_down_time[event.name]
                            for key, char in unacked.items():
                                if char == event.name:
                                    timings_l[key] = timing
                                    del unacked[key]
                                    break
                    except KeyError:
                        continue
            
                if event.name == "enter" and event.event_type == keyboard.KEY_DOWN and unacked:
                    for key in unacked:
                        logger.debug(f"Key {unacked[key]} UP was not recorded.")
                        if unacked[key] in key_down_time: timings_l[key] = event.time - key_down_time[unacked[key]]
                    
                    key_down_time, unacked = {}, {}

        logger.debug(f"Timings: {timings_l}")

        return (inp_phrase, timings_l)


    def collect(self) -> list[list[float]]:
        logger.debug("Starting collector")
        att = 0
        while att < self.collection_attempts:
            logger.info(f"Attempt {att + 1}")
            phrase, timings_l = self.prompt()
            if phrase != self.control_phrase:
                logger.error(ERR_INVALID_PASSPHRASE)
                continue
            self.key_press_times += [timings_l]
            att += 1

        return self.key_press_times