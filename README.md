# Twilio Livekit Agent

## Setting up Livekit CLI -
https://docs.livekit.io/home/cli/cli-setup/






# Important
1. make sure you remove any space or hiphen from the phone number
2. make sure you export following livekit variables to your terminal before running any `lk` commnad
```
export LIVEKIT_URL=wss://XXXX.livekit.cloud
export LIVEKIT_API_KEY=XXXXXX
export LIVEKIT_API_SECRET=XXXXXXX
```

# How to add a new phone number as an Inbound SIP trunk ?
1. Go to your Twilio and set up and Inbound trunk, use your livekit SIP URI over there.
### Creating inbound SIP trunk on Twilio
https://docs.livekit.io/sip/quickstarts/configuring-twilio-trunk/

2. On your Twilio, link your phone number to the SIP trunk

3. Create an inbound trunk.
    ## Creatin SIP inbound trunking
    create a file similar to the sample file in repo with name inbound_trunk_<phonenumber>.json 
    update your twilio phone number in name and numbers
    then RUN `lk sip inbound create inbound_trunk_<phonenumber>.json`

4. It will print a SIPTrunkID: <ST_XXXX> add this id to your dispatch rule file.

5. Create a dispatch rule
    ## Creating SIP dispatch rule
    create a file with name dispatch_rule_<phonenumber>.json add the trunk id to it,  also, change the phonenumber in the roomPrefix then RUN `lk sip dispatch create dispatch_rule_<phonenumber>.json`

6. Now you can make a phone call and test the flow. 

## Listing inbound Trunks
Following command will list all inbound SIP trunks and show their Ids
`lk sip inbound list`

## Listing dispatch Rules
Following command will list all dispatch Rules and show their Ids
`lk sip dispatch list`

## Deleting inbound SIP trunk
`lk sip inbound delete <sip-trunk-id>`

## Deleting inbound dispatch rule
`lk sip dispatch delete <dispatch-rule-id>`

## How to RUN the agent scrip locally with Livekit CLoud -
1. Add all env variable values for variables in .env.examples and rename it to .env
2. Set up virtual env
`python3.12 -m venv .venv`

3. Activate virtual env 
(Linux/Mac)
`source .venv/bin/activate`
(Windows)
`.venv\Scripts\activate`

4. Install Requirements -
`pip install -r requirements.tx`

5. Start livekit agent (on dev env)-
`python -m voice_agent dev`

6. Start livekit agent (on prod env)-
`python -m voice_agent start`

7. If you have alredy created an inbound trunk on twilio using the steps given above, then you can give your twilio number a call to test it out.
