import os
import time
import logging
from datetime import datetime

import tweepy
import schedule
from dotenv import load_dotenv

##
## Load environment variables
load_dotenv()

##
## Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AmpyJr:
    def __init__(self):
        """Initialize the simple Twitter bot using Tweepy v2 client."""
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.bot_name = os.getenv('BOT_NAME', 'Ampy Jr.')
        
        ##
        ## Initialize Twitter API v2 client
        self.client = self._authenticate()
        
        if self.client:
            logger.info(f"Bot '{self.bot_name}' initialized successfully with v2 client!")
        else:
            logger.error("Failed to initialize Twitter API v2 client")
    
    def _authenticate(self):
        """Authenticate with Twitter API v2."""
        try:
            ##
            ## Create OAuth 1.0a User Context authentication handler
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            
            ##
            ## Create API v2 client
            client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            ##
            ## Verify credentials by getting user info
            me = client.get_me()
            if me.data:
                logger.info(f"Twitter v2 authentication successful! Logged in as: @{me.data.username}")
                return client
            else:
                logger.error("Failed to verify Twitter v2 credentials")
                return None
            
        except Exception as e:
            logger.error(f"Twitter v2 authentication failed: {e}")
            return None
    
    
    
    
    def tweet(self):
        if not self.client:
            logger.error("Twitter v2 client not initialized")
            return False
        
        try:
            ##
            ## Post the tweet using v2 API
            response = self.client.create_tweet(text="hello")
            if response.data:
                logger.info(f"Tweet posted successfully: {response.data['id']}")
                return True
            else:
                logger.error("Tweet response didn't contain data")
                return False
            
        except tweepy.errors.Forbidden as e:
            if "453" in str(e):
                logger.error("❌ Twitter API Error 453: Your API access level doesn't include posting tweets")
                logger.error("You need 'Elevated' or 'Enterprise' access to post tweets")
                logger.error("Visit: https://developer.twitter.com/en/portal/products")
            else:
                logger.error(f"❌ Twitter API Forbidden Error: {e}")
            return False
            
        except tweepy.errors.Unauthorized as e:
            logger.error(f"❌ Twitter API Unauthorized: {e}")
            logger.error("Check your API credentials in the .env file")
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error posting tweet: {e}")
            return False


def main():
    """Main function to run the bot."""
    ##
    ## Check if environment variables are set
    required_vars = [
        'TWITTER_API_KEY', 'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please copy env.example to .env and fill in your Twitter API credentials")
        return
    
    ##
    ## Initialize bot
    bot = AmpyJr()
    
    if not bot.client:
        logger.error("Bot initialization failed. Exiting.")
        return
    
    ##
    ## Schedule the bot to tweet every 2 hours
    schedule.every(2).hours.do(bot.tweet)
    
    ##
    ## Tweet immediately when starting
    logger.info("Posting initial 'hello' tweet...")
    if not bot.tweet():
        logger.error("❌ Failed to post initial tweet. Check the error above.")
        logger.error("The bot will continue running and try again in 2 hours.")
    
    logger.info("Bot is running! Will tweet every 2 hours. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            ##
            ## Check every minute
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
