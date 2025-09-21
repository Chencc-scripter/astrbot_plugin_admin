# 关键修正：旧版AstrBot的on_message在decorators子模块，Bot/Message在core子模块
from astrbot.decorators import on_message  # 正确导入装饰器
from astrbot.core import Bot, Message        # 正确导入Bot和消息类
from astrbot.scheduler import CronJob        # 正确导入定时任务类
import time
import re

# ========== 功能1：无限制撤回消息 ==========
@on_message(keywords=["/撤回"])  # 装饰器导入正确，可正常触发指令
async def recall_msg(bot: Bot, msg: Message):
    cmd = msg.text.strip()
    at_users = msg.mentions
    # 提取撤回条数，无输入默认20条（无上限，输多少撤多少）
    count_match = re.search(r"\d+", cmd)
    count = int(count_match.group()) if count_match else 20

    if at_users:
        for user in at_users:
            await bot.recall_messages(user_id=user.user_id, count=count)
        await bot.send_msg(msg, f"已撤回@{user.nickname} 的{count}条消息")
    else:
        await bot.recall_messages(chat_id=msg.chat_id, count=count)
        await bot.send_msg(msg, f"已撤回当前群的{count}条消息")

# ========== 功能2：宵禁定时任务 ==========
@on_message(keywords=["/宵禁"])
async def set_curfew(bot: Bot, msg: Message):
    try:
        time_range = msg.text.split(" ")[1]
        start_time, end_time = time_range.split("-")
        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))

        # 时间合法性校验，避免无效值
        if not (0 <= start_h <=23 and 0<=start_m<=59 and 0<=end_h<=23 and 0<=end_m<=59):
            await bot.send_msg(msg, "时间错啦！时0-23，分0-59（例：/宵禁 23:00-06:00）")
            return

        # 定时禁言任务（用群ID命名，避免多群重名）
        curfew_start = CronJob(
            name=f"curfew_start_{msg.chat_id}",
            cron=f"{start_m} {start_h} * * *",
            func=lambda: bot.set_chat_permission(chat_id=msg.chat_id, permission="forbidden")
        )
        await bot.add_cron_job(curfew_start)

        # 定时恢复任务
        curfew_end = CronJob(
            name=f"curfew_end_{msg.chat_id}",
            cron=f"{end_m} {end_h} * * *",
            func=lambda: bot.set_chat_permission(chat_id=msg.chat_id, permission="normal")
        )
        await bot.add_cron_job(curfew_end)

        await bot.send_msg(msg, f"宵禁设置成功！每天{start_time}-{end_time}自动生效")
    except IndexError:
        await bot.send_msg(msg, "格式错啦！正确：/宵禁 开始时间-结束时间（例：/宵禁 23:00-06:00）")
    except ValueError:
        await bot.send_msg(msg, "时间格式错啦！必须是“时:分-时:分”（例：/宵禁 23:00-06:00）")

# ========== 功能3：清屏逐行显示 ==========
@on_message(keywords=["/清屏"])
async def clear_screen(bot: Bot, msg: Message):
    prompt = [
        "  正", "  在", "  清", "  屏", "  ，",
        "  请", "  勿", "  打", "  扰", "  ，",
        "  闲", "  杂", "  人", "  等", "  ，",
        "  靠", "  边", "  等", "  候", "  ，",
        "  正", "  在", "  清", "  屏"
    ]
    for line in prompt:
        await bot.send_msg(msg, line)
        time.sleep(1.25)

# 启动时控制台提示（能看到这个就说明插件加载成功）
print("AstrBot 自定义插件（撤回+宵禁+清屏）已加载！")