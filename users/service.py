import uuid
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


# #functional approach
# def create_activation_key(email:str):
#     raise NotImplementedError

# def send_user_activation_email(email:str, activation_key:str):
#     raise NotImplementedError


#class approach 
User = get_user_model()
CACHE: dict[uuid.UUID, dict] = {}


class Activator:
    UUID_NAMESPACE = uuid.uuid4()

    def __init__(self, email: str | None = None) -> None:
        self.email: str | None = email

    def create_activation_key(self) -> uuid.UUID:
        if self.email is None:
            raise ValueError("Email isn't specified for activation key creation")
        else:
            return uuid.uuid3(self.UUID_NAMESPACE, self.email)


    def send_user_activation_email(self, activation_key: uuid.UUID):
        link = f"https://frontend.com/users/activation/{activation_key}"
        self.send_activation_mail(activation_link=link)
        pass
    

    def send_activation_mail(self, activation_link: str):
        if self.email is None:
            raise ValueError("Email isn't specified to send the Email")
        else:
            print(f"Sending email to {self.email} with link {activation_link}")
            send_mail(
                subject="User activation",
                message=f"Please, activate your account: {activation_link}",
                from_email="admin@catering.support.com",
                recipient_list=[self.email],
            )


    def save_activation_information(self, user_id: int, activation_key: uuid.UUID):
        payload = {"user_id": user_id}
        CACHE[activation_key] = payload



    def activate_user(self, activation_key: uuid.UUID | None) -> None:
        if activation_key is None:
            raise ValueError("Can't activate user without activation key")
        if activation_key not in CACHE:
            raise ValueError("Invalid activation key. The key may have expired or was never generated.")
        else:
            user_cache_payload = CACHE[activation_key]
            user = User.objects.get(id=user_cache_payload["user_id"])
            user.is_active = True
            user.save()
            print("User {user.pk} is activated")

        