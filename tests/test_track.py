from game.Engine import GraphicsEngine
from game.Circuito import Circuito

def test_track():
    app = GraphicsEngine()
    try:
        Circuito(app).render()
    except Exception as e:
        print(f"FAIL while loading track: {e}")