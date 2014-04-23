from wtforms import Form, StringField
from wtforms.validators import Length


def ouch():
    print("ouch!")


class FakeForm(Form):
    string = StringField('String', [Length(min=2, max=4)])
