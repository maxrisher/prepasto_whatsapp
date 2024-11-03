import pandas as pd
import pytz
from datetime import datetime, timedelta

def get_user_timezone(conn, user_whatsapp_waid):
    """Given a connection and a user_whatsapp_waid, return the user's timezone string"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT time_zone_name
        FROM whatsapp_bot_whatsappuser
        WHERE whatsapp_wa_id = %s
    """, (user_whatsapp_waid,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_user_diary_df(conn, user_whatsapp_waid, user_timezone_str):
    user_tz = pytz.timezone(user_timezone_str)
    end_date = datetime.now(user_tz)
    start_date = end_date - timedelta(days=365)

    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.local_date,
               d.calorie_goal,
               d.protein_g_goal,
               d.fat_g_goal,
               d.carb_g_goal,
               COALESCE(SUM(m.calories), 0) as calories,
               COALESCE(SUM(m.protein), 0) as protein,
               COALESCE(SUM(m.carbs), 0) as carbs,
               COALESCE(SUM(m.fat), 0) as fat
        FROM whatsapp_bot_whatsappuser wu
        LEFT JOIN main_app_diary d ON wu.whatsapp_wa_id = d.whatsapp_user_id
        LEFT JOIN main_app_meal m ON d.id = m.diary_id
        WHERE wu.whatsapp_wa_id = %s
        AND d.local_date BETWEEN %s AND %s
        GROUP BY d.local_date,
                 d.calorie_goal,
                 d.protein_g_goal,
                 d.fat_g_goal,
                 d.carb_g_goal
        ORDER BY d.local_date
    """, (user_whatsapp_waid, start_date, end_date))

    nutrition_data = cursor.fetchall()
    df = pd.DataFrame(nutrition_data, columns=['date', 'calorie_goal', 'protein_goal', 'fat_goal', 'carb_goal', 'calories', 'protein', 'carbs', 'fat'])
    return df

def get_user_dish_df(conn, user_whatsapp_waid, user_timezone_str):
    user_tz = pytz.timezone(user_timezone_str)
    end_date = datetime.now(user_tz).date()
    start_date = end_date.replace(month=1, day=1)  # January 1st of current year

    cursor = conn.cursor()
    cursor.execute("""
            SELECT 
                d.local_date,
                m.created_at_utc,
                m.description,
                dish.name,
                dish.grams,
                dish.calories,
                dish.protein,
                dish.carbs,
                dish.fat,
                dish.usda_food_data_central_food_name,
                dish.usda_food_data_central_id,
                dish.nutrition_citation_website
            FROM main_app_dish dish
            JOIN main_app_meal m ON dish.meal_id = m.id
            JOIN main_app_diary d ON m.diary_id = d.id
            WHERE dish.whatsapp_user_id = %s
            AND d.local_date >= %s
            AND d.local_date <= %s
            ORDER BY d.local_date DESC, m.created_at_utc
        """, (user_whatsapp_waid, start_date, end_date))

    dish_data = cursor.fetchall()
    df = pd.DataFrame(dish_data, columns=[
            'date',
            'utc_time',
            'meal',
            'name',
            'grams',
            'calories',
            'protein',
            'carbs',
            'fat',
            'usda_food_name',
            'usda_food_id',
            'source'
        ])
    df['utc_time'] = pd.to_datetime(df['utc_time'], utc = True)
    df['time'] = df['utc_time'].dt.tz_convert(user_timezone_str)
    df['time'] = df['time'].dt.round('min')

    df['time'] = df['time'].dt.time
    # df['time'] = df['time'].dt.round('min')
    # df = df.drop('utc_time')
    df = df[[
        'date',
        'time',
        'meal',
        'name',
        'grams',
        'calories',
        'protein',
        'carbs',
        'fat',
        'usda_food_name',
        'usda_food_id',
        'source'
    ]]
    return df

def make_year_diary_df(diary_df):
    # Ensure date column is datetime
    diary_df['date'] = pd.to_datetime(diary_df['date'])
    
    # Get the most recent date
    max_date = diary_df['date'].max()

    # Create date range from January 1st of the same year to the most recent date
    start_date = pd.Timestamp(f"{max_date.year}-01-01")
    date_range = pd.date_range(start=start_date, end=max_date, freq='D')
    
    # Create empty DataFrame with all dates
    complete_df = pd.DataFrame({'date': date_range})
    
    # Merge with original diary entries
    result_df = pd.merge(complete_df, diary_df, on='date', how='left')

    return result_df