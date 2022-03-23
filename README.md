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
      8.1. https://visualstudio.microsoft.com/ru/downloads/?q=build+tools
      8.2. 
![photo_2022-03-23_16-10-25](https://user-images.githubusercontent.com/52703175/159745023-96951170-4080-4462-a176-5833b5c88702.jpg)
      8.3. Make shure to install MSCV containing C++ tools
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
