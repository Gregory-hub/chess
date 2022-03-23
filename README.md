# Chess
Online chess game created with flask, sqlalchemy and socketio
# Istallation(Windows)
  1. Download python and git
  2. Open terminal
  3. Go to your installation folder:
      >>> chdir path\to\folder
      >>> F:                # to change disk to F:
  4. Download repo:
      >>> git clone https://github.com/Gregory-hub/chess.git
  5. Go to chess folder:
      >>> chdir chess
  6. Switch to sqlite-version:
      >>> git switch sqlite-version
  7. Install requirements from requirements.txt:
      >>> pip install -r requirements.txt
      >>> python -m pip install -r requirements.txt   # if previous did not work
  8. If you get an error installing netifaces, install Visual Studio Build Tools: 
      * https://visualstudio.microsoft.com/ru/downloads/?q=build+tools
![photo_2022-03-23_16-31-26](https://user-images.githubusercontent.com/52703175/159749374-f064bbb2-1a8a-49ef-86d8-74896b57c6a8.jpg)
      * Make shure to install MSCV containing C++ tools
![photo_2022-03-23_16-10-24](https://user-images.githubusercontent.com/52703175/159745551-57de11c4-fd43-4195-98ee-e76ba4b95e04.jpg)
  9. Go to python shell:
      >>> python
  10. Create tables in db:
      >>> from chess import db
      >>> db.create_all()
      >>> db.session.commit()
      >>> exit()
  11. Now you can run application:
      >>> python run.py
