import json
import requests
import time

###########################################################################################
##CONFIG
public_key = ''
private_key = ''
list_id = ''
from_email = 'jonathan.batscha@yourcompany.com'
from_name = 'Jonathan Batscha'
template_url = 'http://www.yourcompany.com/dailydeals/today'
smart_send = True
google_analytics = False
subject = "Daily Deals!"
##END CONFIG
###########################################################################################

##########################
## name templates/campaigns

#for tracking unique templates/campaigns
# can change this to get date from epoch when in production
epoch = str(time.time())

#generated attributes
template_name = 'template'+epoch
campaign_name = 'campaign'+epoch
##end names
###########

# to get response, in case template page blocks scripts, can add permissions as needed
agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
headers = {
    'User-Agent':agent
    }

############################
## start html retrieve/parse
dd_response = requests.get(template_url,headers=headers)
dd_html = dd_response.text.replace('\r\n','')

# this is the html for unsubscribe link at the bottom
# this should be updated to reflect the style of your template
unsub_html = '<tr><td style="font-family: Arial, Helvetica, sans-serif; font-size: 10px; color: #525252;" align="left">{% unsubscribe %}</td></tr>'

# this piece inserts unsub_html into appropriate place in html
# this should be updated to reflect the structure of your template html
dd_html = dd_html[:-13] + unsub_html + dd_html[-13:]
## end html retrieve/parse
##########################

# create template and save id
template_data = {
    'api_key':private_key,
    'name':template_name,
    'html':dd_html
}

template_response = requests.post('https://a.klaviyo.com/api/v1/email-templates',template_data)

template_id = template_response.json()['id']

#create a campaign and save id
campaign_data = {
    'api_key':private_key,
    'list_id':list_id,
    'template_id':template_id,
    'from_email':from_email,
    'from_name':from_name,
    'subject':subject,
    'name':campaign_name,
    'use_smart_sending':smart_send,
    'add_google_analytics':google_analytics
}

campaign_response = requests.post('https://a.klaviyo.com/api/v1/campaigns',campaign_data)

campaign_id = campaign_response.json()['id']

# sends campaign immediately
# note: can alternatively use klaviyo api to schedule a send in the future
send_data = {
    'api_key':private_key
}

send_url = 'https://a.klaviyo.com/api/v1/campaign/{}/send'.format(campaign_id)

send_response = requests.post(send_url,send_data)

print(send_response)