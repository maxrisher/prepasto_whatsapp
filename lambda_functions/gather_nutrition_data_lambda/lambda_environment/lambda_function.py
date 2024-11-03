import json
import os
import psycopg2
import pandas as pd
import tempfile

from prepasto_database import get_user_timezone, get_user_diary_df, get_user_dish_df, make_year_diary_df
from data_visualization import save_diary_plot
from web_requests import upload_to_whatsapp, send_to_django

WHATSAPP_PHONE_NUMBER_ID=''

def lambda_handler(event, context):
    """
    AWS Lambda handler that creates an Excel file and uploads it to WhatsApp servers.
    Uses temporary file system for file operations.
    """
    try:
        user_whatsapp_id = event['user_whatsapp_id']
        print(user_whatsapp_id)

        #Download and generate data
        prepasto_db_connection = psycopg2.connect(os.getenv('DATABASE_URL'))
        user_timezone_str = get_user_timezone(prepasto_db_connection, user_whatsapp_id)
        print(user_timezone_str)

        diary_df = get_user_diary_df(prepasto_db_connection, user_whatsapp_id, user_timezone_str)
        print(diary_df)
        print(diary_df.to_csv())
        year_diary_df = make_year_diary_df(diary_df)
        print(year_diary_df)
        print(year_diary_df.to_csv())

        dish_df = get_user_dish_df(prepasto_db_connection, user_whatsapp_id, user_timezone_str)

        print(dish_df)
        with tempfile.TemporaryDirectory() as tmp_dir:
            diary_path = os.path.join(tmp_dir, 'daily_totals.xlsx')
            year_diary_df.to_excel(diary_path, index=False)

            dish_path = os.path.join(tmp_dir, 'full_food_data.xlsx')
            dish_df.to_excel(dish_path, index=False)

            plot_path = os.path.join(tmp_dir, 'two_week_nutrition.png')
            save_diary_plot(diary_df, user_timezone_str, plot_path)
            
            payload = {
                'nutrition_data_requester_whatsapp_wa_id': user_whatsapp_id,
                'diary_xlsx': upload_to_whatsapp(diary_path, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'nutrition_xlsx_ytd_id': upload_to_whatsapp(dish_path, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'nutrition_bar_chart_id': upload_to_whatsapp(plot_path, 'image/png')
            }

            print(payload)
        prepasto_db_connection.close()

        get_django_url(context)
        send_to_django(payload)
        return {'statusCode': 200}
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    finally:
        if 'conn' in locals():
            prepasto_db_connection.close()
    diary_df = get_user_diary_df(prepasto_db_connection, user_whatsapp_id)
    dish_df = get_user_dish_df(prepasto_db_connection, user_whatsapp_id, user_timezone_str)
    diary_plot_image = draw_diary_plot(diary_df, user_timezone_str)

    #Save files to the tmp/
    diary_xlsx_path = save_df_to_tmp_xlsx(diary_df, 'diaries.xlsx')
    dish_xlsx_path = save_df_to_tmp_xlsx(dish_df, 'dishes.xlsx')
    diary_plot_path = save_to_tmp(diary_plot_image, 'two_week_diaries.png')

    #Upload files to whatsapp
    whatsapp_media_ids = {}
    whatsapp_media_ids['diary_xlsx_whatsapp_id'] = upload_to_whatsapp(diary_xlsx_path)
    whatsapp_media_ids['dish_xlsx_whatsapp_id'] = upload_to_whatsapp(dish_xlsx_path)
    whatsapp_media_ids['diary_plot_whatsapp_id'] = upload_to_whatsapp(diary_plot_path)

    #Pass media IDs to django
    django_url = get_django_url(context)
    send_to_django(django_url, whatsapp_media_ids)

    #Clean up
    os.remove(tmp_path)
    prepasto_db_connection.close()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Nutrition report generated and uploaded successfully',
            'excel_media_id': excel_media_id,
            'image_media_id': image_media_id
        })
    }
    
def get_django_url(context):
    """
    Sets the django site url depending on which alias the function has
    """
    print(context)
    alias_str = get_lambda_alias(context.invoked_function_arn)

    if alias_str == 'production':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PRODUCTION_RAILWAY_PUBLIC_DOMAIN') #should read from parameter store

    elif alias_str == 'stagingAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('STAGING_RAILWAY_PUBLIC_DOMAIN')

    elif alias_str == 'pullRequestAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PULL_REQUEST_RAILWAY_PUBLIC_DOMAIN') #should read the latest PR
    
    print("Alias is "+alias_str+", so I am sending lambda result to "+ os.getenv('RAILWAY_PUBLIC_DOMAIN'))

def get_lambda_alias(arn):
    parts = arn.split(':')

    if len(parts) > 7:
        return parts[7]
    else:
        return 'production' #default to production alias if there is no alias

lambda_handler({'user_whatsapp_id': '17204768288'}, 'test')