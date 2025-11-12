# 🚀 Guía Rápida - Detector de Tráfico Anómalo

## 5 Minutos para empezar

### Paso 1: Instalación (3 minutos)

**Para Windows:**
```bash
# 1. Abre PowerShell como Administrador
# 2. Navega a la carpeta del proyecto
cd "C:\Users\tu_usuario\OneDrive\Documentos\Detector de tráfico anomalo"

# 3. Ejecuta el instalador
.\install.bat

# 4. Espera a que termine (verás "✓ Instalación completada!")
```

**Para Linux/macOS:**
```bash
cd ~/Detector\ de\ tráfico\ anomalo
chmod +x install.sh
./install.sh
```

### Paso 2: Ejecutar Backend (1 minuto)

**Windows (abre una terminal como Administrador):**
```bash
venv\Scripts\activate.bat
python backend\app.py
```

**Linux/macOS:**
```bash
source venv/bin/activate
sudo python backend/app.py
```

Deberías ver:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Paso 3: Ejecutar Frontend (1 minuto)

**En una NUEVA terminal (sin cerrar la anterior):**
```bash
cd frontend
npm start
```

Deberías ver:
```
Compiled successfully!

You can now view your app in the browser.
  Local:            http://localhost:3000
```

### ¡Listo! 🎉

Abre tu navegador en: **http://localhost:3000**

---

## Usando el Dashboard

### 1. Iniciar Captura
- Click en botón verde **"Iniciar Captura"** en la esquina superior derecha
- Verás que el botón cambia a **"Detener Captura"** en rojo

### 2. Ver Datos en Tiempo Real
- Las estadísticas se actualizan automáticamente
- Los gráficos muestran el tráfico en vivo

### 3. Navegar por Pestañas

```
📈 Resumen        → Gráficos de tráfico y protocolos
⚠️  Anomalías      → Alertas de patrones sospechosos
📦 Paquetes       → Detalles de cada paquete capturado
🔗 Flujos         → Conexiones activas en la red
```

### 4. Interpretar Severidades

```
🔴 CRÍTICO        → Anomalía confirmada, actuar inmediatamente
🟠 ALTO           → Probable amenaza, investigar
🟡 MEDIO          → Comportamiento inusual, monitorear
🟢 BAJO           → Tráfico normal, confianza alta
```

---

## Solución de Problemas Comunes

### ❌ Error: "Permission denied"
```
✅ Solución:
   Windows: Ejecutar terminal como Administrador
   Linux/macOS: Usar sudo con el backend
```

### ❌ "Port 5000 already in use"
```
✅ Solución:
   Otra aplicación usa el puerto 5000
   1. Cierra las otras terminales
   2. Reinicia tu computadora
```

### ❌ "npm: command not found"
```
✅ Solución:
   Node.js no está instalado
   Descarga desde: https://nodejs.org/
```

### ❌ Paquetes no se capturan
```
✅ Solución:
   Windows:
   - Instala Npcap desde https://npcap.com/
   - Reinicia el backend
   
   Linux/macOS:
   - Verifica interfaz en .env
   - Ejecuta con sudo
```

### ❌ Terminal con error rojo en Frontend
```
✅ Solución:
   Espera 30 segundos, suele actualizarse solo
   Si persiste: Presiona Ctrl+C y vuelve a hacer "npm start"
```

---

## Casos de Uso Comunes

### 🔍 Detectar Ataque DDoS
1. Inicia captura
2. Ve a "Anomalías"
3. Busca múltiples paquetes SYN desde misma IP
4. Score de anomalía > 70%

### 🕵️ Investigar Flujo Sospechoso
1. Ir a "Flujos"
2. Ver "Puertos" - muchos puertos diferentes = escaneo
3. Anotar IP origen y destino

### 📊 Generar Reporte
1. Capturar tráfico 5-10 minutos
2. Ir a API: `http://localhost:5000/api/export/anomalies`
3. Guardar JSON para análisis

### 🎓 Educación/Pruebas
1. Generar tráfico: `ping -t localip` (Windows) o `ping -c 0 localhost` (Linux)
2. Abrir múltiples conexiones
3. Ver cómo se detectan en el dashboard

---

## Comandos Útiles

### Ver interfaz de red
**Windows:**
```
ipconfig
```

**Linux/macOS:**
```
ifconfig
o
ip addr show
```

### Detener captura forzadamente
```
Presionar Ctrl+C en la terminal del backend
```

### Ver logs
```
cat logs/detector*.log (Linux/macOS)
type logs\detector*.log (Windows)
```

---

## Siguientes Pasos

1. 📖 Lee [README completo](README_COMPLETO.md) para configuración avanzada
2. 🔐 Cambia contraseña en `.env`
3. 💾 Configura base de datos PostgreSQL para persistencia
4. 📊 Crea alertas personalizadas modificando anomaly_detector.py

---

## 📚 Archivos Importantes

```
.env                    ← Configuración (cambiar contraseña aquí)
backend/app.py         ← API principal
frontend/src/App.js    ← Dashboard principal
requirements.txt       ← Dependencias Python
```

---

## ⏱️ Tiempos Típicos

| Acción | Tiempo |
|--------|--------|
| Instalación | 5-10 minutos |
| Inicio backend | 5-10 segundos |
| Inicio frontend | 20-30 segundos |
| Primera captura | Al instante |
| Detección de anomalías | 30-60 segundos |

---

## 🆘 ¿Todavía hay problemas?

1. Verifica tu versión de Python: `python --version` (debe ser 3.8+)
2. Verifica Node.js: `node --version` (debe ser 14+)
3. Revisa logs en carpeta `logs/`
4. Consulta documentación completa en README_COMPLETO.md
5. Crea un issue en GitHub con el error

---

## 💡 Pro Tips

✨ **Tip 1**: Abre 3 terminales (1 backend, 1 frontend, 1 para comandos)
✨ **Tip 2**: Usa Firefox DevTools (F12) para ver tráfico API
✨ **Tip 3**: Captura tráfico durante 2-3 minutos para mejores resultados
✨ **Tip 4**: Las anomalías tienen mejor score con >50 paquetes

---

¡Ahora ya estás listo para detectar anomalías de tráfico! 🎯
