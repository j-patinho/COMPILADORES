import re

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

    def __repr__(self, nivel=0, prefijo=""):
        ret = prefijo + repr(self.valor) + "\n"
        if self.hijos:
            for i, hijo in enumerate(self.hijos):
                if i == len(self.hijos) - 1:  # Si es el último hijo
                    ret += hijo.__repr__(nivel + 1, prefijo + "    └─ ")
                else:  # Si no es el último hijo
                    ret += hijo.__repr__(nivel + 1, prefijo + "    ├─ ")
        return ret

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

# Función para mostrar los tokens agrupados por categoría
def mostrar_tokens_categorizados():
    for categoria, tokens in tokens_categorizados.items():
        if tokens:
            print(f"{categoria}: {', '.join(sorted(tokens))}")
            print()

# Función para realizar el análisis sintáctico (construcción del árbol)
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
            tipo_siguiente, valor_siguiente = tokens[i]
            if tipo_siguiente in ["Número", "Identificador", "Cadena"]:
                valor_nodo = NodoAST(f"Valor: {valor_siguiente}")
                asignacion.agregar_hijo(valor_nodo)
            elif tipo_siguiente == "Palabra clave" and valor_siguiente in {"input", "float"}:
                funcion_nodo = NodoAST(f"Llamada a función: {valor_siguiente}")
                asignacion.agregar_hijo(funcion_nodo)

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
    return raiz

# Función para realizar el análisis semántico
def analisis_semantico(raiz):
    print("\nIniciando análisis semántico...")

    variables_declaradas = set()

    def recorrer_arbol(nodo):
        if "Asignación" in nodo.valor:
            # Verificar que la variable se está declarando
            variable = nodo.hijos[0].valor.split(":")[1].strip()
            variables_declaradas.add(variable)

            # Verificar que el valor es consistente
            valor = nodo.hijos[1].valor.split(":")[1].strip()
            if valor.isdigit():
                print(f"Asignación válida: {variable} = {valor} (entero)")
            elif valor in variables_declaradas:
                print(f"Asignación válida: {variable} = {valor} (identificador)")
            else:
                print(f"Error semántico: La variable '{valor}' no está declarada antes de su uso.")
        
        elif "Llamada a función" in nodo.valor:
            funcion = nodo.valor.split(":")[1].strip()
            if funcion == "print" or funcion == "input":
                print(f"Llamada a función válida: {funcion}")
            else:
                print(f"Error semántico: La función '{funcion}' no está definida.")

        for hijo in nodo.hijos:
            recorrer_arbol(hijo)

    recorrer_arbol(raiz)
    print("Análisis semántico finalizado.")

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
    arbol = generar_arbol_sintactico(tokens)

    # Realizar el análisis semántico
    analisis_semantico(arbol)

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
