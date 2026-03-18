def crear_restaurante():
    # Los datos son un simple diccionario
    return {1: "Libre", 2: "Libre", 3: "Libre"}

def mostrar_estado(mesas):
    for num, estado in mesas.items():
        print(f"Mesa {num}: {estado}")

def reservar_mesa(mesas, num_mesa):
    if mesas.get(num_mesa) == "Libre":
        mesas[num_mesa] = "Reservada"
        print(f"✅ Mesa {num_mesa} reservada con éxito.")
    else:
        print(f"❌ La mesa {num_mesa} no está disponible.")

# Uso del sistema
mi_restaurante = crear_restaurante()
reservar_mesa(mi_restaurante, 1)
mostrar_estado(mi_restaurante)