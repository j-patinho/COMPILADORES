import re
import tkinter as tk

# Definir las palabras clave y operadores en un lenguaje de programación simple
palabras_clave = {"if", "else", "while", "for", "return", "int", "float", "void", "print", "input"}
operadores = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
separadores = {'(', ')', '{', '}', '[', ']', ';', ','}

# Expresiones regulares para identificar tipos de tokens
token_regex = {
    "palabra_clave": r'\b(?:' + '|'.join(palabras_clave) + r')\b',
    "identificador": r'[a-zA-Z_áéíóúÁÉÍÓÚñÑ][a-zA-Z_0-9áéíóúÁÉÍÓÚñÑ]*',
    "numero": r'\b\d+(\.\d+)?\b',
    "operador": r'(?:' + '|'.join(map(re.escape, operadores)) + r')',
    "separador": r'(?:' + '|'.join(map(re.escape, separadores)) + r')',
    "comentario": r'#.*',
    "cadena": r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
}

# Diccionario para almacenar los tokens clasificados
tokens_categorizados = {
    "Palabra clave": set(),
    "Identificador": set(),
    "Número": set(),
    "Operador": set(),
    "Separador": set(),
    "Comentario": set(),
    "Cadena": set(),
    "Error léxico": set()
}

# Clase para representar un nodo del árbol de sintaxis
class NodoAST:
    def __init__(self, valor, hijos=None):
        self.valor = valor
        self.hijos = hijos if hijos else []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

# Función para categorizar y almacenar los tokens en el diccionario
def categorizar_token(token, tipo):
    tokens_categorizados[tipo].add(token)

# Función para dividir el código en tokens
def tokenizar(codigo):
    scanner = re.Scanner([
        (token_regex["comentario"], lambda scanner, token: ("Comentario", token)),
        (token_regex["palabra_clave"], lambda scanner, token: ("Palabra clave", token)),
        (token_regex["identificador"], lambda scanner, token: ("Identificador", token)),
        (token_regex["numero"], lambda scanner, token: ("Número", token)),
        (token_regex["operador"], lambda scanner, token: ("Operador", token)),
        (token_regex["separador"], lambda scanner, token: ("Separador", token)),
        (token_regex["cadena"], lambda scanner, token: ("Cadena", token)),
        (r'\s+', None),
        (r'.', lambda scanner, token: ("Error léxico", token))
    ])
    tokens, _ = scanner.scan(codigo)
    return tokens

# Función para mostrar los tokens categorizados
def mostrar_tokens_categorizados():
    print("\nTokens Categorizados:")
    for tipo, tokens in tokens_categorizados.items():
        print(f"{tipo}: {', '.join(tokens)}")

# Función para generar el árbol de sintaxis a partir de los tokens
def generar_arbol_sintactico(tokens):
    print("\nGenerando Árbol de Sintaxis...")
    raiz = NodoAST("Programa")

    i = 0
    while i < len(tokens):
        tipo, valor = tokens[i]

        # Manejo de asignaciones
        if tipo == "Identificador" and i + 1 < len(tokens) and tokens[i + 1][1] == "=":
            asignacion = NodoAST("Asignación")
            variable = NodoAST(f"Variable: {valor}")
            asignacion.agregar_hijo(variable)

            i += 2  # Saltar el identificador y el '='
            expresion = NodoAST("Expresión")  # Crear un nodo para la expresión

            # Procesar la primera parte de la expresión (número)
            if i < len(tokens) and tokens[i][0] == "Número":
                valor_nodo = NodoAST(f"Valor: {tokens[i][1]}")
                expresion.agregar_hijo(valor_nodo)
                i += 1  # Saltar el número

            # Procesar operadores y números subsiguientes
            while i < len(tokens) and tokens[i][0] == "Operador":
                operador_nodo = NodoAST(f"Operador: {tokens[i][1]}")
                expresion.agregar_hijo(operador_nodo)
                i += 1  # Saltar el operador

                if i < len(tokens) and tokens[i][0] == "Número":
                    valor_nodo = NodoAST(f"Valor: {tokens[i][1]}")
                    expresion.agregar_hijo(valor_nodo)
                    i += 1  # Saltar el número

            # Agregar la expresión al nodo de asignación
            asignacion.agregar_hijo(expresion)
            raiz.agregar_hijo(asignacion)

        # Manejo de funciones como input() y print()
        elif tipo == "Palabra clave" and valor in {"input", "print"}:
            funcion_nodo = NodoAST(f"Llamada a función: {valor}")
            i += 1  # Saltar la palabra clave

            if i < len(tokens) and tokens[i][1] == "(":
                i += 1  # Saltar el '('
                while i < len(tokens) and tokens[i][1] != ")":
                    if tokens[i][0] in ["Número", "Identificador", "Cadena"]:
                        argumento = NodoAST(f"Argumento: {tokens[i][1]}")
                        funcion_nodo.agregar_hijo(argumento)
                    i += 1
                raiz.agregar_hijo(funcion_nodo)

        elif tipo == "Comentario":
            comentario = NodoAST(f"Comentario: {valor}")
            raiz.agregar_hijo(comentario)

        i += 1

    # Mostrar el árbol de sintaxis generado
    print(raiz)
    mostrar_arbol_grafico(raiz)

# Función para mostrar el árbol de sintaxis en una ventana gráfica
def mostrar_arbol_grafico(nodo):
    ventana = tk.Tk()
    ventana.title("Árbol de Sintaxis")

    canvas = tk.Canvas(ventana)
    canvas.pack(fill=tk.BOTH, expand=True)

    dibujar_nodo(canvas, nodo, 400, 30, 200)
    
    ventana.mainloop()

# Función para dibujar nodos en el canvas
def dibujar_nodo(canvas, nodo, x, y, offset):
    # Dibujar el nodo
    canvas.create_text(x, y, text=nodo.valor, tags="node")

    # Dibujar las líneas hacia los hijos
    for i, hijo in enumerate(nodo.hijos):
        nuevo_x = x - offset // (2 ** (y // 30)) + (i * offset // (2 ** (y // 30)))  # Recalcular posición horizontal
        nuevo_y = y + 50  # Aumentar la posición vertical
        canvas.create_line(x, y + 10, nuevo_x, nuevo_y - 10)  # Línea hacia el hijo
        dibujar_nodo(canvas, hijo, nuevo_x, nuevo_y, offset // 2)  # Llamada recursiva para dibujar el hijo

# Función principal para leer el código y procesarlo
def analizador_lexico():
    print("Introduce el código fuente (presiona dos veces Enter para finalizar):")
    codigo = ""
    linea = input()  # Leer la primera línea
    linea_anterior = None

    # Leer hasta que el usuario presione dos veces Enter (líneas vacías consecutivas)
    while not (linea == "" and linea_anterior == ""):
        codigo += linea + "\n"
        linea_anterior = linea
        linea = input()
    
    tokens = tokenizar(codigo)
    for tipo, valor in tokens:
        categorizar_token(valor, tipo)

    mostrar_tokens_categorizados()

    # Generar el árbol de sintaxis después del análisis léxico
    generar_arbol_sintactico(tokens)

# Función para mostrar el menú y manejar las opciones del usuario
def mostrar_menu():
    while True:
        print("Menú:")
        print("1. Analizar código")
        print("2. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            global tokens_categorizados
            tokens_categorizados = {
                "Palabra clave": set(),
                "Identificador": set(),
                "Número": set(),
                "Operador": set(),
                "Separador": set(),
                "Comentario": set(),
                "Cadena": set(),
                "Error léxico": set()
            }
            analizador_lexico()
        elif opcion == "2":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# Ejecutar el menú
if __name__ == "__main__":
    mostrar_menu()