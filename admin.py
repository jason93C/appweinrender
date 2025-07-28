from app import app, db, user

with app.app_context():
    # Verificar si el usuario ya existe
    existe = user.query.filter_by(user="admin").first()
    if existe:
        print("⚠️  Ya existe un usuario admin.")
    else:
        nuevo_usuario = user(
            nom_usuario="Admin",
            ape_usuario="General",
            username="admin",
            password="admin123"
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        print("✅ Usuario admin creado con éxito.")