# sheptwit
A discord bot that reposts tweets

# Setup

## Installing the bot
1. Install [python 3.10 or later](https://www.python.org/downloads/)
2. Clone or download and unzip the bot files
3. (Optional but recommended) Create a new [python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
4. Install the dependencies with `pip install -r requirements.txt`. Note that the provided requirements.txt is very mess and contains many unneeded packages. Sorry!
5. Download and install Chromedriver and a compatible version of chrome. I recommend getting the [latest stable version](https://googlechromelabs.github.io/chrome-for-testing/) unless it doesn't work. I think I've tested with v120 and v131

## Configuring the bot
1. Open sample_config.json in a text editor of your choice
2. Replace the `AAA.123` of the DiscordToken with your [discord bot's token](https://discord.com/developers/applications/)
3. Set the driverpath to the path to your chromedriver.exe
4. Update BOTH occurrences of `my_twitter_account` with the username (not display name!) of your bot's twitter account. Do NOT use your personal twitter account!
5. Set the `email` and `pass` of your bot's twitter account
6. For each twitter account you want to repost from: set the twitter handle and target discord channel. You can add or remove rows as needed, but note that every row must end in a comma EXCEPT the last row.

## Running the bot
1. Lanch the bot with `python3 discordbot.py` or maybe `python3.10 discordbot.py` or whatever your current python is
