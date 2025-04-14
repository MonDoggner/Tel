import requests
# Use config.py file to secure this data
# Use .gitignore file to secure config.py XD (It is important)
from config import API_KEY, TELEGRAM_BOT_TOKEN, WALLET_ID 
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater

WALLET_API_URL = f'https://api.bitgo.com/v2?access_token={API_KEY}'  # Include API key in the URL


# In-memory storage for the sake of example
users = {}  # {telegram_id: {'wallet_id': ..., 'balance': ..., 'referrals': []}}
referral_rewards = 1  # Amount awarded for each successful referral in USD

def register_user(user_id):
    wallet_id = "new_wallet_id"  # Replace with actual wallet creation logic 
    users[user_id] = {'wallet_id': wallet_id, 'balance': 0, 'referrals': []} 
    # Not bad, really

def get_balance(user_id):
    return users[user_id]['balance']

def update_balance(user_id, amount):
    users[user_id]['balance'] += amount

def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in users:
        register_user(user_id)
        
    if len(context.args) != 1:
        update.message.reply_text("Usage: /refer <telegram_id>")
        return

    referred_user_id = context.args[0]

    if referred_user_id not in users:
        register_user(referred_user_id)
        
    # Update referral counts and rewards
    users[user_id]['referrals'].append(referred_user_id)
    update_balance(user_id, referral_rewards)
    update.message.reply_text(f"You have referred user {referred_user_id} and earned ${referral_rewards}!")

def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in users:
        register_user(user_id)
    
    balance = get_balance(user_id)
    update.message.reply_text(f"Your current balance is: ${balance:.2f}")

def transfer(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in users:
        register_user(user_id)

    balance = get_balance(user_id)
    
    if balance < 1:
        update.message.reply_text("Referral limit not reached. You need a minimum balance of $1 to transfer.")
        return

    # Call the wallet API to send the total balance to the BitGo wallet address
    response = requests.post(
        f"{WALLET_API_URL}/wallet/{WALLET_ID}/tx/send", 
        json={
            'recipients': [
                { 
                    'address': WALLET_ID,
                    'amount': balance * 1e8 
                }
            ]
        })  # Amount in satoshis
    # I think it will be more readable
    
    if response.status_code == 200:
        update.message.reply_text(f"You have successfully transferred ${balance:.2f} to your BitGo wallet.")
        update_balance(user_id, -balance)  # Deduct the transferred amount
    else:
        update.message.reply_text("Transfer failed. Please try again later.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)  # Use the hardcoded bot token 
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("refer", refer))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("transfer", transfer))  # New command for transferring earnings

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    # Interesting project. But be carefull with importand variables like tokens, api keys and so on. 
    # One day it can cause many problems on the real project
    # Good luck XD
