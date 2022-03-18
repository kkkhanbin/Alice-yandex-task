import os

from src import app
from waitress import serve


def main():
    port = int(os.environ.get('PORT', 5000))
    serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
