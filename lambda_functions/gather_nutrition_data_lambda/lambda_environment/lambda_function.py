import json
import os

def lambda_handler(event, context):
    """
    AWS Lambda handler that creates an Excel file and uploads it to WhatsApp servers.
    Uses temporary file system for file operations.
    """
    user_whatsapp_id = event['user_whatsapp_id']

    #Download and generate data
    prepasto_db_connection = get_db_connection()
    user_timezone_str = get_user_timezone(prepasto_db_connection, user_whatsapp_id)
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