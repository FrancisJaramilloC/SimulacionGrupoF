# SimulacionGrupoF
El siguiente sistema sigue un patron de diseño modular con separacion de responsabilidades.
##modelos.py
Define las estructuras de datos fundamentales del sistema.
###Tipo de caja
Esta representacion es un Enum, en la que se definen, la caja normal, la cual no tiene limite de articulos y la caja express, la cual posee un limite de articulos.
###Cliente(DataClass)
Representa a un cliente en la fila de espera y cuenta con los siguiente atributos:
- id: Identificador unico del cliente.
- num_articulos: La cantidad de articulos que lleva.
- tiempo_cobro: La cantidad de timpo para procesar el pago.
Tambien cuenta con el siguiente metodo:
- __repr__(): Es la representacion visual del cliente mostrando el numero de articulos.

###Caja(DataClass)
Representa una caja registradora del supermercado y cuenta con los siguientes atributos:
- numero: Es el numero con el que se identifica la caja.
- tipo: Muestra que tipo de caja es, ya sea express o normal.
- tiempo_escaneo: El tiempo que tarda en escanear cada articulo.
- clientes: Lista los clientes que se encuentran en la fila.
- max_articulos: Es limite maximo de articulos que puede tener el cliente.
Tambien cuenta con los siguientes metodos:
- calular_tiempo_total: Este metodo calcula el tiempo total de espera, sumando el tiempo de todos los clientes en la fila.
- atender_cliente: Remueve y retorna el primer cliente de la fila.
- puede_usar_caja: Verifica si un cliente puede usar una caja dependiendo el limite de articulos.
- agregar_cliente: Agrega un cliente al final de la fila
##tuti.py
Esta clase se encarga de administrar las cajas y la logica general del sistema y los metodos que se utiliza son los siguientes:
- agregar_caja: Crea y agrega una nueva caja(normal o express).
- encontrar_mejor_caja(num_articulos): Este metodo se encarga de encontrar la mejor caja segun el tiempo de espera.
- tiene_clientes_en_espera: Este metodo verifica si quedan clientes por atender.
- atender_todos: Este metodo atiende un cliente de cada caja con fila.

##generador_clientes.py
Esta clase crea clientes aleatorios con distintas caracteristicas y los metodos que tiene son los siguientes:
- generar_cliente(maz_articulos = 50): Este metodo se encarga de crear un cliente con articulos y tiempo aleatorios.
- generar_multiples_clientes(maz_articulos = 50): Este metodo se encarga de generar varios clientes a la vez.

##configurador.py
Esta clase permite crear las cjas mediante la consola, solicitando datos al usuario.
Ejemplo de flujo: 
1. Pide cantidad de cajas normales y express.
2. Solicita numero de clientes y velocidad de escaneo para cada una.
3. Crea las cajas en el sistema.

##visualizador.py
Esta clase muestra el estado actual del supermercado y las cajas y cumple con las siguientes funciones:
- limpiar_pantalla: Limpia la consola.
- mostrar_cabecera: Muestra el titulo del sistema.
- mostrar_caja(caja): Muestra detalles de cada caja y su fila.
- mostar_atencion(caja, cliente, tiempo): Muestra si el cliente esta siendo atendido y en que caja.
- mostrar_recomendacion(caja, num_articulos): Muestra al usuario cual seria la caja mas rapida.
  
##simulador.py
Ejecuta la simulacion paso a paso. 
##menu.py
##main.py
