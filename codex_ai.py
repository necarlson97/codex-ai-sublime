import sublime
import sublime_plugin

import json
import requests


class CodexCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                # Get the selected text
                prompt = self.view.substr(region)
                # Get result from codex
                response = self.get_codex_response(prompt)
                self.view.replace(edit, region, prompt + response)
            else:
                msg = "Please highlight a comment of section of code."
                sublime.status_message(msg)
                raise ValueError(msg)

    def get_codex_response(self, prompt):
        """
        Pass the given text to Open AI's codex (davinci)
        model, returning the response
        """
        settings = sublime.load_settings('Default.sublime-settings')
        key = settings.get('open_ai_key', None)
        if key is None:
            msg = "Please put an 'open_ai_key' in the CodexAI package settings"
            sublime.status_message(msg)
            raise ValueError(msg)

        response = requests.post(
            'https://api.openai.com/v1/engines/davinci-codex/completions',
            headers={
                'Authorization': "Bearer " + key,
                'Content-Type': 'application/json',
            },
            data=json.dumps({
                'prompt': prompt,
                "max_tokens": settings.get('max_tokens', 100)
            }),
            verify='/etc/ssl/certs'
        )

        respone_dict = response.json()

        if respone_dict.get('Error', None):
            raise ValueError(respone_dict['Error'])
        else:
            choice = respone_dict.get('choices', [{}])[0]
            ai_text = choice.get('text', response.text)
        return ai_text
