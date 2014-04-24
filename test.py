from wtforms import Form, StringField
from wtforms.validators import Length


'''
Here we define a subclass of the Form class
from wtforms.  We give it a StringField named
'string', passing to the StringField constructor
the label 'String', and a list of validators
(here, a 1-element list consisting of the 'Length'
validator)
'''
class FakeForm(Form):
    string = StringField('String', [Length(min=2, max=4)])


my_string = "Foo!"


'''
Using the 'data' keyword, you can pass a dictionary to
the form constructor.  In typical usage, the dictionary
keys should be the names of fields in the form.  Here,
our FakeForm has a field called 'string', so the key in
our one-pair dictionary is 'string'.
'''
form = FakeForm(data={'string': my_string})
'''
You can also use field names as keywords.  The following
line of code is equivalent to the code we just saw:

form = FakeForm(string=my_string)
'''


if form.validate():
    print("{0} is valid input.  Yay!".format(my_string))
else:
    print("{0} is not valid input.  Boo!".format(my_string))
