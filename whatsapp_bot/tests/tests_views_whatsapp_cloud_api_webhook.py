import json
from datetime import date, datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from whatsapp_bot.models import WhatsappUser, WhatsappMessage, MessageType
from main_app.models import Meal, Dish, Diary
from whatsapp_bot.utils import send_to_lambda
from whatsapp_bot.tests.mock_whatsapp_webhook_data import create_meal_for_user_text

class WhatsappUserMessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp_cloud_api_webhook')
        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/Denver'
        )
        self.meal = Meal.objects.create(
            whatsapp_user=self.whatsapp_user,
            diary=Diary.objects.create(whatsapp_user=self.whatsapp_user, local_date=date.today()),
            local_date=date.today(),
            calories=200,
            carbs=30,
            fat=10,
            protein=3,
            description='1 brownie'
        )
        self.dish = Dish.objects.create(
            whatsapp_user=self.whatsapp_user,
            meal=self.meal,
            name='Brownie',
            matched_thalos_id=12345,
            usda_food_data_central_id=54321,
            usda_food_data_central_food_name='Chocolate brownie',
            grams=100,
            calories=200,
            carbs=30,
            fat=10,
            protein=3,
            usual_ingredients=['flour', 'sugar', 'cocoa'],
            state='baked',
            amount='1 piece',
            similar_dishes=['cookie', 'cake'],
            fndds_categories=[1000, 2000]
        )

    @freeze_time("2023-05-01 12:00:00")
    def test_text_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(create_meal_for_user_text),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_TEXT.value).count(), 1)
        self.assertTrue(send_to_lambda.called)

    def test_photo_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_photo_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_IMAGE.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_IS_TEXT_ONLY.value).count(), 1)

    def test_video_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_video_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_VIDEO.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_IS_TEXT_ONLY.value).count(), 1)

    def test_reaction_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_reaction_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_contact_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_contact_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_document_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_document_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_location_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_location_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_reply_button_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_reply_button_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_delete_button_press_meal_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_delete_button_press(str(self.meal.id))),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_DELETE_REQUEST.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_MEAL_DELETED_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_DIARY_TEXT.value).count(), 1)
        self.assertFalse(Meal.objects.filter(id=self.meal.id).exists())

    def test_delete_button_press_meal_not_exists(self):
        non_existent_meal_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(user_delete_button_press(non_existent_meal_id)),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_DELETE_REQUEST.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ERROR_TEXT.value).count(), 1)

    @freeze_time("2023-05-01 12:00:00")
    def test_status_update_sent_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_sent('test_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertIsNotNone(message.sent_at)
        self.assertEqual(message.sent_at, timezone.now())

    def test_status_update_sent_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_sent('non_existent_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @freeze_time("2023-05-01 12:00:00")
    def test_status_update_failed_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_failed('test_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertIsNotNone(message.failed_at)
        self.assertEqual(message.failed_at, timezone.now())
        self.assertIsNotNone(message.failure_details)

    def test_status_update_failed_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_failed('non_existent_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_status_update_read_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_read('test_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_read_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(status_update_read('non_existent_message_id')),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class NonWhatsappUserMessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp_cloud_api_webhook')

    def test_text_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_text_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_photo_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_photo_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_video_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_video_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_reaction_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_reaction_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        
    def test_contact_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_contact_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_document_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_document_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_location_message_from_new_user(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_location_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_LOCATION_SHARE.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONFIRM_TIMEZONE_BUTTON.value).count(), 1)

    def test_reply_button_message_confirm(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_reply_button_confirm),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TIMEZONE_CONFIRMATION.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONFIRM_USER_TEXT.value).count(), 3)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONTACT_CARD.value).count(), 1)

    def test_reply_button_message_cancel(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_reply_button_cancel),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TIMEZONE_CANCELLATION.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_TRY_AGAIN.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)

    def test_status_update_sent_from_new_user(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_status_update_sent),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_STATUS_UPDATE_SENT.value).count(), 1)

    def test_status_update_failed_from_new_user(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(new_user_status_update_failed),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_STATUS_UPDATE_FAILED.value).count(), 1)