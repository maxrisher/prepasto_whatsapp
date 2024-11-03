import pandas as pd
import pytz
from datetime import datetime, timedelta
# import matplotlib as plt

def draw_diary_plot(diary_df, user_tz_string):
    user_tz = pytz.timezone(user_tz_string)
    end_datetime = datetime.now(user_tz)
    end_date = end_datetime.date()
    start_date = end_date - timedelta(days=14)

    date_range = pd.date_range(start=start_date, end=end_date)
    plt_df = pd.DataFrame({'date': date_range})

    diary_df['date'] = pd.to_datetime(diary_df['date']).dt.date
    plt_df['date'] = plt_df['date'].dt.date
    plt_df = plt_df.merge(diary_df, on='date', how='left')

    plt_df['calorie_completion'] = 100 * plt_df.calories / plt_df.calorie_goal
    plt_df['protein_completion'] = 100 * plt_df.protein / plt_df.protein_goal
    plt_df['carbs_completion'] = 100 * plt_df.carbs / plt_df.carb_goal
    plt_df['fat_completion'] = 100 * plt_df.fat / plt_df.fat_goal
    print(plt_df)

    # _plot_diary_df(plt_df)

    print(plt_df)

def _plot_diary_df(df):
    # Create the scatter plot
    plt.figure(figsize=(12, 6))

    # Plot each completion metric
    plt.scatter(df['date'], df['calorie_completion'], label='Calories', alpha=0.7, s=100, c='blue')
    plt.plot(df['date'], df['calorie_completion'], alpha=0.7, c='blue')

    plt.scatter(df['date'], df['protein_completion'], label='Protein', alpha=0.7, s=100, c='green')
    plt.plot(df['date'], df['protein_completion'], alpha=0.7, c='green')

    plt.scatter(df['date'], df['carbs_completion'], label='Carbs', alpha=0.7, s=100, c='orange')
    plt.plot(df['date'], df['carbs_completion'], alpha=0.7, c='orange')

    plt.scatter(df['date'], df['fat_completion'], label='Fat', alpha=0.7, s=100, c='red')
    plt.plot(df['date'], df['fat_completion'], alpha=0.7, c='red')

    # Add padding of 12 hours to either side of the date range
    padding = timedelta(days=1)
    plt.xlim(df['date'].min() - padding, df['date'].max() + padding)

    # Customize the plot
    plt.title('Nutrition Goal Completion (Last 14 Days)', pad=20)
    plt.xlabel('Date')
    plt.ylabel('Percent of goal (%)')

    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

    # Add horizontal line at 100%
    plt.axhline(y=100, color='black', linestyle='--', alpha=0.7)

    # Add legend
    plt.legend()

    # Add grid for better readability
    plt.grid(True, alpha=0.3)

    # Set y-axis limits to show 0-120% (to give some padding above 100%)
    plt.ylim(20, 150)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Show the plot
    plt.show()