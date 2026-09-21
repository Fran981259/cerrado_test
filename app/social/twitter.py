import logging
import os

import tweepy

from .renderer import generate_twitter_image

logger = logging.getLogger(__name__)


def get_twitter_client():
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        logger.warning("Credenciais do Twitter ausentes no .env")
        return None

    # Tweepy v2 Client for posting tweets
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    # Tweepy v1.1 API for media upload (v2 media upload is limited/complex in some tweepy versions)
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    return client, api


def post_to_twitter(title: str, category: str, slug: str):
    """
    Generate an image and post to Twitter.
    Returns True if successful, False otherwise.
    """
    creds = get_twitter_client()
    if not creds:
        return False

    client, api = creds
    image_path = None

    try:
        # 1. Generate Image
        image_path = generate_twitter_image(title, category)

        # 2. Upload Media
        media = api.media_upload(filename=image_path)
        media_id = media.media_id

        # 3. Create Tweet Text
        tweet_text = f"🚨 {category.upper()}: {title}\n\nLeia mais: https://portalcerrado.com.br/noticia/{slug}"

        # 4. Post Tweet
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        logger.info(f"Tweet postado com sucesso! ID: {response.data['id']}")
        return True
    except Exception as e:
        logger.error(f"Erro ao postar no Twitter: {e}")
        return False
    finally:
        # Clean up temp image
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
