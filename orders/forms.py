# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class GuestCheckoutForm(forms.Form):
    email = forms.EmailField()
    email2 = forms.EmailField(label='確認用メールフォーム')

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email == email2:
            user_exists = User.objects.filter(email=email).count()
            if not user_exists == 0:
                raise forms.ValidationError('このメールの登録情報があります。ログインしてください。')
            return email2
        else:
            raise forms.ValidationError("確認用メールフォームと同じメールアドレスにしてください。")
