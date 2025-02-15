# ed_stats
ED explorer statistics

# Configure and run

Add the full path to your ED logs directory. It's probably:
```
/home/your_username/.steam/debian-installation/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/
```

```
$ cd ed_plants/
$ nano config.json
```
When done, start the app while in ed_plants directory. 

```
python3 -m venv .venv
. .venv/bin/activate
python app.py
```

Open http://localhost:5000/ in your webbrowser. 
