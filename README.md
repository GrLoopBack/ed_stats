# ed_stats
ED explorer statistics
**This code was written by deepseek bot.** 

# Configure and run

Add the full path to your ED logs directory. It's probably:
```
/home/your_username/.steam/debian-installation/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/
```
You could also creata a link to logs directory and use much shorter link in the config file. 

```
ln -s LongAndUglyPath EDlogs
```

```
$ cd ed_stats/
$ nano config.json
```
When done, start the app while in ed_stats directory. 

```
python3 -m venv .venv
. .venv/bin/activate
(if first time, install flask: pip install flask)
python app.py
```

Open http://localhost:5000/ in your webbrowser. 
