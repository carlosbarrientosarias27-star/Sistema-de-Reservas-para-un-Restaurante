from core.sistema import SistemaReservas
from config import FORMATO_FECHA
def mostrar_reserva(r: dict) -> None:
    print(f"  #{r['id']} | {r['nombre']} | Mesa {r['mesa']} ({r['zona']})")
    print(f"  {r['fecha_hora']} | {r['comensales']} comensales | {r['estado']}")
    print(f"  {r['telefono']} / {r['email']}\n")


def ejecutar():
    sr = SistemaReservas()
    print(f"✅ Sistema cargado — {len(sr.reservas)} reservas en memoria.")

    while True:
        print("\n====== SISTEMA DE RESERVAS (SEGURO) ======")
        print("1. Crear reserva")
        print("2. Consultar reservas de un cliente")
        print("3. Cancelar reserva")
        print("4. Modificar reserva")
        print("5. Comprobar disponibilidad")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            nombre     = input("Nombre: ")
            telefono   = input("Teléfono: ")
            email      = input("Email: ")
            try:
                mesa       = int(input("Número de mesa (1-5): "))
                fecha      = input(f"Fecha y hora ({FORMATO_FECHA}): ")
                comensales = int(input("Comensales: "))
            except ValueError:
                print("❌ Número de mesa y comensales deben ser enteros.")
                continue
            res = sr.crear_reserva(nombre, telefono, email, mesa, fecha, comensales)
            if "error" in res:
                print(f"❌ {res['error']}")
            else:
                print("✅ Reserva creada:")
                mostrar_reserva(res["reserva"])

        elif opcion == "2":
            nombre = input("Nombre del cliente: ")
            lista  = sr.consultar_cliente(nombre)
            if lista:
                for r in lista:
                    mostrar_reserva(r)
            else:
                print("No hay reservas activas para ese cliente.")

        elif opcion == "3":
            try:
                id_r = int(input("ID de la reserva: "))
            except ValueError:
                print("❌ El ID debe ser un número entero.")
                continue
            res = sr.cancelar_reserva(id_r)
            print(f"✅ {res['mensaje']}" if "ok" in res else f"❌ {res['error']}")

        elif opcion == "4":
            try:
                id_r = int(input("ID de la reserva: "))
            except ValueError:
                print("❌ El ID debe ser un número entero.")
                continue
            nueva_fecha = input("Nueva fecha (vacío = no cambiar): ").strip() or None
            nc = input("Nuevos comensales (vacío = no cambiar): ").strip()
            nuevos_com = int(nc) if nc else None
            res = sr.modificar_reserva(id_r, nueva_fecha, nuevos_com)
            if "error" in res:
                print(f"❌ {res['error']}")
            else:
                print("✅ Reserva modificada:")
                mostrar_reserva(res["reserva"])

        elif opcion == "5":
            try:
                mesa  = int(input("Número de mesa: "))
            except ValueError:
                print("❌ El número de mesa debe ser un entero.")
                continue
            fecha = input("Fecha y hora: ")
            libre = sr.esta_disponible(mesa, fecha)
            print("✅ Mesa LIBRE" if libre else "❌ Mesa OCUPADA o no existe")

        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    ejecutar()