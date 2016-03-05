# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model

from .models import UserAddress

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


class AddressForm(forms.Form):
    billing_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type='billing'),
        widget=forms.RadioSelect,
        empty_label=None,
    )
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type='shipping'),
        widget=forms.RadioSelect,
        empty_label=None,
    )


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'zipcode',
            'state',
            'address1',
            'address2',
            'type',
        ]
