## VK API WRAPPER

This application will take the content published by a VKontakte page, and it will output a table with the **date**, the **text**, the **number of likes**, and the **original link** to the post.
It is also possible to input a start and an end date to filter out the results. The output will be saved as a **CSV** file in the output folder.

The commands available are:

|   Command   |                               Description                                |
|:-----------:|:------------------------------------------------------------------------:|
| credentials |                             Provide API Key                              |
|    dates    |              Insert date or date range (dd/mm/yyyy format)               |
|    dshow    |                            Show stored dates                             |
|     run     | When everything is set, the scraper will start running with this command |
|   targets   |  Isert whitespace separated list of target(s), will overwrite old ones   |
|    tshow    |                   Show comma separated list of target                    |

A small code example to start the application:

`python3 main.py <target name>`

The target name is retrieved from the target `url`: `https://vk.com/<target name>`

NB This application uses your service access key from your VKontakte API
