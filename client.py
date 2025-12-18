import requests
import json

api_url = "http://127.0.0.1:5000/api/v1/simulate"

def send_request(event_type, num_runs, odds_params):
    #Constructs and sends a POST requests to the API

    data = {
        "event_type": event_type,
        "num_runs": num_runs,
        "odds_parameters": odds_params
    }

    try:
        #Send the POST request
        response = requests.post(api_url, json=data)
    except:
        print("\n Error, connection refused. Ensure flask server is running")

    #Handle any response
    if response.status_code == 200:
        results = response.json()
        print("\n Success, HTTP 200")

        print(f"Target Outcome: {results['target_outcome']}")
        print(f"Total Runs: {results['total_runs']}")
        print(f"Success Count: {results['success_count']}")
        print(f"Failure Count: {results['failure_count']}")
        print(f"Empirical Probability: {results['empirical_probability']}")
        print(f"Theoretical Probability: {results['theoretical_probability']}")

    elif response.status_code == 400:
        error_data = response.json()
        print(f"\n Failure HTTP 400")
        print(f"Error Message: {error_data.get('error', 'Unknown 400 error.')}")
        
    else:
        #Other Server Errors (500)
        print(f"\n SERVER ERROR (HTTP {response.status_code})")
        print(f"Response Text: {response.text}")

if __name__ == '__main__':
    
    # --- Test Case 1: Coin Flip (Success) ---
    send_request("coin_flip", 800, "heads")
    
    # --- Test Case 2: Dice Roll (Success) ---
    send_request("dice_roll", 600, 3)
    
    # --- Test Case 3: Card Deck (Success) ---
    send_request("card_deck", 520, "Ace of Spades")
    
    # --- Test Case 4: Validation Failure (num_runs too high) ---
    send_request("coin_flip", 1001, "tails")
    
    # --- Test Case 5: Validation Failure (Invalid odds_parameters) ---
    send_request("dice_roll", 50, 7)