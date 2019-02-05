import sys
from admin_game import AdminGame
from user_game import UserGame
import matplotlib.pyplot as plt


database = 'SQL'
if len(sys.argv) == 1:
    game_type = UserGame(database)
elif sys.argv[1] == "admin":
    game_type = AdminGame(database)
elif sys.argv[1] == "normal":
    game_type = UserGame(database)
else:
    raise ValueError("Invalid input")
game_type.initiate_seq()
plt.show()
