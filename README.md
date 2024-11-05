# Gif Replace Function for Open WebUI

A comprehensive filter that replaces /gif "query" commands with random GIFs from Giphy.

![Gif Replace Open WebUI](https://refbax.com/img/gif-replace-open-web-ui.gif)

## Requirements

- Giphy API key (It's free) : https://developers.giphy.com/
- Open WebUI : https://github.com/open-webui/open-webui

## Installation
- Go in "Workspace" > "Functions"
- Add a new function
- Copy the main.py content and add it to the function
- Copy your API key in the function settings
- Save

### Model création
- You have to set a model that will be used to generate the GIFs
- You can use the default one, or create your own
- To create your own model, go to "Workspace" > "Models" > "Create new model"
- Active the "Gif Replacer" filter
- In the system prompt, add some instructions to help the model to generate relevant GIFs

Here an example of a system prompt :

```plaintext
You are an agent making joke and using the command /gif "...." to make gif for fun.

## Example for using /gif command
/gif "lol"
/gif "wasting time"

it's just few examples, i'm sure you can create a lot of alternatives
Two words in maximum in gif commands
```

## Usage
- Talk with your model like you would do with ChatGPT
- when the model use the /gif "query" command, it will generate a random GIF based on the query

That's all, enjoy !

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

