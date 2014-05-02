from cgi import escape

from flask.ext.wtf import Form
from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.compat import text_type
from wtforms.validators import (
    InputRequired,
    Email,
    EqualTo,
)
from wtforms.widgets import html_params, HTMLString


class SelectWithDisable(object):
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, disabled in field.iter_choices():
            html.append(self.render_option(val, label, selected, disabled))
        html.append('</select>')
        return HTMLString(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, disabled=False, **kwargs):
        options = dict(kwargs, value=value)
        if selected:
            options['selected'] = True
        if disabled:
            options['disabled'] = True
        return HTMLString('<option %s>%s</option>' % (html_params(**options), escape(text_type(label))))


class SelectFieldWithDisable(SelectField):
    widget = SelectWithDisable()

    def __init__(self, label=None, validators=None, coerce=text_type,
                 choices=None, disabled=[], **kwargs):
        super(SelectFieldWithDisable, self).__init__(label, validators, coerce, choices, **kwargs)
        self.disabled = dict((opt, True) for opt in disabled)

    def iter_choices(self):
        for value, label in self.choices:
            # This line is odd.  According to the docs, the values for a select
            # field are tuples of the form (value, label).  However, in order
            # to get an empty string for the value of 'State' (my default
            # option), while also disabling it, I have to do 'value in
            # self.disabled' instead of 'label in self.disabled', and pass the
            # tuple '("", 'State')'.  Strange.
            yield (value, label, self.coerce(value) == self.data, value in self.disabled)


class LoginForm(Form):
    username = StringField('Username', [InputRequired(message="Please provide your username")])
    password = PasswordField('Password', [InputRequired(message="Please provide your password")])
    submit = SubmitField('Login')


class SignupForm(Form):
    email = StringField('Email', [Email(message="That's not a valid email address"),
                                  InputRequired()])
    username = StringField('Username', [InputRequired(message="Please provide a username")])
    password = PasswordField(
        'Password',
        [InputRequired("Please provide a password"),
         EqualTo('check_password', message="Passwords must match")])
    check_password = PasswordField('Re-enter password')
    submit = SubmitField('Sign up')
