import random
import json
from flask import Flask, request, jsonify

#Defines what events the api will accept
valid_events = {"coin_flip", "dice_roll", "card_deck"}
#Limits the maximum number of times the simulator can be used
max_runs = 1000

#Constants for deck of cards to work
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
standard_deck = [f"{rank} of {suit}" for suit in suits for rank in ranks]

#Initialise the flask instance
app = Flask(__name__)

def input_params(data):   #Validates incoming user requests
                          #and raises any invalid or missing data

    if not data:
        raise ValueError("Request body must contain variables")
    
    #Checks that input contains all the required fields
    required_fields = ['event_type', 'num_runs', 'odds_parameters']
    if not all(field in data for field in required_fields):
        raise ValueError("Missing required fields: event type, number of runs and odds parameters")
    
    #Converts num run input to int
    try:
        num_runs = int(data['num_runs'])
    except ValueError:
        raise ValueError("number of runs must be an integer")
    
    #Ensures user hasn't exceeded allowed number of runs
    if num_runs <= 0 or num_runs > max_runs:
        raise ValueError(f"number runs must be between 1 and 1000")
    
    event_type = data['event_type']
    odds_params = data['odds_parameters']

    #Ensures a defined event has been selected
    if event_type not in valid_events:
        raise ValueError(f"Invalid event type, must be one of: {', '.join(valid_events)}")
    
    #Validation for each specific event
    if event_type == "coin_flip":
        target = str(odds_params).lower()
        if target not in ['heads', 'tails']:
            raise ValueError("Coin flip odds parameters must be either heads or tails")
        
    elif event_type == "dice_roll":
        try:
            target = int(odds_params)
            if target < 1 or target > 6:
                raise ValueError("Dice roll odds parameters must be an integer value between 1 and 6")
        except (TypeError, ValueError):
            raise ValueError("Dice roll odds parameter must be a single integer between 1 and 6")
    
    elif event_type == "card_deck":
        if not isinstance(odds_params, str) or not odds_params.strip():
            raise ValueError("Card deck odds parameters must specify the card or characteristics e.g. King of Hearts")

    #Returns cleaned params
    return {
        'event_type': event_type,
        'num_runs': num_runs,
        'odds_parameters': data['odds_parameters']
    }

def calculate_probability(valid_params): #Executed the simulator based off validated inputs

    event_type = valid_params['event_type']
    num_runs = valid_params['num_runs']
    odds_params = valid_params['odds_parameters']
    success_count = 0
    theoretical_prob = 0.0

    if event_type == "coin_flip":
        target_outcome = str(odds_params).lower()
        theoretical_prob = 0.5
    
        #Simulation Loop
        for _ in range(num_runs):
            #Generates a float between 0.0 and 1.0 if it is <0.5 it is treated as head
            is_heads = random.random() < 0.5

            #Checks if the simulation matches the specified outcome
            if(is_heads and target_outcome == 'heads') or (not is_heads and target_outcome == 'tails'):
                success_count += 1

    elif event_type == "dice_roll":
        target_outcome = int(odds_params)
        theoretical_prob = 1.0/ 6.0

        for _ in range(num_runs):
            trial_result = random.randint(1, 6)

            #Checks the target outcome is valid
            if trial_result == target_outcome:
                success_count += 1

    elif event_type == "card_deck":
        target_outcome = str(odds_params).title()
        theoretical_prob = 1.0 / 52.0

        for _ in range(num_runs):
            #Simulate drawing one card randomly from the deck
            drawn_card = random.choice(standard_deck)

            if drawn_card == target_outcome:
                success_count += 1

    #Final result calculation
    if num_runs == 0:
        empirical_probability = 0.0
    else: 
        empirical_probability = success_count / num_runs
    return {
        "event_type": event_type,
        "total_runs": num_runs,
        "target_outcome": odds_params,
        "success_count": success_count,
        "failure_count": num_runs - success_count,
        "empirical_probability": round(success_count / num_runs, 6),
        "theoretical_probability": round(theoretical_prob, 6)
    }

#Flask route definition
@app.route('/api/v1/simulate', methods=['POST'])
def simulate():
    #API endpoint to handle requests

    #Checks the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request body"}), 400
    
    data = request.get_json()

    try:
        valid_params = input_params(data)
        results = calculate_probability(valid_params)
        return jsonify(results), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An unexpected server error occured"}), 500

if __name__ == '__main__':
    app.run(debug=True)