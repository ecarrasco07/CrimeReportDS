import requests
import re
import pandas as pd
import numpy as np
import time
import oracledb
import getpass
import logging
from geopy.geocoders import Nominatim

# Emailing packages
from email.message import EmailMessage
from email.utils import make_msgid
import ssl
import smtplib


geolocator = Nominatim(user_agent="MU-DS-Capstone")


def fix_address(address):
    # Error catching
    # Not-string error
    address = str(address)
    # Remove city
    if "," in address:
        address = address[:address.index(",")].strip()
    # If intersection, just use first street. TODO: Improve this
    # if "/" in address:
    #    address = address[:address.index("/")].strip()
    # Remove NA values
    if pd.isna(address):
        address = np.nan
    # Change block address to just be that address number
    address = address.replace("-BLK", "")
    # Catching the BLVD error, needs to say BLVD not BL
    if address.endswith("BL"):
        address += "VD"
    # Catching MLK DR error, use old name
    address = address.replace("MARTIN L KING JR DR", "OLD WORLD THIRD ST")
    # Layton Error
    address = address.replace("S LAYTON ST", "S LAYTON BLVD")
    # Leon Error
    address = address.replace("LEON TR", "LEON TERRACE")
    # Mc Kinley Error
    address = address.replace("MC KINLEY", "MCKINLEY")
    # W Fond Du Lac Error
    if "FOND DU LAC" in address and "AV" not in address:
        address = address.replace("FOND DU LAC", "FOND DU LAC AV")
    # Bluemound road error
    address = address.replace("BLUE MOUND RD", "BLUEMOUND RD")
    return address + " MILWAUKEE"


def geocode(address):
    try:
        # First scan for intersections
        if "/" in address:
            url = generate_search_url(address)
            latlong = url_to_latlong(url)
            # Add some buffer so that the getgpt function will grab the correct
            # data
            geocoded = [0, latlong]
        else:
            geocoded = geolocator.geocode(address)
        return geocoded
    except Exception as e:
        logging.warning("Error geocoding", e)


def get_gps(geocoded, index):
    if geocoded is None:
        return np.nan
    gps = geocoded[1][index]
    if index == 0 and abs(gps - 43.0389) > 1:
        return np.nan
    elif index == 1 and abs(gps + 87.9065) > 1:
        return np.nan
    return gps

# Functions to use a request to google maps and find the lat long from there


def generate_search_url(street):
    street = street.replace(",MKE", "")
    street = street.replace(" /", "%")
    street = street.replace("/", "%")
    street = street.replace(" ", "+")
    if ("Milwaukee" in street) or ("MILWAUKEE" in street):
        return f"https://www.google.com/maps/search/{street},+WI+5xxxx/@"
    else:
        return f"https://www.google.com/maps/search/{street},+Milwaukee,+WI+5xxxx/@"


def url_to_latlong(url):
    website_txt = requests.get(url, timeout=(30, 60)).text
    var_to_scan_across_latlong = 100
    center_loc = website_txt.find("center")
    center_line = website_txt[center_loc:center_loc +
                              var_to_scan_across_latlong]
    match = re.search(r"center=(-?\d+\.\d+)%2C(-?\d+\.\d+)", center_line)
    latit, longit = match.group(1), match.group(2)
    return float(latit), float(longit)


# Emailing functions

def securely_send_message(message, recipient):
    # Defining security measures
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login('pyemail.test6@gmail.com', 'ciorccxvnqcbdiam')
        smtp.sendmail('pyemail.test6@gmail.com',
                      recipient, message.as_string())


def send_email(recipient, subject, body, sender='example@gmail.com'):
    # Defining the email
    em = EmailMessage()
    em['From'] = sender
    em['To'] = recipient
    em['Subject'] = subject
    em['Body'] = body

    securely_send_message(em, recipient)


def imbed_email(recipient, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    image_cid = make_msgid(domain='xyz.com')
    msg.add_alternative("""\
    <html>
        <body>
            <p>""" + body + """<br>
            </p>
            <img src="cid:{image_cid}">
        </body>
    </html>
    """.format(image_cid=image_cid[1:-1]), subtype='html')

    securely_send_message(msg, recipient=recipient)


if __name__ == "__main__":
    logging.basicConfig(filename="logs.txt")

    # Connect to database
    password = getpass.getpass("DB Password: ")
    wallet_password = getpass.getpass("Wallet Password: ")
    connection = oracledb.connect(
        user="admin",
        password=password,
        dsn="ltl3y0m4d7of29l1_high",
        config_dir="./config",
        wallet_location="./config",
        wallet_password=wallet_password)

    logging.info("Successfully connected to Oracle Database")
    cursor = connection.cursor()

    # Run indefinitely
    try:
        while True:
            try:
                # Grab police call log from HTML table
                url = 'https://itmdapps.milwaukee.gov/MPDCallData/index.jsp?district=All'
                headers = {'User-Agent': 'Marquette Data Science'}
                html = requests.get(url, headers=headers).content
                df = pd.read_html(html, index_col=0, header=None)[-1]
                # Remove multi-index
                df.columns = df.columns.droplevel(0)

                # Add Latitude and Longitude columns to dataframe
                fixed_addresses = df.Location.transform(fix_address)
                geocoded_addresses = fixed_addresses.apply(geocode)
                df["Latitude"] = geocoded_addresses.apply(get_gps, index=0)
                df["Longitude"] = geocoded_addresses.apply(get_gps, index=1)

                """ SEND DATA TO SQL DATABASE """

                for callnumber, (date, location, district, nature,
                                 status, latitude, longitude) in df.iterrows():
                    if pd.isna(latitude):
                        latitude = "NULL"
                    if pd.isna(longitude):
                        longitude = "NULL"
                    try:
                        query = f"SELECT * FROM CALLS_DUP WHERE CALL_NUMBER = '{callnumber}' AND DATE_TIME = '{date}' AND LOCATION = '{location}' \
                        AND POLICE_DISTRICT = '{district}' AND NATURE_OF_CALL = 'nature' AND STATUS = 'Service in Progress'"
                        response = cursor.execute(query).fetchall()
                        if response:
                            continue  # SKIP IF ALREADY EXISTS IN DATABASE
                        query = f"INSERT INTO CALLS_DUP VALUES ('{callnumber}', '{date}', '{location}', '{district}', '{nature}', '{status}', {latitude}, {longitude})"    
                        cursor.execute(query)
                    except Exception as e:
                        logging.warning("Error updating Database:", e)
                        logging.warning(
                            callnumber, date, location, district, nature, status, latitude, longitude)

                connection.commit()

            except Exception as e:
                logging.warning("Fatal Error:", e)

            time.sleep(30 * 60)  # Sleep for 30 minutes
    except BaseException:
        # Citation:
        # https://github.com/ifrankandrade/automation/blob/main/Send%20Emails.py
        emails = ['pyemail.test6@gmail.com', 'zfarahany193@gmail.com', 'zachariah.farahany@marquette.edu', 'thomas.florian@marquette.edu'
                  ]
        for email in emails:
            imbed_email(email, 'DS-Capstone-Alert',
                        'This is a secure message that your DS-Capstone data collection script is no longer running. You maybe potentially losing data and should get it up and running ASAP')
