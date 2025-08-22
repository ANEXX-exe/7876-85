import discord
from discord.ext import commands
from discord import app_commands
import json
import random

DISCORD_TOKEN = "ضع_هنا_توكن_البوت"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

with open("questions.json", "r", encoding="utf-8") as f:
    questions_data = json.load(f)

scores = {}
history = {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.tree.command(name="مسابقة", description="ابدأ مسابقة")
@app_commands.describe(fئة="اختر الفئة", صعوبة="اختر الصعوبة", عدد="عدد الأسئلة")
async def quiz(interaction: discord.Interaction, فئة: str, صعوبة: str, عدد: int):
    await interaction.response.send_message("⏳ يتم توليد الأسئلة...")
    pool = [q for q in questions_data.get(fئة, []) if q["صعوبة"].lower() == صعوبة.lower()]
    if not pool:
        await interaction.followup.send("❌ لا توجد أسئلة متاحة لهذه الفئة والصعوبة.")
        return
    selected = random.sample(pool, min(len(pool), عدد))
    score = 0
    for i, q in enumerate(selected, 1):
        options = "
".join(f"{idx+1}. {opt}" for idx, opt in enumerate(q["خيارات"]))
        await interaction.followup.send(f"**سؤال {i}:** {q['نص']}
{options}")
    scores[str(interaction.user.id)] = scores.get(str(interaction.user.id), 0) + score
    save_json("scores.json", scores)
    await interaction.followup.send(f"✅ انتهت المسابقة! مجموع نقاطك: {score}")

@bot.tree.command(name="لوحة_النتائج", description="عرض ترتيب النقاط")
async def leaderboard(interaction: discord.Interaction):
    if not scores:
        await interaction.response.send_message("لا توجد نتائج بعد.")
        return
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    msg = "
".join(f"<@{user}>: {pts}" for user, pts in top)
    await interaction.response.send_message(f"🏆 **أعلى النقاط:**
{msg}")

@bot.tree.command(name="سجل", description="عرض سجل الإجابات")
async def show_history(interaction: discord.Interaction):
    user_hist = history.get(str(interaction.user.id), [])
    if not user_hist:
        await interaction.response.send_message("❌ لم يتم تسجيل أي إجابات بعد.")
        return
    msg = "
".join(user_hist[-10:])
    await interaction.response.send_message(f"📜 **سجل آخر الإجابات:**
{msg}")

bot.run(DISCORD_TOKEN)