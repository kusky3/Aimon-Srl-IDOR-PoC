# 0x1D012
How a not-so-random URL unraveled a major privacy violation.

#### Spam and hex
One day I received a spam text message with the following content:
```
Tired of [...]?
use https://redacted.lan/1234abcd
```
and I tapped the link, yes, I didn't worry about it because I'm not worth [$1M](https://web.archive.org/web/20220113021824/https://citizenlab.ca/2021/09/forcedentry-nso-group-imessage-zero-click-exploit-captured-in-the-wild/).
The webpage contained a form which included my phone number, home address and my father's full name.
No authentication was required, and the URL path was an 8 figures base16 ID.

#### The thin line
A quick bruteforce test and it turns out one every 2000 IDs is valid.
If the IDs are randomly distributed among the 4 billion possible hex values,
then this would mean there are more than 2 million valid IDs.
```python
#!/usr/bin/env python3
url = "https://redacted.lan/"
combos = 16**8 # 0xffffffff 
height = 0 # 0x00000000
def hexgen(i):
    while i < combos:
        yield "{:08X}".format(i)
        i += 1
for code in hexgen(height):
        r = requests.get(url + code)
        if r.text:
        	print("found valid ID: "+code+" ("+height+")")        
```
[Google does this too](https://web.archive.org/web/20211124085739/https://www.theverge.com/2015/6/23/8830977/google-photos-security-public-url-privacy-protected), but where to draw the line between IDOR and unguessable?
The IDs should be at least more secure than passwords but it's not that easy.
While passwords can be changed, URL paths can rarely be re-generated by the user in case of compromission.
At the same time, when passwords are compromised, the impact is usually broader.

#### Down the rabbit hole
So how did my, and that of many others, private information ended up there?
Let's narrow it down... who has that data?
In my case, not many:  

* The government  
* My mobile and home ISP
* Family and close friends  

Being realistic narrows it down to just one actor, my ISP.
That's quite worrying because I logged into my account and sure enough,
the "allow us to sell your data" checkbox was unchecked.
But these are just allegations.
At least until I realized that this is the only contract I ever signed up using the combination of my phone number and my father's name.
So the ISP illegally sold them my information to someoene who decided to put it on the internet.
Way to go!
A few `whois` later and I have the name of the company running the SMS spam campaign, a call center.
Their website has a big banner saying that: "We only use authorized databases and We respect your privacy".

#### Forgery 100
Back to the SMS link, let's inspect the webpage form:
```html
[...]
<label for="submit">By clicking you authorize the treatment of the data.</label>
<button id="submit" name="submit">
<b>I'm interested</b>
</button>
[...]
$.ajax({
	type: "POST",
	url: "data.php",
	data: data,
	dataType: "html"
})
[...]
```
So We could easily give the consent for someone else's data to be used, since no authentication is required and We can easily guess the IDs.
Another interesting quirk is that whenever a form is submitted, the call center is notified.
This means that it is possible to craft a POST request to `data.php`,
such that the specified phone number will be called by someone.
The page is also accessible via TOR exit nodes,
meaning that anyone could disrupt their business by sending bogus requests.
A call center just joined the botnet.

#### Certified experts
I had recently learned about [certificate transparency logs](https://crt.sh)
so I decided to give it a go and look for any interesting domains related to `redacted.lan`.
Way stealthier than vhost bruteforcing right?
Among all, one subdomain caught my attention: `redacted`.
Same IP address as the SMS link domain, so they probably use vhosts.
This subdomain points to a webserver with a login form.
Let's inspect the html:
```html
<div> style="display: false;">
	<form id="admin-interface">
		[...]
	</form>
</div>
```
They're hiding the admin interface with `display: false`, which can be changed client side.
Now this might be irrelevant if it wasn't for the fact that, along with that, they're leaking:

* Call center operators
* Contacts database names
* Other companies names (probably their clients)

They can't even protect their own privacy.

#### Pushing to master
Let's keep digging. A JavaScript file called `myscript.js` is being used.
It contains many functions used by the admin interface and some `*.php` endpoints.
All of these endpoints will check if you are authenticated, which I am not,
and redirect you back to the login except one: `ajax/addUser.php`.
After sending a request to this endpoint, even with empty data, We're greeted with the following output:
```json
{"message":"OK","URL":"\/nominative.php?id=1337"}
```
The ID gets incremented after every request.
It would be a shame if someone accidentally created a few thousand totally valid contacts.

---
> Don't comply.  
> -- _James Freeman_
