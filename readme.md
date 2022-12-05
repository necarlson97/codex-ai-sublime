# Codex AI Sublime Package
Work alongside cutting edge AI to write code - automate the boilerplate, and focus on the creative side of coding.
Can be used as code-autocomplete, to help generate boilerplate, to translate between different programming languages, and more.

![gif](sublime-codex.gif)

## Disclaimer
This relies entirely upon [OpenAI's API](https://openai.com/blog/openai-api/). You must have an account, and API key, and be authorized to use the [Codex API](https://openai.com/blog/openai-codex/).
You are trusting an outside organization with the code you send them, and it is not encrypted - this cannot be used for HIPPA info, confidential data, etc.
Thanks to OpenAI for their work on this tech - this is not an official package.

See [OpenAI](https://openai.com/blog/openai-codex/) for more details on the technology.

Powerful technology can be dangerous. Please use this (and all AI tools) with kindness, care, and the greater good in mind. Supervise all it creates, and, as always, do not run code you do not trust or understand. [Be responsible.](https://beta.openai.com/policies/codex-terms)

## Installation
### Linux
Use Package Control and find CodexAI
### OSX
Until upstream publishes this version for OSX in package control, do the following:
1. checkout this github project somewhere other than your default Packages directory
2. create a link to this github project in your Packages directory e.g:
```
  cd /Users/whoeveryouare/Library/Application Support/Sublime Text 3/Packages/
  ln -s /Users/whoeveryouare/where/ever/you/put/the/project CodexAI
```
3. Restart sublime
## Use
First: input your OpenAI API key in the Preferences->Package Settings->CodexAI

### Completion
To have the Codex AI try to generate code/text, simply simply highlight whatever prompt you would like to complete, then use the following keybindings to see how Codex would complete that prompt.
* Linux: 'ctrl-shift-insert'
* OSX: 'command-shift-a'

One can also use the command pallet (ctrl+shift+p) and type 'Codex AI' to see the 'Generate' command.


### Editing
You could also have Codex AI try edit your code -perhaps to translate it to a different langue, or try a more terse implementation, or add documentation. Highlight whatever code you would like edited, then use the following keybindings to instruct Codex to re-work that area.
* Linux: 'ctrl+shift+end' 
* OSX: 'command-shift-e'

One can also use the command pallet (ctrl+shift+p) and type 'Codex AI' to see the 'Instruct' command.

You can type whatever you like when asked for the editing instruction. Short, clear instructions work best, but feel free to experiment with more abstract concepts.

At the time of writing (5/22), OpenAPI has this 'edits' endpoint in beta. It is thus free to use - but at times unstable. If your text is replaced with:
```
{
  "error": {
    "message": "Could not edit text. Please sample again or try with a different temperature setting, input, or instruction.",
    "type": "invalid_edit",
    "param": null,
    "code": null
  }
}
```
codex was unable to help with that specific prompt and instruction. Simply 'ctrl+z' to get your prompt back. Feel free to try again, perhaps with a different wording of the instruction.

## Tips
Codex is great for filling out bite-sized methods - things like reading a file, creating a server, etc - then you can focus on orchestrating those pieces into a larger project.

Codex can help you determine what libraries you might use to solve a problem. Similarly, if you already know the library you would like, you can suggest Codex use it - (e.g., include 'import numpy').

Including a method name and a clear, standardized comment is a great way to turn 'plain english' into code.
Similarly, you must include some of the conventions / syntax of the language you want codex to generate.(e.g., 'def method_name():' for python vs 'static void methodName() {' for java)


Codex is trained on real user's code. Though it can do some extrapolation on it's own, it will likely fail on niche, novel problems. However, for the same boring syntax-y code you have googled a dozen times, Codex is perfect. ("How do I unpack an .MP4 again? Ah, Codex will know!")
