## VK SCRAPER
To run this application you will need a GitHub Private Access Key, the app will ask to insert one on startup if not present. 
This application will take the content published by a VKontakte page, and it will output a table with the **date**, the **text**, the **number of likes**, and the **original link** to the post.
It is also possible to input a start and an end date to filter out the results. The output will be saved as a **CSV** file in the output folder.

The commands available are:

|  Command  |                                                Description                                                 |
|:---------:|:----------------------------------------------------------------------------------------------------------:|
|   dates   |                               Insert date or date range (dd/mm/yyyy format)                                |
| download  |                  From a commaseparated list of post links it will download the thumbnails                  |
|   dshow   |                                             Show stored dates                                              |
|gitkey|You can change the saved GitHub Private Access Key that you saved|
|    run    |                  When everything is set, the scraper will start running with this command                  |
|  targets  |                   Isert whitespace separated list of target(s), will overwrite old ones                    |
| translate | This command will start the translation of the targets you have set in English. NB, requires DeepL API key |
|   tshow   |                                    Show comma separated list of target                                     |
|  update   |                          This commands is used to update the API key credentials                           |

A small code example to start the application, the `<target name>` is optional, it can be set within the application using `targets`:

`python3 main.py -t <target name>`

All of the data you willscrape or download will be found in the `outputs` folder.

The target name is retrieved from the target `url`: `https://vk.com/<target name>`

NB Timezone is set for `"Europe/Moscow"`, I'm still figuring out how TZ work on VK
  
For translation, you need a DeepL API key, if you have one just run `translate` and if not altready saved it will ask you for an API key.

**For any new feature, bug, help, etc. Just contact me @ albertofedericoolivieri@gmail.com or open a ticket.**

