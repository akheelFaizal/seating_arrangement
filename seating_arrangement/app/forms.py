# # users/forms.py
# from django.contrib.auth.forms import UserCreationForm
# from django import forms
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ("roll_number", "name", "email", "course", "department", "year", "password1", "password2")

#     # Example customizations:
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#     #     self.fields["course"].queryset = Course.objects.select_related("department")
#     #
#     # def clean_roll_number(self):
#     #     rn = self.cleaned_data["roll_number"].upper()
#     #     # add format checks here
#     #     return rn
