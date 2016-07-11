# -*- coding: utf-8 -*-
import os
from app import oauth

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class GithubOAuth:

    github = oauth.remote_app(
        'github',
        consumer_key='e830b099c951d20e8784',
        consumer_secret='1044b30af71f4f3a9d0004f6cf195b966cc5bf9b',
        request_token_params={'scope': 'admin:org'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )


class GitlabOAuth:

    gitlab = oauth.remote_app(
        'gitlab',
        # consumer_key='66dcd9cea621513f6ed2b0ee7bd84eb32fb559ee3a7d4b4a63c38d61103d0bfa',
        consumer_key='675532f089b661c350f5b7f1be143145353124cca44ecdae1391d8cb8419e4e9',
        # consumer_secret='c5043ac0701b80b880fd1e6c81feff2c785a8024e09e1c370df00136204cd7dc',
        consumer_secret='290e4d19ff457771d6947f646c649a8ce4aade8c4e3f0d2c633c6df6f4581507',
        base_url='http://code.smartstudy.com/oauth/authorize',
        request_token_url=None,
        access_token_method='GET',
        access_token_url='http://code.smartstudy.com/oauth/token'
    )
