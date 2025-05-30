# SENG533Project

This is the repository for SENG 533 group project. In this project, we evaluate and compare the performance of locally hosted LLMs. Our two main questions were what the average response time and the throughput of the system are.

We are group **#45** and our members:

| Name                | Student ID | GitHub Tag    |
|---------------------|------------|---------------|
| Sergiy Redko        | 30151178   | Sergiy Redko  |
| Caroline Basta      | 30057042   | CarolineBasta |
| Romanard Tiratira   | 30142708   | r-tiratira    |
| Sukriti Sharma      | 30115530   | suxxmjz       |

All instructions listed in this README are for Windows systems. Alternative instructions for UNIX based systems are easy to find online.

## Table of Contents

- [SENG533Project](#seng533project)
- [License](#license)
- [Installation Instructions](#installation-instructions)
  - [Ollama](#ollama)
  - [Python](#python)
- [Run and Replicate Our Tests](#run-and-replicate-our-tests)
- [Some Useful Links](#some-useful-links)

## License

This project is open-source under MIT license. Copy is [here](./LICENSE).

## Installation Instructions

### Ollama

Download and install [Ollama](https://ollama.com/).

Launch Ollama app.

> NOTE: Ollama app does not have a UI. It will be visible in the system tray, though.

Open CMD (or other terminal) and install the following models:
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

Now you can run our tests, or the installed models from the terminal with `ollama run <model name>` and `/bye` to terminate a session with a specific model:
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

### Python

First, you should start the virtual environment: `.\venv\Scripts\activate.bat`

Now, install all required Python modules: `pip install -r requirements.txt`

## Run and Replicate Our Tests

Run our tests with `python tester.py`.

This script comes with 2 arguments:
- `--max-queries` if you do not want to run all the queries.
- `--test-iterations` if you want to run multiple iterations of this test to normalize the error.

This script will ask you for your initial. **DO NOT FORGET TO ENTER IT**!

While the test is running, you will see something like this:
```cmd
(venv) C:\Users\sergi\Documents\GitHub\SENG533Project>python tester.py  
Please enter your initials: SR
|■■■■■-----------------------------------------------------------------------------------------------|
    Percent complete:        5%
    Test iteration:           1
    Testing model:  deepseek-r1
    Testing query:            9
```
We implemented this progress bar and status display as testing process takes quite a while. Without a status bar it is difficult to tell if the test is still running, or if the whole thing got hung up.

You may notice that after running this script, `./Results/performance_results_{user_initial}.json` was generated. This file contains all the intermediate data we will need.

The second step is to run the analyzer with `python analyzer.py`. Please make sure that `performance_results_XX.json` files are in the `Results` folder. After running this script, the statistics for each model will be printed to the terminal. 

## Some Useful Links

There is an informative and concise tutorial on how to use Ollama [here](https://www.youtube.com/watch?v=UtSSMs6ObqY).
