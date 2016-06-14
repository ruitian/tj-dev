# -*- coding: utf-8 -*-
from app import oauth


class GithubOAuth:

    github = oauth.remote_app(
        'github',
        consumer_key='e830b099c951d20e8784',
        consumer_secret='1044b30af71f4f3a9d0004f6cf195b966cc5bf9b',
        request_token_params={'scope': 'user:email'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )
