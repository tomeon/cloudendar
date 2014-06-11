import simplejson as json

from gapi import get_web_server_flow
from oath2client.client import OAuth2WebServerFlow

def get_credentials():
    """
    For use with the flask-login LoginManager.user_loader decorator
    """

