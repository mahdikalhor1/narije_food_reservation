import requests
import argparse
import datetime
import time
import asyncio


def get_bearer_token(username, password):
    url = "https://api.narijeh.com/v1/Login"
    headers = {"content-type": "application/json"}
    data = {"mobile": username, "password": password, "panel": "user"}
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    if response.status_code == 200:
        return response_data["token"]
    else:
        print("Failed to get token:", response_data["message"])
        exit()


def get_reserves(token, date):
    url = f"https://api.narijeh.com/user/reserves?fromDate={date}&toDate={date}"
    headers = {"authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()


async def reserve_food(token, date, food):
    url = "https://api.narijeh.com/user/reserves"
    headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}
    data = [{"datetime": date, "reserves": [{"foodId": food["foodId"], "qty": 1, "foodType": 0}]}]
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully reserved {food['food']} for {date}.")
    else:
        print(f"Failed to reserve food: {response.json()['message']}, date: {date}")
    time.sleep(10)


def display_and_choose_food(reserves_list):
    print("Available foods:")
    for i, food in enumerate(reserves_list, start=1):
        print(f"{i}. {food['food']}")
    while True:
        choice = input("Choose an option (1-{0}): ".format(len(reserves_list)))
        try:
            choice = int(choice)
            if 1 <= choice <= len(reserves_list):
                chosen_food = reserves_list[choice - 1]
                return chosen_food
            else:
                print("Invalid choice. Please choose a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")


async def main(username, password, include_thursdays, lazy_mode):
    token = get_bearer_token(username, password)
    start_date = datetime.datetime.today()
    reserves = []
    for day in range(36):  # For today until 35 days later
        current_date = start_date + datetime.timedelta(days=day)
        current_date_str = current_date.strftime("%Y-%m-%dT00:00:00")

        if current_date.weekday() == 4 and not include_thursdays:
            print(f"Skipping Thursday: {current_date_str}")
            continue
        # Skip Fridays
        if current_date.weekday() == 5:
            continue

        reserves_response = get_reserves(token, current_date_str)

        if reserves_response["status"] == "OK":
            reserves_list = reserves_response["data"]
            if reserves_list and reserves_list[0]["reserves"]:
                if lazy_mode:
                    chosen_food = reserves_list[0]["reserves"][0]
                else:
                    chosen_food = display_and_choose_food(reserves_list[0]["reserves"])

                reserves.append(asyncio.create_task(reserve_food(token, current_date_str, chosen_food)))
            else:
                print(f"No reserves available for {current_date_str}.")
        else:
            print(f"Failed to get reserves: {reserves_response['message']}, date: {current_date_str}")
    await asyncio.gather(*reserves)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reserve food via API.")
    parser.add_argument("--username", required=True, help="Your username (mobile number).")
    parser.add_argument("--password", required=True, help="Your password.")
    parser.add_argument(
        "--include-thursdays", action="store_true", help="Include Thursdays in the reservation process."
    )
    parser.add_argument(
        "--lazy-mode", action="store_true", help="Enable lazy mode: reserve only the first available food each day."
    )

    args = parser.parse_args()
    asyncio.run(main(args.username, args.password, args.include_thursdays, args.lazy_mode))
