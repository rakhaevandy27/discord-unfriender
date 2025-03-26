import requests
import time
import os
import pwinput
from datetime import datetime, timezone

def get_token():
    return pwinput.pwinput("Enter your Discord token: ", mask="*").strip()

def get_account_info(token):
    headers = {"Authorization": token}
    response = requests.get("https://discord.com/api/users/@me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        discord_epoch = 1420070400000
        user_id_int = int(user_data["id"])
        timestamp = (user_id_int >> 22) + discord_epoch
        creation_date = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        print("\n==== ACCOUNT INFO ====")
        print(f"Username   : {user_data['username']}#{user_data['discriminator']}")
        print(f"User ID    : {user_data['id']}")
        print(f"Global Name: {user_data.get('global_name', 'N/A')}")
        print(f"Created On : {creation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("======================\n")
        return True
    else:
        print("Error: Invalid token or failed to retrieve account info.")
        return False

def get_friends(token):
    headers = {"Authorization": token}
    response = requests.get("https://discord.com/api/users/@me/relationships", headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch friends list - Status: {response.status_code}")
        return []
    return response.json()

def delete_friend(user, token):
    user_id = user["id"]
    url = f"https://discord.com/api/users/@me/relationships/{user_id}"
    headers = {"Authorization": token}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"✅ Friend deleted: {user['username']}#{user['discriminator']} ({user.get('global_name', 'N/A')})")
        return True
    else:
        print(f"❌ Failed to delete {user['username']}#{user['discriminator']} - Status: {response.status_code}")
        return False

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        print(f"⏳ Next batch in {remaining} seconds...", end="\r")
        time.sleep(1)
    print("\n")

def delete_friends(token, batch_size, batch_interval):
    while True:
        friends_list = get_friends(token)
        total_friends = len(friends_list)
        if total_friends == 0:
            print("✅ No more friends to delete. Exiting...")
            break
        print(f"\n📌 Total friends remaining: {total_friends}")
        batch = friends_list[:batch_size]
        for friend in batch:
            delete_friend(friend["user"], token)
        if len(batch) < batch_size:
            print("✅ No more friends to delete. Exiting...")
            break
        print(f"⏳ Waiting {batch_interval} seconds before next batch...\n")
        countdown(batch_interval)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("==== 🚀 Discord Friend Remover ====")
    token = get_token()
    if not get_account_info(token):
        print("Exiting due to invalid token.")
        return
    friends_list = get_friends(token)
    total_friends = len(friends_list)
    print(f"📌 Total friends: {total_friends}\n")
    if total_friends == 0:
        print("✅ No friends to delete. Exiting...")
        return
    batch_size = int(input("🔢 Enter how many friends to delete per batch: "))
    batch_interval = int(input("⏳ Enter the interval (seconds) between each batch: "))
    print(f"\n⚠️ WARNING: You are about to delete {batch_size} friends per batch with {batch_interval} seconds between each batch.")
    confirm = input("❓ Are you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm == "yes":
        delete_friends(token, batch_size, batch_interval)
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    main()