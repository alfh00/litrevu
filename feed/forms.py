from django import forms

from .models import Photo, Review, Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description"]


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["file", "caption"]


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ["rating", "headline", "body"]


class TicketRemoveForm(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)
