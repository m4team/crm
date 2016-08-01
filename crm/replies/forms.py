from django import forms

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'send-box'}),
                              label="Message Content")


