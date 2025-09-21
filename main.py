from astrbot.decorators import on_message, on_cron
from astrbot.core import Bot, Message
from astrbot.scheduler import CronJob
import time
import re

# ========== 功能1：撤回消息 ==========
@on_message(keywords=["/撤回"])
async def recall_msg(bot: Bot, msg: Message):
    cmd = msg.text.strip()
    at_users = msg.mentions
    count_match = re.search(r"\d+", cmd)
    count = int(count_match.group()) if count_match else 20

    if at_users:
        for user in at_users:
            await bot.recall_messages(user_id=user.user_id, count=count)
        await bot.send_msg(msg, f"已为你撤回@{user.nickname} 的{count}条消息")
    else:
        await bot.recall_messages(chat_id=msg.chat_id, count=count)
        await bot.send_msg(msg, f"已为你撤回当前群的{count}条消息")


# ========== 功能2：宵禁定时任务 ==========
@on_message(keywords=["/宵禁"])
async def set_curfew(bot: Bot, msg: Message):
    time_range = msg.text.split(" ")[1]
    start, end = time_range.split("-")
    start_h, start_m = map(int, start.split(":"))
    end_h, end_m = map(int, end.split(":"))

    job = CronJob(
        name="curfew",
        cron=f"{start_m} {start_h} * * *",
        func=lambda: bot.set_chat_permission(msg.chat_id, "forbidden"),
    )
    await bot.add_cron_job(job)

    job = CronJob(
        name="curfew_end",
        cron=f"{end_m} {end_h} * * *",
        func=lambda: bot.set_chat_permission(msg.chat_id, "normal"),
    )
    await bot.add_cron_job(job)

    await bot.send_msg(msg, f"宵禁已设置：{start}-{end}")


# ========== 功能3：清屏（空两格逐行显示） ==========
@on_message(keywords=["/清屏"])
async def clear_screen(bot: Bot, msg: Message):
    prompt_lines = [
        "  正",
        "  在",
        "  清",
        "  屏",
        "  ，",
        "  请",
        "  勿",
        "  打",
        "  扰",
        "  ，",
        "  闲",
        "  杂",
        "  人",
        "  等",
        "  ，",
        "  靠",
        "  边",
        "  等",
        "  候",
        "  ，",
        "  正",
        "  在",
        "  清",
        "  屏"
    ]
    for line in prompt_lines:
        await bot.send_msg(msg, line)
        time.sleep(1.25)