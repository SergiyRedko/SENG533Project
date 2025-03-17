# SENG533Project

This is the repository for SENG 533 group project.

We are group **#45** and our members:

| Name                | Student ID | GitHub Tag           |
|---------------------|-----------|-----------------------|
| Sergiy Redko        | 30151178  | Sergiy Redko|
| Caroline Basta      | 30057042  | CarolineBasta        |
| Romanard Tiratira   | 30142708  | r-tiratira     |
| Sukriti Sharma      | 30115530  |         |

All instructions listed in this README are for Windows systems. Alternative instructions for UNIX based systems are easy to find online.

## Table of Contents

> GENERATE THIS!!!

## License

This project is open-source under MIT license. Copy is [here](./LICENSE).

## Installation Instructions

Download and install [Ollama](https://ollama.com/).

Launch Ollama app.

> NOTE: Ollama app does not have a UI. It will be visible in system tray though.

Open CMD (or other terminal) and install following models:
- DeepSeek-R1 (`ollama pull deepseek-r1`)
- Llama 3.1 (`ollama pull llama3.1`)
- Mistral (`ollama pull mistral`)

You should verify that everything installed correctly by running `ollama list`. This should list installed models. You should see output similar to this:
```cmd
C:\Users\sergi>ollama list
NAME                  ID              SIZE      MODIFIED
mistral:latest        f974a74358d6    4.1 GB    5 minutes ago
llama3.1:latest       46e0c10c039e    4.9 GB    11 minutes ago
deepseek-r1:latest    0a8c26691023    4.7 GB    18 minutes ago
```

Now you can run our tests, or the installed models from terminal with `ollama run <model name>` and `/bye` to terminate a session with a specific model:
```cmd
C:\Users\sergi>ollama run mistral
>>> Tell me a joke about a frenchmen, a brit, and an italian in a bar.
 Why were the Frenchman, the Brit, and the Italian sitting at a bar together?

Because it was a "united" bars special night! (A play on words with "United Nations")

The Frenchman ordered a glass of wine, the Brit asked for a pint of ale, and the Italian demanded an espresso. The bartender looked at them and said, "You know, you three could save some money if you all just shared one drink!"

So they each took a sip from the same cup...

The Frenchman sipped his wine, the Brit took a swig of ale, the Italian drank his espresso - and immediately spit it out!

"What's wrong?" asked the bartender. The Italian replied, "Disgusting! It tastes like the three of us drank from the same cup!"

>>> /bye

C:\Users\sergi>
```

## Run and Replicate Our Tests

> WRITE THIS UP!!!

## Some Useful Links

There is an informative and concise tutorial on how to use Ollama [here](https://www.youtube.com/watch?v=UtSSMs6ObqY).