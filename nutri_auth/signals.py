from django.dispatch import Signal
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random

otp_signal = Signal()


def generate_otp():
    return random.randint(100000, 999999)

def handle_otp_signal(sender, **kwargs):
    user_data = kwargs.get('user_data')
    email = user_data.get('email')

    otp = generate_otp()
    print(otp)

    user_data['otp'] = otp
    user_data['otp_generated_time'] = timezone.now().isoformat()

    try:
        send_mail(
            'Your OTP Code',
            f'Your OTP for account verification is {otp}.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

otp_signal.connect(handle_otp_signal)
