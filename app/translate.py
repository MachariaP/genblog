import requests
from flask import current_app
from flask_babel import _


def translate(text, source_language, dest_language):
    """
    Translate text from one language to another using Microsoft Translator.

    Args:
        text (str): The text to translate.
        source_language (str): The source language code.
        dest_language (str): The destination language code.

    Returns:
        str: The translated text or an error message if the translation fails.
    """
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not\
            current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')

    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'westus'
    }

    url = (
        'https://api.cognitive.microsofttranslator.com/translate'
        '?api-version=3.0&from={}&to={}'.format(source_language, dest_language)
    )

    r = requests.post(url, headers=auth, json=[{'Text': text}])

    if r.status_code != 200:
        return _('Error: the translation service failed.')

    return r.json()[0]['translations'][0]['text']
