import grpc
import froggy_pb2
import froggy_pb2_grpc
import random

def jugar():
    with grpc.insecure_channel('localhost:50051') as canal:
        stub = froggy_pb2_grpc.FroggyGameStub(canal)
        
        # Registrar jugador
        nombre = input("Ingresa tu nombre: ")
        emoji = input("Ingresa tu emoji: ")
        
        respuesta = stub.registrarJugador(froggy_pb2.RegistroRequest(
            nombre=nombre, emoji=emoji
        ))
        
        jugador_id = respuesta.id_jugador
        print(f"Te has registrado con ID: {jugador_id}")
        
        # Jugar hasta que termine
        while True:
            # Mostrar opciones de movimiento
            print("\n¿Qué dirección quieres mover?")
            print("1. ARRIBA")
            print("2. ABAJO") 
            print("3. IZQUIERDA")
            print("4. DERECHA")
            
            opcion = input("Selecciona (1-4): ")
            
            if opcion == '1':
                movimiento = froggy_pb2.ARRIBA
            elif opcion == '2':
                movimiento = froggy_pb2.ABAJO
            elif opcion == '3':
                movimiento = froggy_pb2.IZQUIERDA
            elif opcion == '4':
                movimiento = froggy_pb2.DERECHA
            else:
                print("Opción inválida")
                continue
            
            # Enviar movimiento
            respuesta_movimiento = stub.moverJugador(froggy_pb2.MovimientoRequest(
                id_jugador=jugador_id, movimiento=movimiento
            ))
            
            if not respuesta_movimiento.exito:
                print("Movimiento inválido o jugador ya no puede moverse")
            
            # Verificar estado
            estado = stub.estadoJugador(froggy_pb2.EstadoRequest(
                id_jugador=jugador_id
            ))
            
            print(f"Estado: {estado.mensaje}")
            
            # Si el juego terminó para este jugador, salir
            if estado.estado in ["CRUZO", "ATROPELLADO"]:
                break

if __name__ == '__main__':
    jugar()
