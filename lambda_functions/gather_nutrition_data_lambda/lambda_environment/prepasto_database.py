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