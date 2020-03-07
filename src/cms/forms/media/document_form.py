from django import forms


class DocumentForm(forms.Form):
    """
    Form for creating and modifying document objects
    """

    upload = forms.FileField()
