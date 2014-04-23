# import localpath
from framework.forms import FakeForm


my_string = "ah!"


class my_obj(object):
    string = my_string


form = FakeForm(data={'string': my_string})
print(form.data)
# form = FakeForm(data={'string': my_string})
if form.validate():
    print("{0} is valid input.  Yay!".format(my_string))
else:
    print("{0} is not valid input.  Boo!".format(my_string))

form = FakeForm(obj=my_obj)
if form.validate():
    print("{0} is valid input.  Yay!".format(my_string))
else:
    print("{0} is not valid input.  Boo!".format(my_string))
