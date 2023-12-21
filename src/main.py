import datetime
import time

import requests
from loguru import logger

from config import TelegramConfig
from db import PgDriver

if __name__ == "__main__":
    while True:
        logger.info(f"TIME {datetime.datetime.now().hour}")
        if 9 <= datetime.datetime.now().hour < 21:
            with PgDriver() as curr:
                curr.execute(
                    """
                    with projects_count as (
                        select count(phone) as count, pr.id, pr.name from phones ph
                        left join projects pr on ph.project_id = pr.id
                        where pr.is_active = true and ph.used = false
                        group by pr.id, pr.name
                    ),
                    projects_count_users as (
                        select pc.count, pc.id, pc.name, count(u.id) as active_users_count from projects_count pc
                        left join project_user pu on pu.project_id = pc.id
                        left join users u on u.id = pu.user_id
                        where u.status != 'OFFLINE'
                        group by pc.id, pc.name, pc.count
                    )
                    select * from projects_count_users
                    where active_users_count > 0
                    """
                )

                items = curr.fetchall()

            for item in items:
                logger.info(f"{item['name']} - {item['count']} users {item['active_users_count']}")
                if item["count"] <= 50:
                    text = f"В проекте {item['name']} осталось номеров: {item['count']}"
                    api_url = f'https://api.telegram.org/bot{TelegramConfig.access_token}/sendMessage'
                    params = {'chat_id': "-1002117048282", 'text': text}

                    response = requests.post(api_url, params=params)
                    result = response.json()

                    logger.info(f"send_mes, {result}")

            time.sleep(60 * 10)
