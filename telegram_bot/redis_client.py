import redis
import os


redis_client = redis.StrictRedis.from_url(
    os.getenv("REDIS_URL")
)


def save_telegram_id(email, telegram_id):
    redis_client.set(f"telegram_id:{email}", telegram_id)


def get_telegram_id(email):
    telegram_id = redis_client.get(f"telegram_id:{email}")

    return telegram_id.decode("utf-8") if telegram_id else None


def delete_telegram_id(user_id):
    redis_client.delete(f"telegram_id:{user_id}")


def save_jwt_token(telegram_id, jwt_token):
    key = f"jwt:{telegram_id}"
    redis_client.set(key, jwt_token, ex=3600 * 24 * 7)



def get_jwt_token(telegram_id):
    key = f"jwt:{telegram_id}"

    return (
        redis_client.get(key).decode("utf-8")
        if redis_client.exists(key)
        else None
    )

