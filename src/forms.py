from cgi import escape
from datetime import date
from dateutil.relativedelta import relativedelta
from flask.ext.wtf import Form
from flask.ext.admin.form.widgets import DateTimePickerWidget
from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextField,
)
from wtforms.compat import text_type
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import (
    InputRequired,
    Email,
    EqualTo,
    ValidationError,
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


class DateTimePickerField(DateTimeField):
    def __call__(self, **kwargs):
        return super(DateTimePickerField, self).__call__(class_="datetimepicker", **kwargs)


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


def compare_datetime(comp_field_name):
    def _compare_datetime(form, field):
        comp_field = form[comp_field_name]
        message = "Date and time must be after %s" % (comp_field.data)
        if field.data <= comp_field.data:
            raise ValidationError(message)

    return _compare_datetime


class EventForm(Form):
    start = DateTimePickerField('Start time',
                          #widget=DateTimePickerWidget(),
                          validators=[InputRequired()],
                          default=date.today() + relativedelta(hour=12),
                          )
    end = DateTimePickerField('End time',
                              #widget=DateTimePickerWidget(),
                              validators=[InputRequired(),
                                          compare_datetime('start')],
                              default=date.today() + relativedelta(hour=13),
                              )
    desc = TextField('Description')
    submit = SubmitField('Submit')


class LoginObj(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        print("<LoginObj %r>" % self.username)


class SignupObj(object):
    def __init__(self, email=None, username=None, password=None,
                 check_password=None):
        self.email = email
        self.username = username
        self.password = password
        self.check_password = check_password

    def __repr__(self):
        print("<SignupObj %r>" % self.username)


class EventObj(object):
    def __init__(self, start=None, end=None, desc=None):
        self.start = start
        self.end = end
        self.desc = desc

    def __repr__(self):
        print("<EventObj %r %r>" % self.start, self.end)
