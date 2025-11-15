import grpc
from concurrent import futures
import froggy_pb2
import froggy_pb2_grpc
import random
import time

class FroggyGameServicer(froggy_pb2_grpc.FroggyGameServicer):
    def __init__(self):
        self.jugadores = {}
        self.tablero = self.inicializar_tablero()
        self.contador_jugadores = 0
        self.juego_activo = True
        self.ganador = None

    def inicializar_tablero(self):
        # Crear un tablero 10x10 con autos en posiciones aleatorias
        tablero = [[' ' for _ in range(10)] for _ in range(10)]
        
        # Agregar autos en filas específicas
        for fila in [2, 4, 6]:
            for _ in range(3):
                col = random.randint(0, 9)
                tablero[fila][col] = 'A'  # 'A' representa un auto
        
        return tablero

    def registrarJugador(self, request, context):
        self.contador_jugadores += 1
        jugador_id = self.contador_jugadores
        
        # Posición inicial en la parte inferior del tablero
        posicion = (9, random.randint(0, 9))
        
        self.jugadores[jugador_id] = {
            'nombre': request.nombre,
            'emoji': request.emoji,
            'posicion': posicion,
            'vivo': True,
            'cruzado': False
        }
        
        print(f"Jugador registrado: {request.nombre} (ID: {jugador_id})")
        
        return froggy_pb2.RegistroResponse(id_jugador=jugador_id)

    def moverJugador(self, request, context):
        jugador_id = request.id_jugador
        
        if jugador_id not in self.jugadores:
            return froggy_pb2.MovimientoResponse(exito=False)
        
        jugador = self.jugadores[jugador_id]
        
        if not jugador['vivo'] or jugador['cruzado']:
            return froggy_pb2.MovimientoResponse(exito=False)
        
        fila, columna = jugador['posicion']
        movimiento = request.movimiento
        
        # Calcular nueva posición
        if movimiento == froggy_pb2.ARRIBA and fila > 0:
            fila -= 1
        elif movimiento == froggy_pb2.ABAJO and fila < 9:
            fila += 1
        elif movimiento == froggy_pb2.IZQUIERDA and columna > 0:
            columna -= 1
        elif movimiento == froggy_pb2.DERECHA and columna < 9:
            columna += 1
        else:
            return froggy_pb2.MovimientoResponse(exito=False)
        
        # Verificar colisión con auto
        if self.tablero[fila][columna] == 'A':
            jugador['vivo'] = False
            print(f"Jugador {jugador['nombre']} fue atropellado!")
        else:
            jugador['posicion'] = (fila, columna)
            
            # Verificar si cruzó (llegó a la fila 0)
            if fila == 0:
                jugador['cruzado'] = True
                self.ganador = jugador['nombre']
                print(f"¡{jugador['nombre']} ha cruzado exitosamente!")
        
        return froggy_pb2.MovimientoResponse(exito=True)

    def estadoJugador(self, request, context):
        jugador_id = request.id_jugador
        
        if jugador_id not in self.jugadores:
            return froggy_pb2.EstadoResponse(
                estado="NO_REGISTRADO",
                mensaje="Jugador no registrado"
            )
        
        jugador = self.jugadores[jugador_id]
        
        if jugador['cruzado']:
            mensaje = f"¡Felicidades {jugador['nombre']}! Has cruzado exitosamente."
            if self.ganador == jugador['nombre']:
                mensaje += " ¡Eres el ganador!"
            return froggy_pb2.EstadoResponse(estado="CRUZO", mensaje=mensaje)
        elif not jugador['vivo']:
            return froggy_pb2.EstadoResponse(
                estado="ATROPELLADO", 
                mensaje=f"{jugador['nombre']} fue atropellado por un auto"
            )
        else:
            return froggy_pb2.EstadoResponse(
                estado="VIVO", 
                mensaje=f"{jugador['nombre']} sigue en el juego"
            )

def servir():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    froggy_pb2_grpc.add_FroggyGameServicer_to_server(FroggyGameServicer(), servidor)
    servidor.add_insecure_port('[::]:50051')
    servidor.start()
    print("Servidor Froggy Revenge iniciado en puerto 50051")
    servidor.wait_for_termination()

if __name__ == '__main__':
    servir()
