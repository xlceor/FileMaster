# FileMaster Licensing Architecture

## Concepto: Lifetime Licensing
FileMaster utiliza un modelo de licencia **"una vez para toda la vida"** (once-for-life). La licencia es válida indefinidamente para un único dispositivo.

## Ciclo de Vida del Licenciamiento

### 1. Activación (Primer Lanzamiento)
- El usuario ingresa su clave de licencia.
- El cliente recopila un **Hardware Fingerprint** (basado en múltiples identificadores de hardware para tolerancia a cambios menores).
- El cliente contacta a la API de validación enviando `{key, fingerprint}`.
- La API vincula permanentemente la licencia a ese `fingerprint` en la base de datos.
- Tras la validación exitosa, el cliente descarga un **lease local firmado y cifrado** que le permite ejecutarse indefinidamente sin necesidad de conexión posterior.

### 2. Actualizaciones (Validación Periódica)
- Cuando el usuario instale una actualización de la aplicación, el cliente realiza una verificación de seguridad silenciosa.
- **Proceso**:
    - El cliente genera un nuevo fingerprint actual del hardware.
    - El cliente envía este fingerprint a la API.
    - La API compara el nuevo fingerprint con el registrado originalmente para esa clave.
    - Si el fingerprint coincide (considerando el algoritmo de tolerancia), la API confirma que la máquina sigue siendo la autorizada.
    - Si el fingerprint ha cambiado drásticamente (ej: cambio de computadora), la API deniega la actualización y solicita un reset manual de la licencia por parte del soporte técnico.

## Arquitectura de Seguridad
- **Cliente**: Considerado entorno inseguro. No contiene claves privadas de cifrado; el lease se maneja mediante una estrategia de cifrado simétrico/asimétrico (según implementación final) donde el cliente solo conoce lo estrictamente necesario.
- **Backend (Vercel + Postgres)**: Es la única fuente de verdad. Almacena las licencias y realiza la vinculación única del fingerprint.
- **Hardware Fingerprinting**: Se utilizan 2 a 3 fuentes de datos (ej: UUID de placa base, ID de procesador, etc.) para asegurar que la máquina es la misma, incluso ante actualizaciones menores del sistema operativo o cambios de periféricos.

## Resumen de Flujo
1. **Instalación Inicial**: Check-in con API → Enlace Licencia-Máquina → Creación de Lease local.
2. **Uso Diario**: Verificación local del Lease (Offline).
3. **Actualización**: Check-in con API → Verificación de Fingerprint → Confirmación de validez continua.
