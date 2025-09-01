import os, sys
import time
import logging
from datetime import datetime
import prettytable as pt
import tweepy
import schedule
from dotenv import load_dotenv
from commands import apy, tvl
from utils import is_dev, get_saved_totals, get_saved_tvl
from utils.helpers import human_readable, get_sign
from PIL import Image, ImageDraw, ImageFont


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
        if is_dev():
            self.api_key = os.getenv('DEV_TWITTER_API_KEY')
            self.api_secret = os.getenv('DEV_TWITTER_API_SECRET')
            self.access_token = os.getenv('DEV_TWITTER_ACCESS_TOKEN')
            self.access_token_secret = os.getenv('DEV_TWITTER_ACCESS_TOKEN_SECRET')
            self.bot_name = os.getenv('BOT_NAME', 'Ampy Jr. Dev')
        else:
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
            api = tweepy.API(auth)
            self.api = api
            
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
        
        tweet_text = ''
        
        ##
        ## Get the current data
        ## this will save the data to the database
        tvl_result = tvl()
        
        if tvl_result['totals_id'] == None:
            logger.error("Failed to save TVL data. Exiting.")
            return
        
        if tvl_result['tvl_id'] == None:
            logger.error("Failed to save TVL data. Exiting.")
            return

        ##
        ## Get the last two entries so we can compare
        saved_totals = get_saved_totals()
        
        if not saved_totals or len(saved_totals) < 2:
            logger.error("Insufficient saved totals data. Need at least 2 records to compare.")
            return
        
        ##
        ## Extract batch IDs for current and previous records
        current_batch_id = saved_totals[0][0]
        previous_batch_id = saved_totals[1][0]
        
        ##
        ## Get TVL data for both batches and validate
        saved_tvl = get_saved_tvl(current_batch_id, previous_batch_id)
        
        if not saved_tvl:
            logger.error("No TVL data found for the specified batch IDs.")
            return

        ##
        ## Calculate the total spending capacity and change.
        current_spending = float(saved_totals[0][2])
        previous_spending = float(saved_totals[1][2])

        total_spending_change = abs(current_spending - previous_spending)
        sign = get_sign(current_spending, previous_spending)

        if total_spending_change == 0:
            total_spending_change = '0'
            sign = ''
            
        total_spending = f"${human_readable(current_spending)} ({sign}${human_readable(total_spending_change)})"

        tweet_text += f"Spending Capacity: {total_spending}\n"

        ##
        ## staked amp total and change
        current_amp = float(saved_totals[0][1]) / 1e18
        previous_amp = float(saved_totals[1][1]) / 1e18

        total_amp_change = abs(current_amp - previous_amp)
        sign = get_sign(current_amp, previous_amp)

        if total_amp_change == 0:
            total_amp_change = '0'
            sign = ''

        total_amp = f"{human_readable(current_amp)} ({sign}{human_readable(total_amp_change)})"

        tweet_text += f"Staked AMP: {total_amp}\n"

        ##
        ## setup the output array for the image. 
        apy_result = apy()
        current_tvl = []
        for i in range(len(saved_tvl)):
            if saved_tvl[i][5] == current_batch_id:
                current_pool_capacity = float(saved_tvl[i][4])
                current_pool_amp = float(saved_tvl[i][3]) / 1e18
                
                ##
                ## Find matching APY for this pool
                pool_name = saved_tvl[i][1]
                pool_apy = 'N/A'
                
                for apy_pool in apy_result['data']:
                    if apy_pool['entity']['name'] == pool_name:
                        apy_short = apy_pool['reward_rate']['7_day']['label']
                        apy_long = apy_pool['reward_rate']['30_day']['label']
                        break
                
                ##
                ## Find how many amp from last jawn.
                previous_pool_amp = 0
                for j in range(len(saved_tvl)):
                    if saved_tvl[j][5] == previous_batch_id and saved_tvl[j][1] == pool_name:
                        previous_pool_amp = float(saved_tvl[j][3]) / 1e18
                        break
                
                current_pool_amp_change = abs(current_pool_amp - previous_pool_amp)
                sign = get_sign(current_pool_amp, previous_pool_amp)

                if current_pool_amp_change == 0:
                    current_pool_amp_change = '0'
                    sign = ''
                else:
                    current_pool_amp_change = f"{sign}{human_readable(current_pool_amp_change)}"

                current_tvl.append([
                    saved_tvl[i][1],
                    apy_long,
                    f"${human_readable(current_pool_capacity)}",
                    human_readable(current_pool_amp),
                    current_pool_amp_change
                ])
        ##
        ## create table
        ## setup columns and alignment
        table = pt.PrettyTable(['Pool', '30D', 'USD', 'AMP', 'Change'])
        table.align['Pool'] = 'l'
        table.align['30D'] = 'r'
        table.align['USD'] = 'r'
        table.align['AMP'] = 'r'
        table.align['Change'] = 'r'
        table.padding_width = 1
        table.header_style = 'upper'
        

        ##
        ## add rows to table
        for row in current_tvl:
            table.add_row(row)

        logger.info(table)

        base_dir = os.path.dirname(__file__)
        font_path = os.path.join(base_dir, "UbuntuMono-R.ttf")
            
        fnt = ImageFont.truetype(os.path.abspath(font_path), 30)
        
        ##
        ## create a blank image that we can measure the text bounding box
        img = Image.new('RGB', (1000, 1000), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        bbox = d.textbbox((0, 0), f'{table}', font=fnt)
        
        ##
        ## create the final image
        img = Image.new('RGB', (bbox[2] + 40, bbox[3] + 40), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.multiline_text((20, 20), f'{table}', font=fnt, fill=(0, 0, 0))

        img_path = os.path.join(base_dir, f'img/twitter.jpg')
        img.save(img_path, 'JPEG')

        media = self.api.media_upload(filename=img_path)
        
        try:
            ##
            ## Post the tweet using v2 API

            response = self.client.create_tweet(
                text=tweet_text,
                media_ids=[media.media_id]
            )
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
    ## Initialize bot
    bot = AmpyJr()
    
    if not bot.client:
        logger.error("Bot initialization failed. Exiting.")
        return

    ##
    ## Tweet immediately when starting
    logger.info("Posting tweet...")
    if not bot.tweet():
        logger.error("❌ Failed to post initial tweet. Check the error above.")
        return
    
    logger.info("Bot completed successfully!")

if __name__ == "__main__":
    main()
