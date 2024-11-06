import requests
import pandas as pd

def get_option_chain_data(symbol: str, expiration: str, api_key: str) -> pd.DataFrame:
    
    url = f"https://www.alphavantage.co/query"
    
    params = {
        'function': 'HISTORICAL_OPTIONS',
        'symbol': symbol,
        'date': expiration,
        'apikey': api_key
    }
     
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return pd.DataFrame()  
    
    data = response.json()
    
    if 'data' not in data or not data['data']:
        print("No results found in the response.")
        return pd.DataFrame() 

    max_bid_by_strike = {}
    max_ask_by_strike = {}

    # logic
    for option in data['data']:
        strike_price = float(option.get('strike', 0))
        bid_price = float(option.get('bid', 0))
        ask_price = float(option.get('ask', 0))
        option_type = option.get('type', "").lower()

        if option_type == "put":
            if strike_price not in max_bid_by_strike:
                max_bid_by_strike[strike_price] = bid_price
            else:
                max_bid_by_strike[strike_price] = max(max_bid_by_strike[strike_price], bid_price)

        # Updating the max ask for call options
        elif option_type == "call":
            if strike_price not in max_ask_by_strike:
                max_ask_by_strike[strike_price] = ask_price
            else:
                max_ask_by_strike[strike_price] = max(max_ask_by_strike[strike_price], ask_price)

    option_data = []

    for strike, max_bid in max_bid_by_strike.items():
        option_data.append([symbol, strike, "PE", max_bid])

    for strike, max_ask in max_ask_by_strike.items():
        option_data.append([symbol, strike, "CE", max_ask])

    df = pd.DataFrame(option_data, columns=["instrument_name", "strike_price", "side", "bid/ask"])
    df.sort_values(by='strike_price',inplace=True) # inplace means it doesn't create new copy to sort
    return df

api_key = "BLVMJMWU6U0BSLHP" 
data = get_option_chain_data("IBM", "2024-10-30", api_key)
print(data)
