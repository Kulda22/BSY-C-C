# BSY C&C

## Disclaimer

Don't try to use this for any bad things, thanks.

## How to run

Clone this repository.

You need to add .env file in root folder.
The .env file needs to have the following structure :

````
gh-api-token = "<github api token>"
gist-id="<id of gist>"
````

Your GH api token needs to have gists access.

Make sure, you have needed libraries installed with `pip install -r requirements.txt`

Then run exactly one controller with `python Controller.py` on your own computer,
and some bots with `python Bot.py` on computer of your victims.

## Notes

Program was tested with Python 3.10.9. 


