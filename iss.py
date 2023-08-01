import yagmail
import requests
import datetime as dt
import os
from neo4mails import Email
import time
import subprocess

times = 0
counter_git = 0


def git_push(remote_repo, branch="main"):
    try:
        # Adding the file to the staging area
        subprocess.run(["git", "add", "."], check=True)

        # Committing the changes
        commit_message = f"Add update"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Pushing the changes to the remote repository
        subprocess.run(["git", "push", remote_repo, branch], check=True)
        print("File successfully pushed to the remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {str(e)}")
        print(
            "Please make sure you have configured your Git credentials and have the necessary permissions."
        )


def iss_checker():
    #Mannheim
    global times
    global counter_git
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
    with open('iss_data.csv', 'a+') as f:
        f.write(f"{iss_position[0]},{iss_position[1]},{dt.datetime.now()}\n")
    counter_git += 1
    if counter_git >= 2:
        counter_git = 0
        remote_repo = "origin"
        branch = "main"  # Change this to your branch name if different
        git_push(remote_repo, branch)

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

        if now >= sunset_hour or now <= sunrise_hour:
            sender = yagmail.SMTP(user=os.environ['GMAIL_MAIL'],
                                  password=os.environ['MAIL_PW'])
            to = Email.read_emails()
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body style="margin: 0; padding: 0; background-image: url('https://raw.githubusercontent.com/GermanPaul12/ISS-Route-Viewer-Streamlit/main/Data/iss.jpg'); background-size: cover; background-repeat: no-repeat;">
                <div style="background-color: rgba(0, 0, 0, 0.8); color: white; padding: 20px; text-align: center; font-size: 24px;">Hey there, look up!</div>
                <div style="background-color: rgba(255, 255, 255, 0.8); padding: 20px;">
                    <p style="font-size: 16px; color: #333333;">The ISS is above you right now!</p>
                    <p style="font-size: 16px; color: #333333;">Best regards,</p>
                    <p style="font-size: 16px; color: #333333; font-weight: bold;">German</p>
                    <p style="font-size: 12px; color: #888888;">(ISS Mannheim Newsletter)</p>
                </div>
                <div style="background-color: rgba(255, 255, 255, 0.8); color: #333333; padding: 10px; text-align: center; font-size: 12px;">
                    <p style="margin: 0; color: #007BFF;">Unsubscribe from the Newsletter: <a href="https://iss-route.streamlit.app/ISS_Newsletter" style="color: #007BFF; text-decoration: none;">Unsubscribe</a></p>
                </div>
            </body>
            </html>
            """
            if to:
                sender.send(to=os.environ['MY_MAIL'],
                            bcc=to,
                            subject="The ISS is above you!📍",
                            contents=html_content)
            else:
                sender.send(to=os.environ['MY_MAIL'],
                            subject="The ISS is above you!📍",
                            contents=html_content)
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
