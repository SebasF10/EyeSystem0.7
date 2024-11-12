import customtkinter as ctk
import pymysql
from datetime import datetime
from tkcalendar import DateEntry
import pandas as pd
from tkinter import ttk
import tkinter as tk

class TablaScrollable(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Crear el treeview con scrollbar
        self.tree = ttk.Treeview(self, columns=("ID", "Código", "Estudiante", "Grupo", "Jornada", "Fecha", "Hora"), show="headings")
        
        # Definir las columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Estudiante", text="Estudiante")
        self.tree.heading("Grupo", text="Grupo")
        self.tree.heading("Jornada", text="Jornada")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        
        # Configurar el ancho de las columnas
        self.tree.column("ID", width=50)
        self.tree.column("Código", width=100)
        self.tree.column("Estudiante", width=200)
        self.tree.column("Grupo", width=100)
        self.tree.column("Jornada", width=100)
        self.tree.column("Fecha", width=100)
        self.tree.column("Hora", width=100)
        
        # Scrollbars
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Configurar el grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

def obtener_conexion():
    return pymysql.connect(
        host='b4qhbwwqys2nhher1vul-mysql.services.clever-cloud.com',
        port=3306,
        db='b4qhbwwqys2nhher1vul',
        user='upvge9afjesbmmgv',
        password='BS2bxJNACO1XYEmWBqA0'
    )

def mostrar_visualizacion_ingresos(frame_padre, callback_regresar):
    # Frame principal
    frame = ctk.CTkFrame(frame_padre)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Frame para filtros
    frame_filtros = ctk.CTkFrame(frame)
    frame_filtros.pack(fill='x', padx=10, pady=10)
    
    # Filtros
    # Fecha inicio
    ctk.CTkLabel(frame_filtros, text="Fecha Inicio:").pack(side='left', padx=5)
    fecha_inicio = DateEntry(frame_filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
    fecha_inicio.pack(side='left', padx=5)
    
    # Fecha fin
    ctk.CTkLabel(frame_filtros, text="Fecha Fin:").pack(side='left', padx=5)
    fecha_fin = DateEntry(frame_filtros, width=12, background='darkblue', foreground='white', borderwidth=2)
    fecha_fin.pack(side='left', padx=5)
    
    # Grupo
    ctk.CTkLabel(frame_filtros, text="Grupo:").pack(side='left', padx=5)
    grupo_var = tk.StringVar()
    grupo_entry = ctk.CTkEntry(frame_filtros, textvariable=grupo_var)
    grupo_entry.pack(side='left', padx=5)
    
    # Jornada
    ctk.CTkLabel(frame_filtros, text="Jornada:").pack(side='left', padx=5)
    jornada_var = tk.StringVar()
    jornada_combobox = ctk.CTkComboBox(frame_filtros, values=["Todas", "Mañana", "Tarde"], variable=jornada_var)
    jornada_combobox.pack(side='left', padx=5)
    jornada_var.set("Todas")
    
    # Búsqueda
    ctk.CTkLabel(frame_filtros, text="Buscar:").pack(side='left', padx=5)
    busqueda_var = tk.StringVar()
    busqueda_entry = ctk.CTkEntry(frame_filtros, textvariable=busqueda_var, width=200)
    busqueda_entry.pack(side='left', padx=5)
    
    # Tabla
    tabla_frame = TablaScrollable(frame)
    tabla_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def cargar_datos():
        # Limpiar tabla
        for item in tabla_frame.tree.get_children():
            tabla_frame.tree.delete(item)
            
        try:
            conn = obtener_conexion()
            with conn.cursor() as cursor:
                # Construir la consulta SQL base
                sql = """
                SELECT i.id_ingreso, i.codigo_est, 
                       CONCAT(e.apellidos, ', ', e.nombres) as estudiante,
                       e.grupo, e.jornada, i.fecha, i.hora
                FROM ingreso i
                JOIN estudiante e ON i.codigo_est = e.codigo_est
                WHERE 1=1
                """
                params = []
                
                # Aplicar filtros
                if fecha_inicio.get_date():
                    sql += " AND i.fecha >= %s"
                    params.append(fecha_inicio.get_date())
                if fecha_fin.get_date():
                    sql += " AND i.fecha <= %s"
                    params.append(fecha_fin.get_date())
                
                if grupo_var.get():
                    sql += " AND e.grupo LIKE %s"
                    params.append(f"%{grupo_var.get()}%")
                
                if jornada_var.get() != "Todas":
                    sql += " AND e.jornada = %s"
                    params.append(jornada_var.get())
                
                if busqueda_var.get():
                    busqueda = f"%{busqueda_var.get()}%"
                    sql += """ AND (
                        e.codigo_est LIKE %s OR
                        e.nombres LIKE %s OR
                        e.apellidos LIKE %s
                    )"""
                    params.extend([busqueda, busqueda, busqueda])
                
                sql += " ORDER BY i.fecha DESC, i.hora DESC"
                
                cursor.execute(sql, params)
                resultados = cursor.fetchall()
                
                for row in resultados:
                    tabla_frame.tree.insert("", "end", values=row)
                
        except Exception as e:
            print(f"Error al cargar datos: {e}")
        finally:
            if conn:
                conn.close()
    
    # Botón para actualizar datos
    ctk.CTkButton(
        frame_filtros,
        text="Actualizar",
        command=cargar_datos
    ).pack(side='left', padx=10)
    
    # Botón para exportar a Excel
    def exportar_excel():
        try:
            data = []
            columns = ["ID", "Código", "Estudiante", "Grupo", "Jornada", "Fecha", "Hora"]
            
            for item in tabla_frame.tree.get_children():
                data.append(tabla_frame.tree.item(item)['values'])
            
            df = pd.DataFrame(data, columns=columns)
            
            # Obtener la fecha actual para el nombre del archivo
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"ingresos_{fecha_actual}.xlsx"
            
            df.to_excel(nombre_archivo, index=False)
            print(f"Datos exportados a {nombre_archivo}")
            
        except Exception as e:
            print(f"Error al exportar datos: {e}")
    
    ctk.CTkButton(
        frame_filtros,
        text="Exportar Excel",
        command=exportar_excel
    ).pack(side='left', padx=10)
    
    # Cargar datos iniciales
    cargar_datos()