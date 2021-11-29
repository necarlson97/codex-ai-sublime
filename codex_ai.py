import sublime
import sublime_plugin

import json
import requests
import threading


class CodexCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        """
        Perform a few checks to make sure codex can run, then
        initiate the async fetching from the Codex API
        """
        settings = sublime.load_settings('codex-ai.sublime-settings')
        key = settings.get('open_ai_key', None)
        if key is None:
            msg = "Please put an 'open_ai_key' in the CodexAI package settings"
            sublime.status_message(msg)
            raise ValueError(msg)

        if len(self.view.sel()) > 1:
            msg = "Please highlight only 1 chunk of code."
            sublime.status_message(msg)
            raise ValueError(msg)

        region = self.view.sel()[0]
        if region.empty():
            msg = "Please highlight a section of code."
            sublime.status_message(msg)
            raise ValueError(msg)

        # Perform the async fetching and editing
        prompt = self.view.substr(region)
        thread = AsyncCodex(key, prompt, region)
        thread.start()
        self.handle_thread(thread)

    def handle_thread(self, thread, seconds=0):
        """
        Recursive method for checking in on the AsyncCodex API fetcher
        """
        settings = sublime.load_settings('codex-ai.sublime-settings')
        max_seconds = settings.get('max_seconds', 60)

        # While the thread is running, show them some feedback,
        # and keep checking on the thread
        if thread.running:
            msg = "Codex is thinking, one moment... ({}/{}s)".format(
                seconds, max_seconds)
            sublime.status_message(msg)
            # Wait a second, then check on it again
            sublime.set_timeout(lambda:
                self.handle_thread(thread, seconds+1), 1000)
            return

        # If we ran out of time, let user know, stop checking on the thread
        if seconds > max_seconds:
            msg = "Codex ran out of time! {}s".format(max_seconds)
            sublime.status_message(msg)
            return

        # If we finished with no result, something is wrong
        if not thread.result:
            sublime.status_message("Something is wrong with Codex - aborting")
            return

        # Otherwise, we are done!
        self.view.run_command('replace_text', {
            "region": thread.region.to_tuple(), "text": thread.prompt + thread.result
        })
        sublime.status_message("Codex has spoken.")


class AsyncCodex(threading.Thread):
    """
    A simple async thread class for accessing the
    OpenAI Codex API, and waiting for a response
    """
    running = False
    result = None

    def __init__(self, key, prompt, region):
        super().__init__()
        self.key = key
        self.prompt = prompt
        self.region = region

    def run(self):
        self.running = True
        self.result = self.get_codex_response(self.prompt, self.key)
        self.running = False

    def get_codex_response(self, prompt, key):
        """
        Pass the given text to Open AI's codex (davinci)
        model, returning the response
        """
        settings = sublime.load_settings('codex-ai.sublime-settings')

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

class ReplaceTextCommand(sublime_plugin.TextCommand):
    """
    Simple command for inserting text
    https://forum.sublimetext.com/t/solved-st3-edit-object-outside-run-method-has-return-how-to/19011/7
    """
    def run(self, edit, region, text):
        region = sublime.Region(*region)
        self.view.replace(edit, region, text)
