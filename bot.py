import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
from telegram.constants import ParseMode

# ================= CONFIG =================
BOT_TOKEN = "8737099647:AAH2dX6T_Eo63z5nMW5cCjmNZMZXKbwnpwE"
ADMIN_CHAT_ID = "8353391073"  # <-- metti qui il tuo ID

if not BOT_TOKEN:
    raise ValueError("8737099647:AAH2dX6T_Eo63z5nMW5cCjmNZMZXKbwnpwE")

if not ADMIN_CHAT_ID:
    raise ValueError("8353391073")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
# ==========================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SCEGLI_PROBLEMA = 1

LABEL_PROBLEMI = {
    "problema_tool": "1] The tool doesn't work/Lo strumento non funziona",
    "problema_uso": "2] I don't understand how to use it/Non capisco come usarlo",
    "problema_pagamento": "3] Tool error problem/ Problema di errore dello strumento",
}

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    user = update.effective_user
    nome = user.first_name if user else "user"

    await update.message.reply_text(
        f"Hi <b>{nome}</b>Welcome to the TracerTheleak_security support bot. What would you need? .\n\n"
        "/collaboration — Collaborate with us\n"
        "/assistance — Get support",
        parse_mode=ParseMode.HTML,
    )


async def collaboration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    user = update.effective_user

    await update.message.reply_text(
        "<b>Thanks for your interest in collaborating!</b>\n\n"
        "]-> also write [1. CHANNEL NAME] [2. WHAT YOU DO] "
        "The administrator will contact you soon within a few hours.",
        parse_mode=ParseMode.HTML,
    )

    if user:
        username = f"@{user.username}" if user.username else "N/A"
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🔔 <b>NEW COLLABORATION REQUEST</b>\n\n"
                f"👤 Name: {user.full_name}\n"
                f"🆔 Username: {username}\n"
                f"🔢 ID: <code>{user.id}</code>"
            ),
            parse_mode=ParseMode.HTML,
        )
        logger.info("Collaboration from %s (ID: %s)", user.full_name, user.id)


# ================= ASSISTANCE =================

async def assistance_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("1]  The tool doesn't work/Lo strumento non funziona", callback_data="problema_tool")],
        [InlineKeyboardButton("2]  I don't understand how to use it/Non capisco come usarlo", callback_data="problema_uso")],
        [InlineKeyboardButton("3]  Tool error problem/ Problema di errore dello strumento", callback_data="problema_pagamento")],
    ]

    await update.message.reply_text(
        "<b>Customer Support</b>\n\nSelect your issue:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SCEGLI_PROBLEMA


async def assistance_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END

    await query.answer()
    user = query.from_user
    label = LABEL_PROBLEMI.get(query.data or "", query.data or "unknown")

    await query.edit_message_text(
        f"<b>Request received!</b>\n\nIssue: <b>{label}</b>\n\n"
        "Thank you! The administrator will contact you soon.",
        parse_mode=ParseMode.HTML,
    )

    username = f"@{user.username}" if user.username else "N/A"
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "🔔 <b>NEW SUPPORT REQUEST</b>\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 Username: {username}\n"
            f"🔢 ID: <code>{user.id}</code>\n\n"
            f"🛠 Issue: {label}"
        ),
        parse_mode=ParseMode.HTML,
    )
    logger.info("Support from %s — %s", user.full_name, label)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


# ================= ADMIN =================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    user = update.effective_user
    if user is None or user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("You are not authorized for this command.")
        return
    await update.message.reply_text(
        "🔧 <b>Admin Panel</b>\n\nBot is running \nYou will receive notifications for every request.",
        parse_mode=ParseMode.HTML,
    )


# ================= INIT =================

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("collaboration", "Request collaboration"),
        BotCommand("assistance", "Get support"),
    ])


# ================= MAIN =================

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("assistance", assistance_start)],
        states={
            SCEGLI_PROBLEMA: [CallbackQueryHandler(assistance_choice, pattern="^problema_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("collaboration", collaboration))
    app.add_handler(conv)
    app.add_handler(CommandHandler("admin", admin_panel))

    logger.info("✅ Bot started — listening...")
    app.run_polling()


if __name__ == "__main__":
    main()