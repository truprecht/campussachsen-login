#!/usr/bin/python3

from requests import session
from sys import argv
from re import search
from html import unescape

assert len(argv) == 3, "Use " + argv[0] + " <username> <password>"

ses = session()

# get link for form submit (university selctor)
req = ses.get("https://campussachsen.tu-dresden.de/o365/login.php")
submit_link = search("https://campussachsen.tu-dresden.de[^\"]*", req.text).group()
# send univerity's login api as id
req = ses.post(submit_link, params= {"entityID": "https://idp2.tu-dresden.de/idp/shibboleth"})

# req.url is redirected to login api
# login w/ credentials and static eventID (why the hell is it even checked?)
req = ses.post(req.url, params = {"j_username": argv[1], "j_password": argv[2], "_eventId_proceed": "Login"})
# check'd
req = ses.post(req.url, params={"relyingPartyId": "https://campussachsen.tu-dresden.de/shibboleth", "_eventId_proceed": "Bestätigen"})

# get js redirect link and cookies
confirmation_link = unescape(search("action=\"([^\"]*)\"", req.text).group(1))
post_parameters = {}
post_parameters["RelayState"]	= unescape(search("name=\"RelayState\" value=\"([^\"]*)\"", req.text).group(1))
post_parameters["SAMLResponse"]	= unescape(search("name=\"SAMLResponse\" value=\"([^\"]*)\"", req.text).group(1))

# post to authorize login to campussachsen; requires non-default user-agent
req = ses.post(confirmation_link, data = post_parameters, headers={'User-Agent': 'Mozilla/5.0'})

# print next expire date
exp_text = search("Ablaufdatum: [^<]*", req.text).group()
print(exp_text)