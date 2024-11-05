import requests
import pandas as pd

def get_option_chain_data(symbol: str, expiration: str, api_key: str) -> pd.DataFrame:
    """
    Fetch option chain data for a specific instrument on a given expiry date.

    Parameters:
    - symbol (str): Ticker symbol of the instrument (e.g., "AAPL").
    - expiration (str): Expiry date of the options in "YYYY-MM-DD" format.
    - api_key (str): API key for accessing the API.

    Returns:
    - pd.DataFrame: A DataFrame with columns: instrument_name, strike_price, side, bid/ask.
    """
    # Define URL with the specified parameters
    url = f"https://www.alphavantage.co/query"
    
    # Define query parameters
    params = {
        'function': 'HISTORICAL_OPTIONS',
        'symbol': symbol,
        'date': expiration,
        'apikey': api_key
    }
     
    headers = {
        'accept': 'application/json'
    }
    
    # Fetch data from the API
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return pd.DataFrame()  # Return an empty DataFrame if request fails
    
    data = response.json()
    
    # Check if the data structure is as expected
    if 'data' not in data or not data['data']:
        print("No results found in the response.")
        return pd.DataFrame()  # Return an empty DataFrame if no data is available

    # Initialize dictionaries to track the highest bid and ask prices for each strike price
    max_bid_by_strike = {}
    max_ask_by_strike = {}

    # Process the options data
    for option in data['data']:
        strike_price = float(option.get('strike', 0))
        bid_price = float(option.get('bid', 0))
        ask_price = float(option.get('ask', 0))
        option_type = option.get('type', "").lower()

        # Update the max bid for put options
        if option_type == "put":
            if strike_price not in max_bid_by_strike:
                max_bid_by_strike[strike_price] = bid_price
            else:
                max_bid_by_strike[strike_price] = max(max_bid_by_strike[strike_price], bid_price)

        # Update the max ask for call options
        elif option_type == "call":
            if strike_price not in max_ask_by_strike:
                max_ask_by_strike[strike_price] = ask_price
            else:
                max_ask_by_strike[strike_price] = max(max_ask_by_strike[strike_price], ask_price)

    # Prepare the final data based on the maximum bid/ask found
    option_data = []

    # Compile the maximum bid prices for "PE" options
    for strike, max_bid in max_bid_by_strike.items():
        option_data.append([symbol, strike, "PE", max_bid])

    # Compile the maximum ask prices for "CE" options
    for strike, max_ask in max_ask_by_strike.items():
        option_data.append([symbol, strike, "CE", max_ask])

    # Convert the list to a DataFrame
    df = pd.DataFrame(option_data, columns=["instrument_name", "strike_price", "side", "bid/ask"])
    df.sort_values(by='strike_price',inplace=True) # inplace means it doesn't create new copy to sort
    return df

# Example usage 
api_key = "BLVMJMWU6U0BSLHP"  # Replace with your actual API key
data = get_option_chain_data("IBM", "2024-10-30", api_key)
print(data)
