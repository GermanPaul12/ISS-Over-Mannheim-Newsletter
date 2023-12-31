import yagmail
import requests
from datetime import datetime
import os
from neo4mails import Email
import subprocess
from secret import Secret


def git_push(remote_repo, branch="main"):
    try:
        # Adding the file to the staging area
        subprocess.run(["git", "add", "."], check=True)

        # Committing the changes
        commit_message = f"update data"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Pushing the changes to the remote repository
        subprocess.run(["git", "push", remote_repo, branch], check=False)
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
    MY_LAT = Secret.secrets['MA_LAT']
    MY_LNG = Secret.secrets['MA_LNG']
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
    with open('Files/iss_data.csv', 'a+') as f:
        f.write(f"{iss_position[0]},{iss_position[1]},{datetime.now()}\n")
   
    
    with open("Files/git_log.txt", "r") as f:
        todays_day = datetime.now().weekday()
        if todays_day in [0,2,4,6]:
            if f.read() == "False":
                remote_repo = "origin"
                branch = "main"  # Change this to your branch name if different
                git_push(remote_repo, branch)
                with open("Files/git_log.txt", "w") as file:
                    file.write("True")
        else:
            with open("Files/git_log.txt", "w") as file:
                file.write("False")   

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

        now = datetime.now().hour

        if now >= sunset_hour or now <= sunrise_hour:
            sender = yagmail.SMTP(user=Secret.secrets['GMAIL_MAIL'],
                                  password=Secret.secrets['MAIL_PW'])
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
                sender.send(to=Secret.secrets['MY_MAIL'],
                            bcc=to,
                            subject="The ISS is above you!📍",
                            contents=html_content)
            else:
                sender.send(to=Secret.secrets['MY_MAIL'],
                            subject="The ISS is above you!📍",
                            contents=html_content)
            with open('Files/iss_mannheim.csv', 'a+') as f:
                f.write(f"{datetime.now()},{iss_position}\n")
            print("Look up")
        else:
            print(
                "The ISS is over your head but the sky is to light to see it.")
    print("The code ran successfully.")

if __name__ == "__main__":
    iss_checker()