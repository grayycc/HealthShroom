def calculate_bmr(gender, age, weight, height):
    """
    Calculate Basal Metabolic Rate (BMR) using the Harris-Benedict Equation.
    Args:
    - gender (str): "M" for male, "F" for female.
    - age (int): Age in years.
    - weight (float): Weight in kilograms.
    - height (float): Height in centimeters.

    Returns:
    - float: BMR value.
    """
    if gender.upper() == "M":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender.upper() == "F":
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        raise ValueError("Invalid gender. Use 'M' for male or 'F' for female.")


def calculate_calories_per_meal(age, weight, height, gender, goal_weight, time_in_months, meals_per_day=3, goal="lose"):
    """
    Calculate the calories a person should consume per meal to lose or gain weight.

    Args:
    - age (int): Age in years.
    - weight (float): Current weight in kilograms.
    - height (float): Height in centimeters.
    - gender (str): "M" for male, "F" for female.
    - goal_weight (float): Goal weight in kilograms.
    - time_in_months (int): Time to achieve goal in months.
    - meals_per_day (int): Number of meals per day.
    - goal (str): "lose" for weight loss, "gain" for weight gain.

    Returns:
    - dict: Calorie recommendations for breakfast, lunch, and dinner.
    """
    bmr = calculate_bmr(gender, age, weight, height)

    activity_multiplier = 2.4  
    daily_calorie_needs = bmr * activity_multiplier

    total_weight_change = abs(weight - goal_weight)
    total_calories_to_adjust = total_weight_change * 7700  
    days = time_in_months * 30  
    daily_calorie_adjustment = total_calories_to_adjust / days

    if goal.lower() == "lose":
        daily_calorie_target = daily_calorie_needs - daily_calorie_adjustment
    elif goal.lower() == "gain":
        daily_calorie_target = daily_calorie_needs + daily_calorie_adjustment
    else:
        raise ValueError("Invalid goal. Use 'lose' for weight loss or 'gain' for weight gain.")

    calories_per_meal = daily_calorie_target / meals_per_day
    return {
        "Breakfast": calories_per_meal * 0.3,  
        "Lunch": calories_per_meal * 0.4,     
        "Dinner": calories_per_meal * 0.3    
    }
