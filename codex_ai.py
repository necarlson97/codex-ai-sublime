import sublime
import sublime_plugin

import json
import http.client
import threading


class CodexCommand(sublime_plugin.TextCommand):
    def check_setup(self):
        """
        Perform a few checks to make sure codex can run
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
                self.handle_thread(thread, seconds + 1), 1000)
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
            "region": thread.region.to_tuple(),
            "text": thread.preText + thread.result
        })        


class CompletionCodexCommand(CodexCommand):
    """
    Give a prompt of text/code for GPT3 to complete
    """

    def run(self, edit):
        # Check config and prompt
        self.check_setup()

        # Gather data needed for codex, prep thread to run async
        region = self.view.sel()[0]
        settings = sublime.load_settings('codex-ai.sublime-settings')
        settingsc = settings.get('completions')

        data = {
            'model': settingsc.get('model',"text-davinci-003"),
            'prompt': self.view.substr(region),
            'max_tokens': settingsc.get('max_tokens', 100),
            'temperature': settingsc.get('temperature', 0),
            'top_p': settingsc.get('top_p', 1),
        }
        hasPreText=settingsc.get('keep_prompt_text')
        if hasPreText:
            preText=self.view.substr(region)
        else:
            preText=""
        thread = AsyncCodex(region, 'completions', data, preText)

        # Perform the async fetching and editing
        thread.start()
        self.handle_thread(thread)


class EditCodexCommand(CodexCommand):
    """
    Give a prompt of text/code to GPT3 along with an instruction of how to
    modify the prompt, while trying to keep the functionality the same
    (.e.g.: "Translate this code to Javascript" or "Reduce runtime complexity")
    """

    def input(self, args):
        return InstructionInputHandler()

    def run(self, edit, instruction):
        # Check config and prompt
        self.check_setup()

        # Gather data needed for codex, prep thread to run async
        settings = sublime.load_settings('codex-ai.sublime-settings')
        settingse = settings.get('edits')
        region = self.view.sel()[0]
        data = {
            'model': settingse.get('edit_model',"text-davinci-edit-001"),
            'input': self.view.substr(region),
            'instruction': instruction,
            'temperature': settingse.get('temperature', 0),
            'top_p': settingse.get('top_p', 1),
        }
        thread = AsyncCodex(region, 'edits', data, "")

        # Perform the async fetching and editing
        thread.start()
        self.handle_thread(thread)


class InstructionInputHandler(sublime_plugin.TextInputHandler):
    def name(self):
        return "instruction"

    def placeholder(self):
        return "E.g.: 'translate to java' or 'add documentation'"


class AsyncCodex(threading.Thread):
    """
    A simple async thread class for accessing the
    OpenAI Codex API, and waiting for a response
    """
    running = False
    result = None

    def __init__(self, region, endpoint, data, preText):
        """
        key - the open-ai given API key for this specific user
        prompt - the string of code/text to be operated on by GPT3
        region - the sublime-text hilighted region we are looking at,
            and will be dropping the result into
        instruction - for the edit endpoint, an instruction is needed, e.g.:
            "translate this code to javascript". If just generating code,
            leave as None
        """
        super().__init__()
        self.region = region
        self.endpoint = endpoint
        self.data = data
        self.prompt = data.get('prompt', "")
        self.preText = preText

    def run(self):
        self.running = True
        self.result = self.get_codex_response()
        self.running = False

    def get_codex_response(self):
        """
        Pass the given data to Open AI's codex (davinci)
        model, returning the response
        """
        settings = sublime.load_settings('codex-ai.sublime-settings')
        conn = http.client.HTTPSConnection('api.openai.com')
        headers = {
            'Authorization': "Bearer " + settings.get('open_ai_key', None),
            'Content-Type': 'application/json'
        }
        data = json.dumps(self.data)
        conn.request('POST', '/v1/' + self.endpoint, data, headers)
        response = conn.getresponse()
        respone_dict = json.loads(response.read().decode())

        if respone_dict.get('error', None):
            raise ValueError(respone_dict['Error'])
        else:
            choice = respone_dict.get('choices', [{}])[0]
            ai_text = choice['text']
            useage = respone_dict['usage']['total_tokens']
            sublime.status_message("Codex tokens used: " + str(useage))
        return ai_text


class ReplaceTextCommand(sublime_plugin.TextCommand):
    """
    Simple command for inserting text
    https://forum.sublimetext.com/t/solved-st3-edit-object-outside-run-method-has-return-how-to/19011/7
    """

    def run(self, edit, region, text):
        region = sublime.Region(*region)
        self.view.replace(edit, region, text)
