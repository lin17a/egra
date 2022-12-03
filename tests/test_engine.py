from game.Engine import GraphicsEngine
from game.UI import menu


def test_menu():
    app = GraphicsEngine()
    try:
        menu(app).render()
    except Exception as e:
        print(f"FAIL while loading menu: {e}")



