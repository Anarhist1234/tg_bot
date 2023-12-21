import time

import requests
from loguru import logger

from config import TelegramConfig
from db import PgDriver

if __name__ == "__main__":
    while True:

        with PgDriver() as curr:
            curr.execute(
                """
                select count(phone), pr.id, pr.name from phones ph
                left join projects pr on ph.project_id = pr.id
                where pr.is_active = true and ph.used = false
                group by pr.id, pr.name
                """
            )

            items = curr.fetchall()

        for item in items:
            logger.info(f"{item['name']} - {item['count']}")
            if item["count"] <= 50:
                text = f"В проекте {item['name']} осталось номеров: {item['count']}"
                api_url = f'https://api.telegram.org/bot{TelegramConfig.access_token}/sendMessage'
                params = {'chat_id': "-1002117048282", 'text': text}

                response = requests.post(api_url, params=params)
                result = response.json()

                logger.info(f"send_mes, {result}")

        time.sleep(60 * 10)
