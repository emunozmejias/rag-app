#!/usr/bin/env python3
"""
Script para consultar las tablas y datos de las bases de datos PostgreSQL
del proyecto RAG.

Uso:
    python query_database.py
    python query_database.py --database vector  # Solo vector store
    python query_database.py --database history # Solo historial
    python query_database.py --table <nombre_tabla>  # Consultar tabla específica
"""

import argparse
import sys
from psycopg import connect
from psycopg.rows import dict_row


# Configuración de conexiones
VECTOR_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "database164",
    "user": "postgres",
    "password": ""  # Sin contraseña por defecto
}

HISTORY_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pdf_rag_history",
    "user": "postgres",
    "password": "postgres"
}


def get_connection_string(config):
    """Construye la cadena de conexión PostgreSQL"""
    if config["password"]:
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
    else:
        return f"postgresql://{config['user']}@{config['host']}:{config['port']}/{config['dbname']}"


def list_tables(conn):
    """Lista todas las tablas en la base de datos"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        return [table[0] for table in tables]


def get_table_info(conn, table_name):
    """Obtiene información sobre las columnas de una tabla"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        return cur.fetchall()


def count_rows(conn, table_name):
    """Cuenta las filas en una tabla"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        return cur.fetchone()[0]


def get_table_data(conn, table_name, limit=10):
    """Obtiene datos de una tabla (limitado)"""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(f"SELECT * FROM {table_name} LIMIT %s;", (limit,))
        return cur.fetchall()


def query_vector_store():
    """Consulta la base de datos del vector store"""
    print("\n" + "="*80)
    print("BASE DE DATOS: database164 (Vector Store)")
    print("="*80)
    
    try:
        conn = connect(get_connection_string(VECTOR_DB_CONFIG))
        print("✓ Conexión exitosa\n")
        
        tables = list_tables(conn)
        print(f"Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table}")
        
        print("\n" + "-"*80)
        
        for table in tables:
            print(f"\n📊 TABLA: {table}")
            print("-"*80)
            
            # Información de columnas
            columns = get_table_info(conn, table)
            print("\nColumnas:")
            for col in columns:
                col_name, data_type, max_length, nullable = col
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  • {col_name}: {data_type}{length_info} {null_info}")
            
            # Conteo de filas
            try:
                row_count = count_rows(conn, table)
                print(f"\nTotal de filas: {row_count}")
            except Exception as e:
                print(f"\n⚠ No se pudo contar filas: {e}")
            
            # Muestra de datos (limitado)
            if row_count > 0:
                print(f"\nPrimeras {min(5, row_count)} filas:")
                try:
                    data = get_table_data(conn, table, limit=5)
                    for i, row in enumerate(data, 1):
                        print(f"\n  Fila {i}:")
                        for key, value in row.items():
                            # Truncar valores muy largos (como embeddings)
                            if isinstance(value, (bytes, str)) and len(str(value)) > 100:
                                display_value = str(value)[:100] + "... [truncado]"
                            else:
                                display_value = value
                            print(f"    {key}: {display_value}")
                except Exception as e:
                    print(f"  ⚠ No se pudieron leer datos: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a database164: {e}")
        print("\nVerifica que:")
        print("  - PostgreSQL esté corriendo")
        print("  - La base de datos 'database164' exista")
        print("  - Las credenciales sean correctas")


def query_chat_history():
    """Consulta la base de datos del historial de chat"""
    print("\n" + "="*80)
    print("BASE DE DATOS: pdf_rag_history (Chat History)")
    print("="*80)
    
    try:
        conn = connect(get_connection_string(HISTORY_DB_CONFIG))
        print("✓ Conexión exitosa\n")
        
        tables = list_tables(conn)
        print(f"Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table}")
        
        print("\n" + "-"*80)
        
        for table in tables:
            print(f"\n📊 TABLA: {table}")
            print("-"*80)
            
            # Información de columnas
            columns = get_table_info(conn, table)
            print("\nColumnas:")
            for col in columns:
                col_name, data_type, max_length, nullable = col
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  • {col_name}: {data_type}{length_info} {null_info}")
            
            # Conteo de filas
            try:
                row_count = count_rows(conn, table)
                print(f"\nTotal de filas: {row_count}")
            except Exception as e:
                print(f"\n⚠ No se pudo contar filas: {e}")
            
            # Muestra de datos (limitado)
            if row_count > 0:
                print(f"\nPrimeras {min(10, row_count)} filas:")
                try:
                    data = get_table_data(conn, table, limit=10)
                    for i, row in enumerate(data, 1):
                        print(f"\n  Fila {i}:")
                        for key, value in row.items():
                            print(f"    {key}: {value}")
                except Exception as e:
                    print(f"  ⚠ No se pudieron leer datos: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a pdf_rag_history: {e}")
        print("\nVerifica que:")
        print("  - PostgreSQL esté corriendo")
        print("  - La base de datos 'pdf_rag_history' exista")
        print("  - Las credenciales sean correctas")


def query_specific_table(database, table_name):
    """Consulta una tabla específica"""
    config = VECTOR_DB_CONFIG if database == "vector" else HISTORY_DB_CONFIG
    db_name = "database164" if database == "vector" else "pdf_rag_history"
    
    print(f"\n📋 Consultando tabla '{table_name}' en {db_name}")
    print("="*80)
    
    try:
        conn = connect(get_connection_string(config))
        
        # Verificar que la tabla existe
        tables = list_tables(conn)
        if table_name not in tables:
            print(f"❌ La tabla '{table_name}' no existe en {db_name}")
            print(f"\nTablas disponibles: {', '.join(tables)}")
            conn.close()
            return
        
        # Información de columnas
        columns = get_table_info(conn, table_name)
        print("\nColumnas:")
        for col in columns:
            col_name, data_type, max_length, nullable = col
            length_info = f"({max_length})" if max_length else ""
            null_info = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"  • {col_name}: {data_type}{length_info} {null_info}")
        
        # Conteo de filas
        row_count = count_rows(conn, table_name)
        print(f"\nTotal de filas: {row_count}")
        
        # Todos los datos (o limitado si son muchos)
        if row_count > 0:
            limit = 50 if row_count > 50 else row_count
            print(f"\nDatos (mostrando {limit} de {row_count}):")
            data = get_table_data(conn, table_name, limit=limit)
            for i, row in enumerate(data, 1):
                print(f"\n  Fila {i}:")
                for key, value in row.items():
                    # Truncar valores muy largos
                    if isinstance(value, (bytes, str)) and len(str(value)) > 200:
                        display_value = str(value)[:200] + "... [truncado]"
                    else:
                        display_value = value
                    print(f"    {key}: {display_value}")
        else:
            print("\nLa tabla está vacía.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta las tablas y datos de las bases de datos PostgreSQL del proyecto RAG"
    )
    parser.add_argument(
        "--database",
        choices=["vector", "history", "all"],
        default="all",
        help="Base de datos a consultar (default: all)"
    )
    parser.add_argument(
        "--table",
        type=str,
        help="Nombre de tabla específica a consultar (requiere --database)"
    )
    
    args = parser.parse_args()
    
    if args.table and not args.database:
        print("❌ Error: --table requiere especificar --database")
        sys.exit(1)
    
    if args.table:
        db = args.database if args.database != "all" else "vector"
        query_specific_table(db, args.table)
    else:
        if args.database in ["vector", "all"]:
            query_vector_store()
        
        if args.database in ["history", "all"]:
            query_chat_history()
        
        print("\n" + "="*80)
        print("✅ Consulta completada")
        print("="*80)
        print("\n💡 Tip: Usa --table <nombre> para consultar una tabla específica")
        print("   Ejemplo: python query_database.py --database vector --table langchain_pg_embedding")


if __name__ == "__main__":
    main()
