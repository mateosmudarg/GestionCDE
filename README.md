# Panel de Control Django

Un panel de control moderno y funcional enfocado en los centros de estudiantes construido con **Django**, **Python** y **Bootstrap**.

---

## 📦 Tecnologías utilizadas

- **Python** – lenguaje principal del backend.
- **Django** – framework web para la estructura del proyecto.
- **Bootstrap 5** – para diseño responsivo y componentes UI.
- **Chart.js** – para visualización de datos.
- **SQLite** – como base de datos (configurable).

---

## 🚀 Instalación

Sigue estos pasos para poner en marcha el proyecto localmente:

1. **Clonar el repositorio**
```bash
git clone https://github.com/mateosmudarg/GestionCDE.git
cd GestionCDE
````

2. **Crear y activar entorno virtual**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones**

```bash
python manage.py migrate
```

5. **Crear superusuario**

```bash
python manage.py createsuperuser
```

6. **Ejecutar el servidor**

```bash
python manage.py runserver
```

Accede a [http://127.0.0.1:8000](http://127.0.0.1:8000) para ver el panel.

---

## 🛠 Roadmap

- **Sistema de elecciones**
    - Carga de listas
    - Seguimiento en tiempo real del escrutinio
    - Carga digital de los resultados
    - Resultados accesibles para todo el publico
- **Gestion avanzadas de eventos**
    - Gestión de torneos: Generación de partidos, Inscripción de equipos, Resultados
    - Reuniones
- **Comunicados**
    - Comunicados del CDE públicos

---

## 🤝 Cómo contribuir

1. Haz un **fork** del repositorio.
2. Crea una nueva rama:

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza los cambios y **commitea**:

```bash
git commit -m "Añadir nueva funcionalidad"
```

4. Haz **push** a tu rama:

```bash
git push origin feature/nueva-funcionalidad
```

5. Abre un **Pull Request** para revisión.

> Asegúrate de mantener el estilo de código consistente y actualizar la documentación si es necesario.

---

## 📚 Recursos adicionales

* [Documentación Django](https://docs.djangoproject.com/)
* [Bootstrap 5](https://getbootstrap.com/)
* [Chart.js](https://www.chartjs.org/)

---


## ⚡ Licencia

Este proyecto está bajo la licencia AGPL v3. Consulta el archivo `LICENSE` para más detalles.
