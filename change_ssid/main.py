#for api calls
import requests

#for structuring responses
import json

#for randomizing data
import random
import string

#for using .env
import os
from dotenv import load_dotenv
load_dotenv()

#for webex
import webexteamssdk
import meraki

#.env variables
#import env_lab

# Read the config file to get settings
#MERAKI_API_KEY = os.getenv('API_KEY_PERSONAL')


print ("This App will update SSIDs Name and PSK.\n\nEnter the API key to manage: ")
MERAKI_API_KEY = input()

baseurl = "https://dashboard.meraki.com/api/v1"

def get_orgs():
    url = baseurl + '/organizations'
    
    payload = None

    headers = {
        'X-Cisco-Meraki-API-Key': MERAKI_API_KEY,
    }

    response_orgs = requests.request('GET',url, headers=headers, data = payload)

    print ("\nThese are all the Organizations available for this key: ")
    
    counter = 1
    for name in response_orgs.json():
        
        print ('(' + str(counter) + ') : ' + name['name'] + ' - ID: ' + name['id'])
        counter = counter+1

    return (response_orgs)

def org_sel(response_orgs):
    print ("\nChoose which organization you want to manage: ")
    selection = input()
    selection = int(selection) - 1
    
    print('\nThe selected ORG name is: ' + response_orgs.json()[int(selection)]['name'])

    #return name of selected ORganization, kinda useless
    #return(response_orgs.json()[int(selection)]['name'])
    
    #returning ID of organization, for further processing
    return(response_orgs.json()[int(selection)]['id'])

def check_mr(org_id):

    url = baseurl + '/organizations/' + org_id + '/devices'

    payload = None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'X-Cisco-Meraki-API-Key': MERAKI_API_KEY,
    }

    response = requests.request('GET',url, headers=headers, data = payload)

    counter = 0
        
    for devices in response.json():
        if str(devices['model']).startswith("MR"):
            print ('There\'s an ' + devices['model'] + ' in this Organization, you can continue :)')
            counter = counter + 1 

    if counter == 0:
        print ("There are no MR to update in this network, lets start again.")
        os.execl(sys.executable, sys.executable, *sys.argv)

    else:
        return(response)

def get_nets(org_id):

    url = baseurl + '/organizations/' + org_id + '/networks' 
    
    payload = None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'X-Cisco-Meraki-API-Key': MERAKI_API_KEY,
    }

    response_nets = requests.request('GET',url, headers=headers, data = payload)

    print ("\nThese are all the Networks available for Org ID: " + org_id)
    counter = 1

    for name in response_nets.json():  
        print ('(' + str(counter) + ') : ' + name['name'] + ' - NETID: ' + name['id'])
        counter = counter+1

    print ('\n')

    return(response_nets)

def net_sel(response_nets):

    print ("Choose which Network you want to manage: ")
    selection = input()
    selection = int(selection) - 1
    
    print('\nThe selected NETWORK name is: ' + response_nets.json()[int(selection)]['name'])

    #return name of selected ORganization, kinda useless
    #return(response_orgs.json()[int(selection)]['name'])

    #returning ID of organization, for further processing
    return(response_nets.json()[int(selection)]['id'])

def get_ssids(net_id):
    url = baseurl + "/networks/" + net_id + "/wireless/ssids"

    payload = None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": MERAKI_API_KEY,
    }

    response_ssids = requests.request('GET', url, headers=headers, data = payload)

    if response_ssids.ok == False:
        print("There are NO SSIDs for the selected Network")
        return(response_ssids.ok)
        
    else:
        print ("\nThese are all the ENABLED SSIDs and PSKs for the selected Network")
        counter = 1

        for name in response_ssids.json():  
            if name['enabled']==True:
                print ('(' + str(counter) + ') : ' + name['name'] + ' - PSK: ' + name['psk'])
                counter = counter+1

        print ('\n')

        return(response_ssids)

def ssid_sel(response_ssids, net_id):
    
    print ("Choose which SSID you want to update the PSK: ")
    selection = input()
    selection = int(selection) - 1
    
    print('\nThe selected SSID is: ' + response_ssids.json()[int(selection)]['name'])
    newssid = input ("Enter the new SSID Name: ")
    newpsk = input("Enter the new PSK: ")

    url = baseurl + "/networks/" + net_id + "/wireless/ssids/" + str(selection)


    payload = {
        "name": newssid,
        "psk": newpsk
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": MERAKI_API_KEY,
    }

    payloadstr=json.dumps(payload)

    response_ssids = requests.request('PUT', url, headers=headers, data = payloadstr) 

    if (response_ssids.json() == 400):
        print("\nBAD URL")
        return()
        
    else:
        print("\nThe new SSID has these attributes:\nName: "+ response_ssids.json()["name"] + "\nPSK: " + response_ssids.json()["psk"])
        #returning ID of organization, for further processing
        return()

# main flow
def main():

    #find and display organizations
    response_orgs = get_orgs()

    #choose desired organization to manage
    org_id = org_sel(response_orgs)

    #list MR devices in this organization, if none is found, reset to the beginning
    check_mr(org_id)

    #find and display networks available under the selected organization
    response_nets = get_nets(org_id)

    #choose the desired network to manage
    #OPT - list productypes in the selected network
    net_id = net_sel(response_nets)

    #find and list SSIDs available in the chosen network
    response_ssids = get_ssids(net_id)

    if (response_ssids==False):
        return False

    #choose the desired SSID to manage
    ssid_n = ssid_sel(response_ssids, net_id)

    return True


if __name__ == "__main__":
    
    stop = False
    while stop==False:
        stop = main()
    
    print ("\nThanks for using our App.\n")