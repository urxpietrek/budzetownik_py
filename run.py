from app import create_app

aplication = create_app()

if __name__ == '__main__':
    aplication.run(debug=True)