# 适配 AstrBot 全版本，直接从顶层包导入核心功能（避免子模块导入冲突）
from astrbot import on_message, Bot, Message, CronJob
import time
import re

# ========== 功能1：无限制撤回消息（支持指定条数/指定用户） ==========
@on_message(keywords=["/撤回"])
async def recall_msg(bot: Bot, msg: Message):
    cmd = msg.text.strip()
    at_users = msg.mentions  # 获取消息中@的用户列表
    
    # 提取用户输入的撤回条数：有数字则用数字，无数字默认撤回20条（可自行修改默认值）
    count_match = re.search(r"\d+", cmd)
    count = int(count_match.group()) if count_match else 20
    
    # 执行撤回逻辑：优先撤回@用户的消息，无@则撤回当前群消息
    if at_users:
        for user in at_users:
            # 调用撤回接口，按指定条数撤回该用户消息
            await bot.recall_messages(user_id=user.user_id, count=count)
        # 撤回后发送反馈（@最后一个用户，避免多次@冗余）
        await bot.send_msg(msg, f"已为你撤回@{user.nickname} 的{count}条消息")
    else:
        # 撤回当前群的指定条数消息
        await bot.recall_messages(chat_id=msg.chat_id, count=count)
        await bot.send_msg(msg, f"已为你撤回当前群的{count}条消息")

# ========== 功能2：宵禁定时任务（含格式错误提示） ==========
@on_message(keywords=["/宵禁"])
async def set_curfew(bot: Bot, msg: Message):
    try:
        # 解析指令格式：必须是“/宵禁 开始时间-结束时间”（例：/宵禁 23:00-06:00）
        time_range = msg.text.split(" ")[1]  # 提取空格后的时间范围
        start_time, end_time = time_range.split("-")  # 拆分开始/结束时间
        
        # 验证时间格式（必须是“时:分”，避免无效时间）
        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))
        # 简单时间合法性校验（时0-23，分0-59）
        if not (0 <= start_h <= 23 and 0 <= start_m <= 59 and 0 <= end_h <= 23 and 0 <= end_m <= 59):
            await bot.send_msg(msg, "时间格式不合法！时需0-23，分需0-59（例：/宵禁 23:00-06:00）")
            return
        
        # 创建“宵禁开始”定时任务：到点设置群为禁止发言
        curfew_start_job = CronJob(
            name=f"curfew_start_{msg.chat_id}",  # 用群ID命名，避免多群任务重名
            cron=f"{start_m} {start_h} * * *",  # cron表达式：分 时 日 月 周（每天固定时间执行）
            func=lambda: bot.set_chat_permission(chat_id=msg.chat_id, permission="forbidden")
        )
        await bot.add_cron_job(curfew_start_job)
        
        # 创建“宵禁结束”定时任务：到点恢复群为正常发言
        curfew_end_job = CronJob(
            name=f"curfew_end_{msg.chat_id}",
            cron=f"{end_m} {end_h} * * *",
            func=lambda: bot.set_chat_permission(chat_id=msg.chat_id, permission="normal")
        )
        await bot.add_cron_job(curfew_end_job)
        
        # 发送设置成功反馈
        await bot.send_msg(msg, f"宵禁已设置成功！每天 {start_time} - {end_time} 自动执行（群内禁止发言→恢复正常）")
    
    # 捕获指令格式错误（用户未输时间/时间格式错）
    except IndexError:
        await bot.send_msg(msg, "指令格式错误！请按：/宵禁 开始时间-结束时间（例：/宵禁 23:00-06:00）")
    except ValueError:
        await bot.send_msg(msg, "时间格式错误！必须是“时:分-时:分”（例：/宵禁 23:00-06:00）")

# ========== 功能3：清屏（空两格逐行显示，避免刷屏） ==========
@on_message(keywords=["/清屏"])
async def clear_screen(bot: Bot, msg: Message):
    # 清屏提示文本（空两格+逐行拆分，避免一次性发多条刷屏）
    clear_prompt = [
        "  正", "  在", "  清", "  屏", "  ，",
        "  请", "  勿", "  打", "  扰", "  ，",
        "  闲", "  杂", "  人", "  等", "  ，",
        "  靠", "  边", "  等", "  候", "  ，",
        "  正", "  在", "  清", "  屏"
    ]
    
    # 逐行发送提示，间隔1.25秒（平衡显示效果和等待时间）
    for line in clear_prompt:
        await bot.send_msg(msg, line)
        time.sleep(1.25)

# 插件加载成功提示（仅启动时在控制台打印，方便确认加载状态）
print("AstrBot 自定义插件（撤回+宵禁+清屏）已成功加载！")