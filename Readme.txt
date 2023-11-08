Steps to run the app:
1) Open the app.py file in word editor like VSCode.
2) Open terminal and create virtualenv
3) Install flask and other dependcies
4) run python file (python3 app.py)
5) Follow the link shown in terminal  http://127.0.0.1:5000
6) Login as Manager or user to use the app (credentials are given below)




Manager Login:
username:Yogeshh
password:qwer1234

User Login:
username:Yogi
password:12345678



To setup virtualenv: Windows
    1-> pip install virtualenv
    2-> python -m venv env
    3-> env/Scripts/Activate.ps1
    4-> pip install -r requirements.txt          //if flask showing error, change interpreter   click on python on bottom right corner of VSCode
    5-> Select python interpreter as virtualenv

To setup virtualenv: Linux
    1-> sudo apt install python3-venv
    2-> /usr/bin/python3 -m venv venv        //which python3
    3-> source venv/bin/activate
    4-> pip install -r requirements.txt                 //if flask showing error, change interpreter   click on python on bottom right corner of VSCode
    5-> Select python interpreter as virtualenv




To setup virtualenv: Mac
    1-> python3 -m pip install --user virtualenv
    2-> python3 -m venv env
    3-> source env/bin/activate
    4-> pip install -r requirements.txt
    5-> python3 app.py



    



