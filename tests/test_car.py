from game.car import Car
from game.Engine import GraphicsEngine

def test_car():
    app = GraphicsEngine()
    try:
        Car(app).render()
    except Exception as e:
        print(f"FAIL while loading car model: {e}")