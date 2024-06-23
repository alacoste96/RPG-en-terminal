# RPG-en-terminal
En este repo encontrarás el código que corresponde a un servidor que ofrece un servicio de un videojuego RPG en terminal y el cliente para conectarse.


Cada partida concierne a 2 jugadores que intentarán superar a 3 enemigos en cada nivel y serán curados cada vez que sobrepasen cada nivel.

El servidor puede gestionar múltiples partidas al mismo tiempo.

El fichero **protocols.py** contiene constantes y funciones usados por el cliente y servidor mutuamente.

El fichero **enemies.py** contiene las clases de los enemigos que pueden aparecer en el minijuego.

El fichero **characters.py** contiene la sclases de los personajes que se pueden elegir para jugar al minijuego.

El fichero **game.py** contiene la clase del juego y sus funciones.

El fichero **server.py** contiene el código del servidor que hace uso de todos los demás ficheros excepto del de clients.py.

El fichero **client.py** contiene el código del cliente que hace uso del fichero **protocols.py**.

# Cómo jugar:

Lo primero es lanzar el servidor. Se le puede añadir un parámetro opcional para indicar el puerto en el que se quiera que escuche el servidor. El puerto por defecto es el 7123.

El puerto se indica con la opción -p 'numero'

Ejemplo:

```bash
python3 server.py -p 7777
```


A continuación en otra terminal, lanzar un cliente. Se le tiene que añadir obligatoriamente un parámetro indicando el nombre y opcionalmente otros 3 parámetros indicando el número de niveles, la ip a conectarse y el puerto a conectarse. Por defecto, se juega sólo un nivel, la ip es 127.0.0.1 y el puerto es el 7123.

1. El nombre se indica con la opción -n "nombre"
2. El número de niveles se indica con la opción -s "numero"
3. La ip se indica con la opción -i "ip"
4. El puerto se indica con la opción -p "numero"

Ejemplo:

```bash
python3 client.py -n alex -s 3 -i 127.0.0.1 -p 7777
```

Al conectarse al servidor, el jugador podrá elegir entre 3 opciones: crear una partida, unirse a una o cargar una partida. Al crear una partida se espera a que otro jugador se una a ella, por ello se deberá de abrir y ejecutar en otra terminal el cliente. 

Durante el juego, se da la opción de qué querer hacer. Hay 2 opciones posibles, atacar o guardar partida. 

Para atacar hay que introducir el carácter: **a**.

Para guardar la partida hay que introducir el carácter: **s**

Para salir del juego basta con introducir **ctrl+C**.

## Nota importante

Este proyecto corresponde a mi primer proyecto haciendo uso de Sockets TCP/IP para la asignatura de la universidad Rey Juan Carlos llamada Programación de Sistemas de Telecomunicaciones y el cuál me garantizó una matrícula de honor. Sin embargo, hay mucho que corregir, mejorar y agregar después de repasarlo teniendo más conocimiento del lenguaje. Pero lo dejo tal cual a modo de recordar el primer escalón en el camino de mi aprendizaje con python. Si encontráis algún bug y alguna barbaridad, abrazarlos y disfrutarlos; es para vosotros, jugadores.




