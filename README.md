# Prueba Técnica: Data Governance Developer

## Introducción y Contexto del Problema 📝

¡Bienvenido/a al proceso de selección para **Governance Developer** en **DeAcero**!

Tu misión es demostrar tus habilidades en la implementación de un marco de gobierno de datos de extremo a extremo utilizando **Google Cloud Platform**. Para ello, trabajarás con el conocido dataset público de Stack Overflow, simulando que es la base de conocimiento interna de nuestra organización.

El objetivo es catalogar los activos clave, proteger la privacidad de los usuarios, asegurar la integridad de los datos, automatizar el proceso y demostrar cómo medirías y comunicarías el valor de estas iniciativas.

**Dataset Público a Utilizar**: `bigquery-public-data.stackoverflow`

---

## Objetivos Principales 🎯

- ✅ Catalogar activos clave de forma automatizada usando un archivo de configuración YAML
- ✅ Implementar una política de seguridad para proteger la información personal de los usuarios mediante el enmascaramiento de datos
- ✅ Implementar una política de calidad para asegurar la integridad de los datos
- ✅ Containerizar la solución con Docker y CI/CD
- ✅ Analizar y documentar conceptos clave de gobernanza como el linaje, las métricas de cumplimiento y la comunicación con stakeholders

---

## Tareas Específicas a Realizar

### **Parte 1: Configuración del Entorno en Dataplex**

1. Crea un **Dataplex Lake** en una región de tu elección (ej. `us-central1`)
2. Dentro de ese Lake, crea una **Dataplex Zone** de tipo **Curated Zone**
3. Asocia la Zone que creaste con el dataset completo de BigQuery: `bigquery-public-data.stackoverflow`
4. Asegúrate de que Dataplex descubra los assets (las tablas) correctamente

---

### **Parte 2: Catalogación Automatizada con YAML**

Crea un **archivo YAML** para definir los metadatos de las siguientes tres tablas: `users`, `posts_questions`, y `posts_answers`. 

Desarrolla un **script en Python** que lea este archivo y utilice la biblioteca cliente de Google Cloud para **Data Catalog** para actualizar las descripciones y adjuntar los tags a las tablas correspondientes en Dataplex.

#### **Información requerida en el yaml**


tables:
  - table_id: users
    description: "Tabla maestra de usuarios. Contiene información personal identificable (PII) y debe ser tratada como sensible."
    data_steward: "identity_management@deacero.com"
    tags:
      - "PII_Direct"
      - "User Data"
      - "Sensitive"

  - table_id: posts_questions
    description: "Contiene todas las preguntas creadas por los usuarios. El contenido es generado por el usuario."
    data_steward: "knowledge_management@deacero.com"
    tags:
      - "User Generated Content"
      - "Knowledge Base"

  - table_id: posts_answers
    description: "Contiene las respuestas a las preguntas. Vinculada a las preguntas y a los usuarios."
    data_steward: "knowledge_management@deacero.com"
    tags:
      - "User Generated Content"
      - "Transactional Data"


---

### **Parte 3: Configuración de Aspect Types en Dataplex** 📊

Crea un **Aspect Type personalizado** en Dataplex para enriquecer los metadatos de las tablas con información de gobierno de datos adicional.

#### **Definir Aspect Type:**
Usando las funcionalidades de Dataplex, crea un nuevo Aspect Type llamado `"data_governance_aspect"` con los siguientes campos:

- **Owner**: Campo de texto para especificar el propietario de los datos (`dataowner@deacero.com`)
- **Freshness**: Campo de enumeración para indicar la frecuencia de actualización (`daily`, `weekly`, `monthly`)

#### **Aplicar Aspect Type:**
Asigna este Aspect Type a las tres tablas principales (`users`, `posts_questions`, `posts_answers`) con los siguientes valores:
- **Owner**: `"dataowner@deacero.com"`
- **Freshness**: `"daily"`

#### **Verificación:**
Demuestra que los Aspect Types se han aplicado correctamente a las tablas en la UI de Dataplex.

---

### **Parte 4: Implementación de Seguridad y Enmascaramiento de Datos** 🔒

La tabla `users` contiene datos que deben ser protegidos. Tu tarea es implementar una **política de enmascaramiento**.

#### **Definir la Política:**
Usando las funcionalidades de "Policies", crea una nueva regla de política de datos.

#### **Configurar la Regla:**
- **Recurso**: Aplica la política a las columnas `display_name` y `location` de la tabla `bigquery-public-data.stackoverflow.users`
- **Roles/Principales**: Asigna la política a tu propia cuenta de usuario
- **Tipo de Enmascaramiento**: Configura la regla para que enmascare los datos usando un hash **SHA-256**

#### **Verificación:**
Ejecuta una consulta en BigQuery:
```sql
SELECT display_name, location 
FROM `bigquery-public-data.stackoverflow.users` 
LIMIT 10;
```
Demuestra que los valores aparecen enmascarados para tu usuario.

---

### **Parte 5: Implementación de una Regla de Calidad de Datos**

El equipo de negocio ha reportado que a veces se crean preguntas sin un autor asignado, lo cual es un **problema de integridad**. Tu tarea es crear una regla que monitoree este problema.

#### **Crear Regla de Calidad:**
Utilizando la funcionalidad de **Data Quality** dentro de Dataplex, crea una nueva regla para la tabla `posts_questions`.

#### **Configurar la Regla:**
La regla debe verificar que la columna `owner_user_id` **nunca sea nula**.

#### **Ejecutar y Verificar:**
Ejecuta el "job" de calidad de datos y proporciona un **screenshot del resultado**, mostrando el **porcentaje de cumplimiento** de la regla.

---

### **Parte 6: Dockerización y CI/CD Pipeline** 🐳

Para hacer la solución **reproducible y escalable**, implementa la containerización y automatización del proceso.



---

### **Parte 7: Análisis de Gobernanza (Conceptual)**

Esta parte **no requiere código adicional**, sino tu análisis como experto en gobernanza. En tu archivo `README.md`, crea una sección dedicada a este análisis y responde a lo siguiente:

#### **Análisis de Linaje:**
Explica la relación de linaje principal entre `users`, `posts_questions` y `posts_answers`. ¿Por qué un "Community Manager" se beneficiaría de poder visualizar este linaje? Escribe un párrafo breve (**máximo 100 palabras**) explicándole en términos sencillos qué es el linaje de datos y por qué es importante que él/ella sepa que la tabla `posts_questions` está conectada a la tabla `users`.

---

## Entregables 📬

Crea un **fork** de este repositorio que contenga:

### **Código y Configuración:**
- ✅ Todos los artefactos, scripts, documentos que creaste
- ✅ Archivo YAML de configuración de metadatos
- ✅ Scripts Python para cada parte de la implementación
- ✅ `Dockerfile` y `docker-compose.yml`
- ✅ Pipeline de CI/CD (github, gitlab o bitbucket)
- ✅ Archivo `requirements.txt`

### **Documentación:**
- ✅ **README.md** con:
  - Instrucciones claras de configuración y ejecución
  - Comandos Docker para ejecutar la solución
  - Plan de implementación para la Parte 6
  - Análisis de gobernanza completo de la Parte 7
  - Cualquier suposición que hayas hecho

### **Evidencias:**
- ✅ **Screenshots** de:
  - Resultado de la carga de metadatos en la UI de Dataplex
  - Resultado de la consulta en BigQuery que demuestra el enmascaramiento
  - Resultado del job de Calidad de Datos
  - Pipeline de CI/CD ejecutándose exitosamente
  - Contenedor Docker funcionando

### **Presentación:**
- ✅ **Documento final** para presentar tu trabajo (PowerPoint, PDF, etc.)

---


---

## 🚀 Recursos de Apoyo


### **Dataset de Prueba:**
- **Proyecto**: `bigquery-public-data`
- **Dataset**: `stackoverflow`
- **Tablas principales**: `users`, `posts_questions`, `posts_answers`



---

**¡Demuestra tu expertise en gobierno de datos y buena suerte!** 🎯

---

**© 2025 DeAcero Analytics Team**
