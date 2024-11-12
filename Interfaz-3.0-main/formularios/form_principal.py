# form_principal.py

import customtkinter as ctk
from PIL import Image
from pathlib import Path
from formularios.form_maestro_design import FormularioMaestroDesign
from formularios.form_administradores_design import FormularioAdministradorDesign
import requests
from tkinter import messagebox
import os

# Definición de colores (tema moderno)
COLOR_MITAD_IZQUIERDA = "#1a1b26"  # Azul oscuro
COLOR_MITAD_DERECHA = "#f0f5ff"    # Azul claro

class FormCrearIniciarSesion(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración básica
        self.title('Sistema de Inicio de Sesión')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-40}+0+0")
        self.resizable(True, True)
        
        # Inicializar frames y elementos
        self.frame_administrador = None
        self.frame_usuario = None
        self.logo_image = None
        self.escudo_image = None
        self.button_administrador = None
        self.button_usuario = None
        
        # Configurar interfaz
        self.cargar_imagenes()
        self.crear_interfaz()
        
    def cargar_imagenes(self):
        try:
            possible_paths = [
                Path(__file__).parent / "imagenes",
                Path(__file__).parent.parent / "imagenes",
                Path.cwd() / "imagenes"
            ]
            
            logo_path = None
            escudo_path = None
            
            for base_path in possible_paths:
                if (base_path / "Logo.png").exists():
                    logo_path = base_path / "Logo.png"
                if (base_path / "sistemas_transparente.png").exists():
                    escudo_path = base_path / "sistemas_transparente.png"
                if logo_path and escudo_path:
                    break
            
            if logo_path:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(400, 300)
                )
            
            if escudo_path:
                self.escudo_image = ctk.CTkImage(
                    light_image=Image.open(escudo_path),
                    dark_image=Image.open(escudo_path),
                    size=(200, 285)
                )
                
        except Exception as e:
            print(f"Error al cargar las imágenes: {e}")

    def crear_interfaz(self):
        # Frame principal
        self.cuerpo_principal = ctk.CTkFrame(self)
        self.cuerpo_principal.pack(fill='both', expand=True)

        # Panel izquierdo
        self.izquierda = ctk.CTkFrame(self.cuerpo_principal, fg_color=COLOR_MITAD_IZQUIERDA)
        self.izquierda.pack(side='left', fill='both', expand=True)

        # Panel derecho
        self.derecha = ctk.CTkFrame(self.cuerpo_principal, fg_color=COLOR_MITAD_DERECHA)
        self.derecha.pack(side='right', fill='both', expand=True)

        # Logos
        if self.logo_image:
            ctk.CTkLabel(self.izquierda, image=self.logo_image, text="").pack(pady=(50, 20))
        if self.escudo_image:
            ctk.CTkLabel(self.derecha, image=self.escudo_image, text="").pack(pady=(50, 20))

        # Botones principales
        self.button_administrador = ctk.CTkButton(
            self.izquierda,
            text="Iniciar Como Administrador",
            command=self.mostrar_formulario_administrador,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#2d4f7c"
        )
        self.button_administrador.pack(expand=True, padx=50, pady=20)

        self.button_usuario = ctk.CTkButton(
            self.derecha,
            text="Iniciar Como Usuario",
            command=self.mostrar_formulario_usuario,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#2d4f7c"
        )
        self.button_usuario.pack(expand=True, padx=50, pady=20)

        # Frames de formularios
        self.frame_administrador = ctk.CTkFrame(self.izquierda, fg_color=COLOR_MITAD_IZQUIERDA)
        self.frame_usuario = ctk.CTkFrame(self.derecha, fg_color=COLOR_MITAD_DERECHA)

    def mostrar_formulario_administrador(self):
        self.ocultar_formularios()
        self.frame_administrador.pack(fill='both', expand=True)
        self.button_administrador.pack_forget()
        
        for widget in self.frame_administrador.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.frame_administrador,
            text="Iniciar Como Administrador",
            font=("Helvetica", 24, "bold"),
            text_color="white"
        ).pack(pady=(20, 20))

        self.entry_admin_correo = ctk.CTkEntry(
            self.frame_administrador,
            width=300,
            height=40,
            placeholder_text="correo@ejemplo.com",
            corner_radius=10
        )
        self.entry_admin_correo.pack(pady=(5, 15))

        self.entry_admin_contraseña = ctk.CTkEntry(
            self.frame_administrador,
            width=300,
            height=40,
            placeholder_text="Contraseña",
            show="•",
            corner_radius=10
        )
        self.entry_admin_contraseña.pack(pady=(5, 20))

        ctk.CTkButton(
            self.frame_administrador,
            text="Iniciar Sesión",
            command=self.iniciar_sesion_admin,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#2d4f7c"
        ).pack(pady=20)

    def mostrar_formulario_usuario(self):
        self.ocultar_formularios()
        self.frame_usuario.pack(fill='both', expand=True)
        self.button_usuario.pack_forget()
        
        for widget in self.frame_usuario.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.frame_usuario,
            text="Iniciar Como Usuario",
            font=("Helvetica", 24, "bold"),
            text_color="#1a1b26"
        ).pack(pady=(20, 20))

        self.entry_usuario_correo = ctk.CTkEntry(
            self.frame_usuario,
            width=300,
            height=40,
            placeholder_text="correo@ejemplo.com",
            corner_radius=10
        )
        self.entry_usuario_correo.pack(pady=(5, 15))

        self.entry_usuario_contraseña = ctk.CTkEntry(
            self.frame_usuario,
            width=300,
            height=40,
            placeholder_text="Contraseña",
            show="•",
            corner_radius=10
        )
        self.entry_usuario_contraseña.pack(pady=(5, 20))

        ctk.CTkButton(
            self.frame_usuario,
            text="Iniciar Sesión",
            command=self.iniciar_sesion_user,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#2d4f7c"
        ).pack(pady=20)

    def ocultar_formularios(self):
        if self.frame_administrador:
            self.frame_administrador.pack_forget()
            self.button_administrador.pack(expand=True, padx=50, pady=20)
        if self.frame_usuario:
            self.frame_usuario.pack_forget()
            self.button_usuario.pack(expand=True, padx=50, pady=20)

    def iniciar_sesion_admin(self):
        datos = {
            "correo": self.entry_admin_correo.get(),
            "password": self.entry_admin_contraseña.get()
        }

        try:
            response = requests.post("https://app-3520e06f-74cd-43ba-9e12-7429c4f4e834.cleverapps.io/login_admin.php", data=datos)
            if response.status_code == 200:
                respuesta_json = response.json()
                if respuesta_json.get("status") == "success":
                    self.iniciar_sesion_administrador()
                else:
                    messagebox.showerror("Error", respuesta_json.get("message", "Correo electrónico o contraseña incorrectos."))
            else:
                messagebox.showerror("Error", f"Código de estado: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def iniciar_sesion_user(self):
        datos = {
            "email": self.entry_usuario_correo.get(),
            "contraseña": self.entry_usuario_contraseña.get()
        }

        try:
            response = requests.post("https://app-3520e06f-74cd-43ba-9e12-7429c4f4e834.cleverapps.io/login_users.php", data=datos)
            if response.status_code == 200:
                respuesta_json = response.json()
                if respuesta_json.get("status") == "success":
                    self.iniciar_sesion_usuario()
                else:
                    messagebox.showerror("Error", respuesta_json.get("message", "Correo electrónico o contraseña incorrectos."))
            else:
                messagebox.showerror("Error", f"Código de estado: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def iniciar_sesion_usuario(self):
        self.destroy()
        app = FormularioMaestroDesign()
        app.mainloop()

    def iniciar_sesion_administrador(self):
        self.destroy()
        admin_app = FormularioAdministradorDesign()
        admin_app.mainloop()

if __name__ == "__main__":
    app = FormCrearIniciarSesion()
    app.mainloop()