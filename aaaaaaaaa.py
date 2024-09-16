import re

# Definir las palabras clave y operadores en un lenguaje de programación simple
palabras_clave = {"if", "else", "while", "for", "return", "int", "float", "void"}
operadores = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
separadores = {'(', ')', '{', '}', '[', ']', ';', ','}

# Expresiones regulares para identificar tipos de tokens
token_regex = {
    "palabra_clave": r'\b(?:' + '|'.join(palabras_clave) + r')\b',
    # Identificadores con caracteres acentuados y la ñ
    "identificador": r'[a-zA-Z_áéíóúÁÉÍÓÚñÑ][a-zA-Z_0-9áéíóúÁÉÍÓÚñÑ]*',
    "numero": r'\b\d+(\.\d+)?\b',
    "operador": r'(?:' + '|'.join(map(re.escape, operadores)) + r')',
    "separador": r'(?:' + '|'.join(map(re.escape, separadores)) + r')',
    # Comentarios que comienzan con #
    "comentario": r'#.*',
    "cadena": r'"(?:\\.|[^"\\])*"'
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
        (r'.', lambda scanner, token: ("Error léxico", token))  # Cualquier cosa no reconocida es un error
    ])
    tokens, _ = scanner.scan(codigo)
    return tokens

# Función para mostrar los tokens agrupados por categoría
def mostrar_tokens_categorizados():
    for categoria, tokens in tokens_categorizados.items():
        if tokens:  # Imprimir solo si hay tokens en esa categoría
            print(f"{categoria}: {', '.join(sorted(tokens))}")
            print()  # Espacio entre categorías

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

    # Mostrar los tokens agrupados por categoría
    mostrar_tokens_categorizados()

# Función para mostrar el menú y manejar las opciones del usuario
def mostrar_menu():
    while True:
        print("Menú:")
        print("1. Analizar código")
        print("2. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            # Reiniciar el diccionario de tokens antes de cada análisis
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
