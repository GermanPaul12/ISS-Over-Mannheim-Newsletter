from keep_alive import keep_alive
from iss import iss_checker
import time

while True:
    keep_alive()
    iss_checker()
    time.sleep(60)
