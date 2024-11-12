import customtkinter as ctk
import pymysql
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

def mostrar_panel_datos(frame_principal, callback_regresar=None):
    # Configuración de la conexión a la base de datos
    db_config = {
        'host': 'b4qhbwwqys2nhher1vul-mysql.services.clever-cloud.com',
        'port': 3306,
        'db': 'b4qhbwwqys2nhher1vul',
        'user': 'upvge9afjesbmmgv',
        'passwd': 'BS2bxJNACO1XYEmWBqA0'
    }

    def obtener_datos():
        try:
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()

            # Consulta para ingresos por jornada
            cursor.execute("""
                SELECT e.jornada, COUNT(*) as cantidad 
                FROM estudiante e
                JOIN ingreso i ON e.codigo_est = i.codigo_est
                WHERE i.fecha = CURDATE()
                GROUP BY e.jornada
            """)
            datos_jornada = pd.DataFrame(cursor.fetchall(), columns=['Jornada', 'Cantidad'])

            # Consulta para horas de llegada del día actual
            cursor.execute("""
                SELECT HOUR(i.hora) as hora, COUNT(*) as cantidad 
                FROM ingreso i
                WHERE i.fecha = CURDATE()
                GROUP BY HOUR(i.hora)
                ORDER BY hora
            """)
            datos_horas = pd.DataFrame(cursor.fetchall(), columns=['Hora', 'Cantidad'])

            # Consulta para total de estudiantes
            cursor.execute("SELECT COUNT(*) FROM estudiante")
            total_estudiantes = cursor.fetchone()[0]

            # Consulta para ingresos del día
            cursor.execute("SELECT COUNT(*) FROM ingreso WHERE fecha = CURDATE()")
            ingresos_hoy = cursor.fetchone()[0]

            # Consulta para obtener distribución por grupos
            cursor.execute("""
                SELECT grupo, COUNT(*) as cantidad
                FROM estudiante
                GROUP BY grupo
            """)
            datos_grupos = pd.DataFrame(cursor.fetchall(), columns=['Grupo', 'Cantidad'])

            cursor.close()
            conn.close()

            return datos_jornada, datos_horas, total_estudiantes, ingresos_hoy, datos_grupos

        except Exception as e:
            print(f"Error al obtener datos: {e}")
            return None, None, 0, 0, None

    # Crear el contenedor principal
    container = ctk.CTkFrame(frame_principal)
    container.pack(fill='both', expand=True, padx=20, pady=20)

    # Título
    titulo = ctk.CTkLabel(container, text="Panel de Control - Eye System", font=("Roboto", 24, "bold"))
    titulo.pack(pady=10)

    # Obtener datos
    datos_jornada, datos_horas, total_estudiantes, ingresos_hoy, datos_grupos = obtener_datos()

    # Frame para estadísticas principales
    stats_frame = ctk.CTkFrame(container)
    stats_frame.pack(fill='x', pady=10, padx=20)

    # Grid para estadísticas
    stats_frame.grid_columnconfigure((0, 1), weight=1)

    # Mostrar estadísticas principales
    ctk.CTkLabel(
        stats_frame,
        text=f"Total de Estudiantes: {total_estudiantes}",
        font=("Roboto", 16, "bold")
    ).grid(row=0, column=0, pady=10, padx=10)

    ctk.CTkLabel(
        stats_frame,
        text=f"Ingresos Hoy: {ingresos_hoy}",
        font=("Roboto", 16, "bold")
    ).grid(row=0, column=1, pady=10, padx=10)

    # Crear figura para los gráficos
    fig = plt.figure(figsize=(12, 8))
    
    # Configurar estilo de los gráficos
    plt.rcParams['axes.grid'] = True
    plt.rcParams['figure.facecolor'] = '#f0f0f0'
    plt.rcParams['axes.facecolor'] = 'white'

    # Ajustar el espacio entre subplots
    plt.subplots_adjust(hspace=0.5, wspace=0.3)

    # Gráfico de ingresos por jornada
    ax1 = fig.add_subplot(221)
    if datos_jornada is not None and not datos_jornada.empty:
        datos_jornada.plot(kind='bar', x='Jornada', y='Cantidad', ax=ax1, color='#2d4f7c')
        ax1.set_title('Ingresos por Jornada (Hoy)', pad=15)
        ax1.set_ylabel('Cantidad de Ingresos')
        plt.xticks(rotation=45)
    else:
        ax1.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center')

    # Gráfico de horas de llegada
    ax2 = fig.add_subplot(222)
    if datos_horas is not None and not datos_horas.empty:
        datos_horas.plot(kind='line', x='Hora', y='Cantidad', marker='o', ax=ax2, color='#2d4f7c', linewidth=2)
        ax2.set_title('Distribución de Horas de Llegada (Hoy)', pad=15)
        ax2.set_xlabel('Hora del Día')
        ax2.set_ylabel('Cantidad de Estudiantes')
    else:
        ax2.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center')

    # Gráfico de distribución por grupos
    ax3 = fig.add_subplot(223)
    if datos_grupos is not None and not datos_grupos.empty:
        # Ordenar los datos de mayor a menor
        datos_grupos = datos_grupos.sort_values('Cantidad', ascending=False)

        # Centrar el gráfico circular
        ax3.set_position([1, 0.2, 0.5, 0.6])

        # Crear el pie chart sin etiquetas
        wedges, texts, autotexts = ax3.pie(
            datos_grupos['Cantidad'],
            autopct='%1.1f%%',
            pctdistance=0.85,
            startangle=90
        )

        # Configurar la leyenda fuera del gráfico
        ax3.legend(
            wedges,
            datos_grupos['Grupo'],
            title="Grupos",
            loc="center left",
            bbox_to_anchor=(1.05, 0.5),  # Posición de la leyenda
            fontsize=10
        )

        ax3.set_title('Distribución por Grupos', pad=20, x= 1.2)
        ax3.axis('equal')  # Asegura que el pie chart sea un círculo
    else:
        ax3.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center')
    plt.subplots_adjust(hspace=0.5, wspace=0.4)

    # Crear el canvas para los gráficos
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)

    # Botón de actualizar
    def actualizar_datos():
        for widget in container.winfo_children():
            widget.destroy()
        mostrar_panel_datos(frame_principal, callback_regresar)

    btn_actualizar = ctk.CTkButton(
        container,
        text="Actualizar Datos",
        command=actualizar_datos,
        fg_color="#2d4f7c"
    )
    btn_actualizar.pack(pady=10)