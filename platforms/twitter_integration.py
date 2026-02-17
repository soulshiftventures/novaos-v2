"""
Twitter Integration - Social media automation
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TwitterIntegration:
    """
    Twitter API integration

    Features:
    - Post tweets
    - Search tweets
    - Get mentions
    - Track engagement
    - Follower growth
    """

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None
    ):
        """
        Initialize Twitter integration

        Args:
            bearer_token: Twitter Bearer Token (or from TWITTER_BEARER_TOKEN)
            api_key: Twitter API Key (or from TWITTER_API_KEY)
            api_secret: Twitter API Secret (or from TWITTER_API_SECRET)
            access_token: Twitter Access Token (or from TWITTER_ACCESS_TOKEN)
            access_secret: Twitter Access Secret (or from TWITTER_ACCESS_SECRET)
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = access_secret or os.getenv('TWITTER_ACCESS_SECRET')

        if not self.bearer_token:
            logger.warning("Twitter bearer token not provided")

        try:
            import tweepy


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)

            self.tweepy = tweepy

            # Initialize client for Twitter API v2
            if self.bearer_token:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret
                )
            else:
                self.client = None

            logger.info("Twitter integration initialized")

        except ImportError:
            logger.error("tweepy package not installed. Run: pip install tweepy")
            self.tweepy = None
            self.client = None

    def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Optional[Dict]:
        """
        Post a tweet

        Args:
            text: Tweet text (max 280 characters)
            reply_to: Tweet ID to reply to

        Returns:
            Tweet data or None
        """
        if not self.client:
            logger.error("Twitter client not available")
            return None

        try:
            response = self.client.create_tweet(
                text=text[:280],  # Enforce character limit
                in_reply_to_tweet_id=reply_to
            )

            tweet_id = response.data['id']
            logger.info(f"Posted tweet: {tweet_id}")

            return {
                'id': tweet_id,
                'text': text,
                'created_at': safe_datetime_now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None

    def post_thread(self, tweets: List[str]) -> List[Optional[Dict]]:
        """
        Post a tweet thread

        Args:
            tweets: List of tweet texts

        Returns:
            List of tweet data
        """
        results = []
        last_tweet_id = None

        for i, text in enumerate(tweets):
            tweet = self.post_tweet(text, reply_to=last_tweet_id)
            results.append(tweet)

            if tweet:
                last_tweet_id = tweet['id']
            else:
                logger.error(f"Failed to post tweet {i+1} in thread")
                break

        return results

    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        since_hours: int = 24
    ) -> List[Dict]:
        """
        Search for tweets

        Args:
            query: Search query
            max_results: Maximum results (default: 10)
            since_hours: Search tweets from last N hours

        Returns:
            List of tweets
        """
        if not self.client:
            return []

        try:
            start_time = safe_datetime_now() - timedelta(hours=since_hours)

            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )

            if not response.data:
                return []

            tweets = []
            for tweet in response.data:
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
                    'metrics': {
                        'likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                        'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                        'replies': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0
                    }
                })

            logger.info(f"Found {len(tweets)} tweets for query: {query}")
            return tweets

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []

    def get_mentions(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get mentions for a user

        Args:
            user_id: Twitter user ID
            max_results: Maximum results

        Returns:
            List of mentions
        """
        if not self.client:
            return []

        try:
            response = self.client.get_users_mentions(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id']
            )

            if not response.data:
                return []

            mentions = []
            for tweet in response.data:
                mentions.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id
                })

            logger.info(f"Found {len(mentions)} mentions")
            return mentions

        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            return []

    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user information

        Args:
            username: Twitter username (without @)

        Returns:
            User data or None
        """
        if not self.client:
            return None

        try:
            response = self.client.get_user(
                username=username,
                user_fields=['public_metrics', 'created_at', 'description']
            )

            if not response.data:
                return None

            user = response.data
            return {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'description': user.description if hasattr(user, 'description') else None,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                'metrics': {
                    'followers': user.public_metrics.get('followers_count', 0) if user.public_metrics else 0,
                    'following': user.public_metrics.get('following_count', 0) if user.public_metrics else 0,
                    'tweets': user.public_metrics.get('tweet_count', 0) if user.public_metrics else 0
                }
            }

        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None

    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """
        Get metrics for a specific tweet

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet metrics
        """
        if not self.client:
            return {'likes': 0, 'retweets': 0, 'replies': 0, 'impressions': 0}

        try:
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['public_metrics', 'non_public_metrics']
            )

            if not response.data:
                return {'likes': 0, 'retweets': 0, 'replies': 0, 'impressions': 0}

            tweet = response.data
            metrics = tweet.public_metrics if tweet.public_metrics else {}

            result = {
                'likes': metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies': metrics.get('reply_count', 0),
                'quotes': metrics.get('quote_count', 0)
            }

            # Add non-public metrics if available
            if hasattr(tweet, 'non_public_metrics') and tweet.non_public_metrics:
                result['impressions'] = tweet.non_public_metrics.get('impression_count', 0)

            return result

        except Exception as e:
            logger.error(f"Error getting tweet metrics: {e}")
            return {'likes': 0, 'retweets': 0, 'replies': 0, 'impressions': 0}

    def like_tweet(self, tweet_id: str) -> bool:
        """
        Like a tweet

        Args:
            tweet_id: Tweet ID

        Returns:
            True if liked successfully
        """
        if not self.client:
            return False

        try:
            # Need to get authenticated user ID first
            me = self.client.get_me()
            if not me.data:
                return False

            self.client.like(tweet_id=tweet_id, user_id=me.data.id)
            logger.info(f"Liked tweet: {tweet_id}")
            return True

        except Exception as e:
            logger.error(f"Error liking tweet: {e}")
            return False

    def retweet(self, tweet_id: str) -> bool:
        """
        Retweet a tweet

        Args:
            tweet_id: Tweet ID

        Returns:
            True if retweeted successfully
        """
        if not self.client:
            return False

        try:
            # Need to get authenticated user ID first
            me = self.client.get_me()
            if not me.data:
                return False

            self.client.retweet(tweet_id=tweet_id, user_id=me.data.id)
            logger.info(f"Retweeted: {tweet_id}")
            return True

        except Exception as e:
            logger.error(f"Error retweeting: {e}")
            return False
