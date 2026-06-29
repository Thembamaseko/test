from app import create_app,socketIO


app = create_app(__name__)
if __name__ == '__main__':
    socketIO.run(app, debug=True, port=5005)


    # this is my database url  postgresql
    # ://zwipi_f4u3_user:nYAKm2Gu7TRI2psNsHNYjGxA3OS5qoXp@dpg-d8si51svikkc739ntoj0-a/zwipi_f4u3