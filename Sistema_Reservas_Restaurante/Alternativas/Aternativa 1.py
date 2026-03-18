class Restaurante:
    def __init__(self, total_mesas):
        # El estado vive dentro del objeto
        self.mesas = {i: "Libre" for i in range(1, total_mesas + 1)}

    def mostrar_estado(self):
        for num, estado in self.mesas.items():
            print(f"Mesa {num}: {estado}")

    def reservar(self, num_mesa):
        if self.mesas.get(num_mesa) == "Libre":
            self.mesas[num_mesa] = "Reservada"
            print(f"✅ Mesa {num_mesa} capturada por el objeto.")
        else:
            print(f"❌ Error: Mesa {num_mesa} ocupada.")

# Uso del sistema
mi_restaurante_oo = Restaurante(3)
mi_restaurante_oo.reservar(1)
mi_restaurante_oo.mostrar_estado()