import json
from freezegun import freeze_time
from unittest.mock import patch
import uuid

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.utils import timezone

from whatsapp_bot.models import WhatsappUser, WhatsappMessage, MessageType
from main_app.models import Meal, Dish, Diary
import whatsapp_bot.tests.mock_whatsapp_webhook_data as webhkdta

class WhatsappUserMessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp-webhook')
        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/Denver'
        )
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

        self.diary = Diary.objects.create(
            whatsapp_user=self.whatsapp_user,
            local_date=self.whatsapp_user.current_date
        )

        self.meal = Meal.objects.create(
            id = uuid.UUID('f2e3b84f-c29d-4e03-bcfb-f4ca6918a64e'),
            whatsapp_user=self.whatsapp_user,
            diary=self.diary,
            local_date=self.whatsapp_user.current_date,
            calories=500,
            carbs=60,
            fat=20,
            protein=30,
            description="A meal description, e.g., Grilled chicken with rice and veggies"
        )

        self.dish = Dish.objects.create(
            whatsapp_user=self.whatsapp_user,
            meal=self.meal,
            name='Grilled Chicken',
            matched_thalos_id=12345,
            usda_food_data_central_id=67890,
            usda_food_data_central_food_name="Chicken, broilers or fryers, breast, meat only, cooked, grilled",
            grams=150,
            calories=200,
            carbs=0,
            fat=5,
            protein=40,
            usual_ingredients=['Chicken breast', 'Salt', 'Pepper'],
            state='grilled',
            qualifiers=['no skin'],
            confirmed_ingredients=['Chicken breast'],
            amount='150 grams',
            similar_dishes=['Roasted Chicken', 'Fried Chicken'],
            fndds_categories=[100],
            fndds_and_sr_legacy_google_search_results=[123456]
        )

        WhatsappMessage.objects.create(
            whatsapp_message_id='test_meal_button',
            sent_to=self.whatsapp_user.whatsapp_wa_id,
            sent_from=settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
            message_type='PREPASTO_MEAL_BUTTON',
        )

    @patch('whatsapp_bot.whatsapp_message_handler.send_to_lambda')
    def test_text_message(self, mock_send_to_lambda):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.create_meal_for_user_text),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CREATING_MEAL_TEXT.value).count(), 1)
        mock_send_to_lambda.assert_called_once_with({
            'sender_whatsapp_wa_id': '17204768288',
            'sender_message': 'Peach'
        })

    def test_photo_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_image_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_IMAGE.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_IS_TEXT_ONLY.value).count(), 1)

    def test_video_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_video_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_VIDEO.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_IS_TEXT_ONLY.value).count(), 1)

    def test_reaction_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_reacts_to_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_contact_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_contacts_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_document_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_document_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_location_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_generic_location_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_reply_button_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_generic_button_press),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(sent_from=self.whatsapp_user.whatsapp_wa_id).count(), 1)

    def test_delete_button_press_meal_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.delete_existing_meal_button_press),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_DELETE_REQUEST.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_MEAL_DELETED_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_DIARY_TEXT.value).count(), 1)
        self.assertFalse(Meal.objects.filter(id=self.meal.id).exists())

    def test_delete_button_press_meal_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.delete_not_existing_meal_button_press),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.USER_DELETE_REQUEST.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ERROR_TEXT.value).count(), 1)

    @freeze_time(timezone.now())
    def test_status_update_sent_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.django_whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )

        self.assertIsNone(message.sent_at)

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_sent),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertIsNotNone(message.sent_at)
        self.assertEqual(message.sent_at, timezone.now())

    def test_status_update_sent_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_sent),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @freeze_time(timezone.now())
    def test_status_update_failed_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )

        self.assertIsNone(message.failed_at)

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_failed),
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
            data=json.dumps(webhkdta.message_status_update_failed),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

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
            data=json.dumps(webhkdta.message_status_update_read),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_read_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_read),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_delivered_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_MEAL_BUTTON.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_delivered),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_read_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_delivered),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

class NonWhatsappUserMessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp-webhook')
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

    def test_text_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.create_meal_for_user_text),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)

    def test_photo_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_image_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)

    def test_video_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_video_message),
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
            data=json.dumps(webhkdta.whatsapp_webhook_user_reacts_to_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)

    def test_contact_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_contacts_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)


    def test_document_message(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_document_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)
    
    def test_generic_location_message_from_new_user(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_generic_location_message),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_LOCATION_SHARE.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONFIRM_TIMEZONE_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 2)

    def test_generic_button_reply_from_new_user(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.whatsapp_webhook_user_generic_button_press),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)

    def test_reply_button_message_confirm(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.location_confirmation),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TIMEZONE_CONFIRMATION.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONFIRM_USER_TEXT.value).count(), 3)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONTACT_CARD.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 5)

    def test_reply_button_message_cancel(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.location_cancel),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_TIMEZONE_CANCELLATION.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_TRY_AGAIN.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 3)

    def test_location_button_press(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.location_share),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_LOCATION_SHARE.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_CONFIRM_TIMEZONE_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 2)

    def test_delete_button_press(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.delete_not_existing_meal_button_press),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.NEW_USER_MESSAGE_GENERIC.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.filter(message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value).count(), 1)
        self.assertEqual(WhatsappMessage.objects.count(), 4)

    @freeze_time(timezone.now())
    def test_status_update_sent_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.django_whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value
        )

        self.assertIsNone(message.sent_at)

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_sent),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertIsNotNone(message.sent_at)
        self.assertEqual(message.sent_at, timezone.now())

    def test_status_update_sent_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_sent),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.count(), 0)

    @freeze_time(timezone.now())
    def test_status_update_failed_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.django_whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value
        )

        self.assertIsNone(message.failed_at)

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_failed),
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
            data=json.dumps(webhkdta.message_status_update_failed),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsappMessage.objects.count(), 0)

    def test_status_update_read_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.django_whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_read),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_read_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_read),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_delivered_message_exists(self):
        message = WhatsappMessage.objects.create(
            whatsapp_message_id='test_message_id',
            whatsapp_user=self.django_whatsapp_user,
            sent_to='17204768288',
            sent_from='14153476103',
            message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value
        )
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_delivered),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_status_update_delivered_message_not_exists(self):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhkdta.message_status_update_delivered),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)