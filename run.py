from app import create_app

aplication = create_app()

if __name__ == '__main__':
    aplication.run(debug=True)
    
"""
twoej saldo poprawic: wyswietlanie i nie mozna dodac kosztow jesli saldo <
przeznaczanie srodkow na cel
wykres po srodku
podliczanie wydatkow na kategorie
baza danych do rodzajow wydatkow"""