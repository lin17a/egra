
from game.texturing import Skybox, Grass
from game.Engine import GraphicsEngine


def test_textures():
    app = GraphicsEngine()
    try:
        Skybox(app).render()
    except Exception as e:
        print(f"FAIL while loading Skybox: {e}")
    try:
        Grass(app).render()
    except Exception as e:
        print(f"FAIL while loading Grass: {e}")