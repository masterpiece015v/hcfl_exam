from django import forms
from .models import User

class LoginForm( forms.Form ):
    user_id = forms.CharField(label='user_id',widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField( label='password',widget=forms.TextInput(attrs={'class':'form-control'}))

class UserForm( forms.ModelForm ):
    class Meta:
        model = User
        fields = ['user_id','password','user_name']
        widgets ={
            'user_id':forms.TextInput(attrs={'class':'form-control'}),
            'password':forms.TextInput(attrs={'class':'form-control'}),
            'user_name':forms.TextInput(attrs={'class':'form-control'})
        }

class UploadFileForm( forms.Form ):
    title = forms.CharField( max_length=50 )
    file = forms.FileField()

