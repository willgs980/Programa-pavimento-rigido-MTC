import math
import random
from site import makepath
import tkinter as tk
from tkinter import messagebox, Toplevel, filedialog
from PIL import Image, ImageTk, ImageDraw  # Para redimensionar las imágenes
import os

os.chdir(r"C:/Users/fsalinas/Downloads/AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC")


def aashto_equation(D, W82, Zr, So, delta_PSI, Pt, Mr, Cd, J, Ec, k):
    term1 = Zr * So
    term2 = 7.35 * math.log10(D + 25.4)
    term3 = -10.39
    term4 = math.log10(delta_PSI / (4.5 - 1.5)) / (1 + (1.25 * 10**19) / ((D + 25.4)**8.46))
    term5 = (4.22 - 0.32 * Pt) * math.log10(
        (Mr * Cd * (0.09 * D**0.75 - 1.132)) / (1.51 * J * (0.09 * D**0.75 - (7.38 / (Ec / k)**0.25)))
    )
    return term1 + term2 + term3 + term4 + term5 - math.log10(W82)

def aashto_equation_derivative(D, delta_PSI, Mr, Cd, J, Ec, k):
    term2 = 7.35 / (D + 25.4) / math.log(10)
    term4 = (
        (-8.46 * (1.25 * 10**19) * math.log10(delta_PSI / (4.5 - 1.5)))
        / ((D + 25.4)**9.46 * (1 + (1.25 * 10**19) / ((D + 25.4)**8.46))**2)
    )
    term5 = (0.75 * 0.09 * Mr * Cd * D**-0.25) / (
        1.51 * J * math.log(10) * (0.09 * D**0.75 - (7.38 / (Ec / k)**0.25))
    )
    return term2 + term4 + term5

def solve_thickness(W82, Zr, So, delta_PSI, Pt, Mr, Cd, J, Ec, k, initial_guess=200, tolerance=1e-6, max_iterations=100):
    D = initial_guess
    for _ in range(max_iterations):
        f_D = aashto_equation(D, W82, Zr, So, delta_PSI, Pt, Mr, Cd, J, Ec, k)
        f_D_derivative = aashto_equation_derivative(D, delta_PSI, Mr, Cd, J, Ec, k)
        if abs(f_D_derivative) < 1e-10:  # Evitar división por cero
            return None
        D_next = D - f_D / f_D_derivative
        if abs(D_next - D) < tolerance:
            return D_next
        D = D_next
    return None

def calculate():
    try:
        W82 = float(entry_W82.get())
        Zr = float(entry_Zr.get())
        So = float(entry_So.get())
        Po = float(entry_Po.get())
        Pt = float(entry_Pt.get())
        delta_PSI = Po - Pt
        Mr = float(entry_Mr.get())
        Cd = float(entry_Cd.get())
        J = float(entry_J.get())
        Ec = float(entry_Ec.get())
        k = float(entry_k.get())

        result = solve_thickness(W82, Zr, So, delta_PSI, Pt, Mr, Cd, J, Ec, k)

        if result is not None:
            messagebox.showinfo("Resultado", f"El espesor del pavimento (D) es aproximadamente {result:.2f} mm.")
        else:
            messagebox.showerror("Error", "No se pudo calcular el espesor del pavimento (D).")
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")

def create_input_with_description(root, label_text, description_text, row):
    """Crea una fila con una etiqueta, entrada y descripción debajo."""
    label = tk.Label(root, text=label_text)
    label.grid(row=row, column=0, sticky="w")
    entry = tk.Entry(root)
    entry.grid(row=row, column=1)
    description = tk.Label(root, text=description_text, wraplength=300, fg="gray")
    description.grid(row=row+1, column=0, columnspan=2, sticky="w")
    return entry

def open_formula_window():
    formula_window = tk.Toplevel(root)
    formula_window.title("Fórmula AASHTO")
    formula_original = Image.open(r"C:/Users/fsalinas/Downloads/AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC/MTC PAVIMENTO RIGIDO/PROGRAMA PAV. RIGIDO CALCULO POR MTC/FORMULA.png")
    formula_image = ImageTk.PhotoImage(formula_original)
    formula_label = tk.Label(formula_window, image=formula_image)
    formula_label.image = formula_image
    formula_label.pack()

def open_variables_window():
    variables_window = tk.Toplevel(root)
    variables_window.title("Variables de la Fórmula")
    variables_original = Image.open(r"C:/Users/fsalinas/Downloads/AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC/DESCRIPCION.png")
    variables_image = ImageTk.PhotoImage(variables_original)
    variables_label = tk.Label(variables_window, image=variables_image)
    variables_label.image = variables_image
    variables_label.pack()


class ArrowDrawingApp:
    def __init__(self, root, image_path):
        self.root = root
        try:
            # Cargar la imagen desde la ruta especificada
            self.image = Image.open(image_path,r"Cuadro Pavimento MTC")
            self.draw = ImageDraw.Draw(self.image)
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró la imagen: {image_path}")
            raise
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al cargar la imagen: {e}")
            raise

        # Configurar ventana principal
        self.root.title("Dibujo de Flechas sobre Imagen")

        # Variables para el dibujo
        self.drawing = True
        self.start_point = None

        # Configuración del canvas
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Botones
        self.stop_button = tk.Button(root, text="Guardar Imagen", command=self.save_image)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.resume_button = tk.Button(root, text="Reanudar Dibujo", command=self.resume_drawing)
        self.resume_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Eventos de clic
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if not self.drawing:
            return

        if self.start_point is None:
            self.start_point = (event.x, event.y)
        else:
            end_point = (event.x, event.y)
            self.draw.line([self.start_point, end_point], fill="red", width=2)
            self.start_point = None
            self.update_canvas()

    def update_canvas(self):
        """Actualiza el canvas con la imagen modificada."""
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def save_image(self):
        """Guarda la imagen en la ruta seleccionada."""
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image = Image.open(makepath)
            self.image.save(file_path)
            messagebox.showinfo("Guardar Imagen", f"Imagen guardada en: {file_path}")

    def resume_drawing(self):
        """Permite reanudar el dibujo."""
        self.drawing = True
        print("Dibujo reanudado.")


def main():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Aplicación de Dibujo de Flechas")

    # Especificar la ruta de la imagen a cargar automáticamente
    image_path = r"C:/Users/fsalinas/Downloads/AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC/Cuadro Pavimento MTC.png"  # Cambia a la ruta deseada si no está en el mismo directorio

    # Inicializar la aplicación
    try:
        ArrowDrawingApp(root, image_path)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")


def check_image_path(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        messagebox.showerror("Error", f"No se encontró el archivo: {ruta_imagen}")
        return False
    return True

ruta_imagen = r"C:/Users/fsalinas/Downloads/AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC/Cuadro Pavimento MTC.png"
if check_image_path(ruta_imagen):
    main()



if __name__ == "__main__":
    main()



# Función para abrir la interfaz de cálculo de K
def open_calculate_k_window():
    k_window = Toplevel(root)
    k_window.title("Cálculo del Módulo de Reacción Compuesto (K)")

    # Título y descripción
    title_label = tk.Label(k_window, text="Cálculo del Módulo de Reacción Compuesto (K)", font=("Arial", 14, "bold"))
    title_label.pack(pady=5)

    description_label = tk.Label(k_window, text="""
Para el cálculo del Módulo de Reacción Compuesto (K), se requiere de los coeficientes 
de reacción de la subbase granular (K1) y la subrasante (K0), con unidades en kg/cm³.
    """, justify="left")
    description_label.pack()


    # Botones para iniciar y detener dibujo
    def start_editing():
        editor_window = Toplevel(k_window)
        ArrowDrawingApp(editor_window, r"C:\Users\fsalinas\Downloads\AVANCE PAVIMENTO RIGIDO ASSHTO Y MTC\Cuadro Pavimento MTC.png")
        editor_window.mainloop()

    start_button = tk.Button(k_window, text="Iniciar Edición", command=start_editing)
    start_button.pack(pady=5)

    # Casillas de entrada
    frame_inputs = tk.Frame(k_window)
    frame_inputs.pack(pady=10)

    tk.Label(frame_inputs, text="h (Espesor de la subbase granular):").grid(row=0, column=0, sticky="w")
    entry_h = tk.Entry(frame_inputs)
    entry_h.grid(row=0, column=1)

    tk.Label(frame_inputs, text="K1 (kg/cm³, Subbase granular):").grid(row=1, column=0, sticky="w")
    entry_k1 = tk.Entry(frame_inputs)
    entry_k1.grid(row=1, column=1)

    tk.Label(frame_inputs, text="K0 (kg/cm³, Subrasante):").grid(row=2, column=0, sticky="w")
    entry_k0 = tk.Entry(frame_inputs)
    entry_k0.grid(row=2, column=1)

    # Resultado y fórmula
    result_label = tk.Label(k_window, text="", font=("Arial", 12))

    def calculate_k():
        try:
            h = float(entry_h.get())
            k1 = float(entry_k1.get())
            k0 = float(entry_k0.get())
            k = ((1 + (h / 38) ** 2 * (k1 / k0) ** (2 / 3)) ** 0.5) * k0
            result_label.config(text=f"K = {k:.3f} kg/cm³")
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")

    tk.Button(k_window, text="Calcular K", command=calculate_k).pack(pady=5)
    result_label.pack(pady=5)

    # Descripción de las variables
    description_variables = tk.Label(k_window, text="""
K (kg/cm³): Coeficiente de reacción combinado
K1 (kg/cm³): Coeficiente de reacción de la subbase granular
K0 (kg/cm³): Coeficiente de reacción de la subrasante
h: Espesor de la subbase granular
    """, justify="left", fg="gray")
    description_variables.pack(pady=5)


# Crear la ventana principal
root = tk.Tk()
root.title("Cálculo de Espesor de Pavimento (D)")

# Botones para abrir ventanas con las imágenes
button_formula = tk.Button(root, text="Ver Fórmula", command=open_formula_window)
button_formula.grid(row=0, column=0, padx=5, pady=5)

button_variables = tk.Button(root, text="Ver Variables", command=open_variables_window)
button_variables.grid(row=0, column=1, padx=5, pady=5)

# Botones para calcular K
button_calculate_k = tk.Button(root, text="Cálculo de K", font=("Arial", 12), command=open_calculate_k_window)
button_calculate_k.grid(row=19, column=2, padx=5, pady=5)


# Crear las entradas con descripciones debajo
entry_W82 = create_input_with_description(root, "W82:", "Número previsto de ejes equivalentes de 8.2 toneladas métricas.", 1)
entry_Zr = create_input_with_description(root, "Zr:", "Desviación normal estándar.", 3)
entry_So = create_input_with_description(root, "So:", "Error estándar combinado en la predicción del tránsito.", 5)
entry_Po = create_input_with_description(root, "Po:", "Índice de servicio inicial.", 7)
entry_Pt = create_input_with_description(root, "Pt:", "Índice de serviciabilidad o servicio final.", 9)
entry_Mr = create_input_with_description(root, "Mr:", "Resistencia media del concreto (MPa) a flexotracción.", 11)
entry_Cd = create_input_with_description(root, "Cd:", "Coeficiente de drenaje.", 13)
entry_J = create_input_with_description(root, "J:", "Coeficiente de transmisión de cargas en las juntas.", 15)
entry_Ec = create_input_with_description(root, "Ec:", "Módulo de elasticidad del concreto (MPa).", 17)
entry_k = create_input_with_description(root, "k:", "Módulo de reacción, dado en MPa/m de la superficie.", 19)

# Botón para calcular
button_calculate = tk.Button(root, text="Calcular Espesor (D)", command=calculate)
button_calculate.grid(row=21, column=0, columnspan=2, pady=10)

print(f"Ruta de la imagen: {makepath}")
print(f"Directorio actual: {os.getcwd()}")


# Iniciar el bucle de la interfaz gráfica
root.mainloop()
