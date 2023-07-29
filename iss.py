import yagmail
import requests
import datetime as dt
import os
from neo4mails import Email
import time

times = 0


def iss_checker():
    #Mannheim
    global times
    MY_LAT = os.environ['MA_LAT']
    MY_LNG = os.environ['MA_LNG']
    #------------------------CODE-------------------------#

    url = "http://api.open-notify.org/iss-now.json"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    latiitude = data["iss_position"]["latitude"]
    longitude = data["iss_position"]["longitude"]

    iss_position = (float(latiitude), float(longitude))
    #print(f"The current ISS location is : {iss_position}")

    parameters = {"lat": MY_LAT, "lng": MY_LNG, "formatted": 0}

    #my_location = (MY_LAT, MY_LNG)
    #print(f"My current location is: {my_location}")

    if iss_position[0] <= float(MY_LAT) + 5 and iss_position[0] >= float(
            MY_LAT) - 5 and iss_position[1] <= float(
                MY_LNG) + 5 and iss_position[1] >= float(MY_LNG) - 5:

        url = "https://api.sunrise-sunset.org/json"
        response = requests.get(url, params=parameters)
        response.raise_for_status()

        data = response.json()
        sunrise = data["results"]["sunrise"]
        sunset = data["results"]["sunset"]

        sunrise_splitted_data = sunrise.split("T")[1].split(":")
        sunset_splitted_data = sunset.split("T")[1].split(":")

        sunrise_hour = int(sunrise_splitted_data[0]) + 1
        sunrise_minute = sunrise_splitted_data[1]

        sunset_hour = int(sunset_splitted_data[0]) + 1
        sunset_minute = sunset_splitted_data[1]

        now = dt.datetime.now().hour
        with open('iss_data.csv', 'a+') as f:
            f.write(f"{iss_position[0]},{iss_position[1]},{dt.datetime.now()}")
        if now >= sunset_hour or now <= sunrise_hour:
            sender = yagmail.SMTP(user=os.environ['GMAIL_MAIL'],
                                  password=os.environ['MAIL_PW'])
            to = Email.read_emails()
            if to:
                sender.send(
                    to=os.environ['MY_MAIL'],
                    bcc=to,
                    subject="The ISS is above you!📍",
                    contents=
                    "Hey there,\n\nThe ISS is above you right now so feel free to look in the sky.\nBest regards\nGerman \n(ISS Mannheim Newsletter)\n\nRemove yourself from the Newsletter: https://iss-route.streamlit.app/ISS_Newsletter"
                )
            else:
                sender.send(
                    to=os.environ['MY_MAIL'],
                    subject="The ISS is above you!📍",
                    contents=
                    "Hey there,\n\nThe ISS is above you right now so feel free to look in the sky.\nBest regards\nGerman \n(ISS Mannheim Newsletter)\n\nRemove yourself from the Newsletter: https://iss-route.streamlit.app/ISS_Newsletter"
                )
            with open('iss_mannheim.csv', 'a+') as f:
                f.write(f"{dt.datetime.now()}: {iss_position}")
            print("Look up")
        else:
            print(
                "The ISS is over your head but the sky is to light to see it.")
        times += 1
        print(f"The code ran {times} times.")
        time.sleep(60)
    else:
        times += 1
        print(f"The code ran {times} times.")
        time.sleep(60)
