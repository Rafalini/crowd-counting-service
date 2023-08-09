# Crowd counting and mapping 🧍‍♂️🧍‍♂️🧍‍♂️
Web service app for counting people from pictures. Users can post crowded images from mass events which will be processed (people counting will be performed, based on [density function](https://arxiv.org/pdf/1907.12428.pdf) )

![image](https://github.com/Rafalini/crowd-counting-service/assets/44322872/aa5e255a-f29f-442c-8c02-1acb2b833f70)

All processed data is agregated and marked on map:

<img src="https://github.com/Rafalini/crowd-counting-service/assets/44322872/2836e173-2f1a-4400-a966-3ee49d626ac7" width="600" height="400">

# Build 🔨 and run 🚘
1. App is build using [Python](https://www.python.org/), hence it requires Python 3.X.X interpreter along with [pip](https://pypi.org/project/pip/)
  a) optional is to use [vnenv](https://docs.python.org/3/library/venv.html)
2. Get dependencies: `pip install -r requirements.txt`
3. Set variables for database connection (URI, Username, Password) for existing soluutions like  [Oracle](https://www.oracle.com/pl/database/), [SQL Server](https://www.microsoft.com/pl-pl/sql-server/sql-server-2019) or any other.

   Or configure local database file, for example:
      
   `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db?check_same_thread=False'`
   
4. Optional:  In root directory/crowdControll/\_\_init\_\_.py configure email server (for password reseting etc):
 ```
    app.config['MAIL_SERVER'] = 'EMAIL_SERVER'
    app.config['MAIL_PORT'] = 0
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'EMAIL_LOGIN'
    app.config['MAIL_PASSWORD'] = 'EMAIL_PASSWORD'
```
5. In the root directory of cloned project run app by executing: `python run.py`
6. To visit homepage, by default go to: http://127.0.0.1:5000/  
