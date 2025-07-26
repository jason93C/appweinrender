from app import app, db

with app.app_context():     
    db.create_all()    # Crea todas las tablas definidas en tus modelos
    print("Base de datos reiniciada correctamente.")