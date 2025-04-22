# Plan de Reorganización a Screaming Architecture

## Estructura Actual
Actualmente, la aplicación sigue una arquitectura por capas técnicas:
```
app/
  controllers/
  database/
  models/
  services/
  utils/
  views/
```

## Nueva Estructura (Screaming Architecture)
La nueva estructura organizará el código por dominios funcionales/casos de uso:

```
app/
  core/                      # Componentes centrales y compartidos
    __init__.py
    database/                # Conexión y esquema de base de datos
      connection.py
      schema.py
    utils/                   # Utilidades generales
      theme_manager.py
  
  authentication/            # Todo lo relacionado con autenticación
    __init__.py
    controllers/
      auth_controller.py
    models/
      user.py
    views/
      login_window.py
  
  expirations/               # Gestión de vencimientos
    __init__.py
    controllers/
      expiration_controller.py
    models/
      expiration.py
      alert.py
    views/
      dashboards/
        integral_dashboard.py
        sabana_dashboard.py
      forms/
        expiration_form.py
      lists/
        expiration_list.py
  
  notifications/             # Sistema de notificaciones
    __init__.py
    services/
      notification_service.py
  
  user_management/           # Gestión de usuarios
    __init__.py
    views/
      user_settings.py
```

## Plan de Migración

1. Crear la nueva estructura de directorios
2. Mover los archivos a sus nuevas ubicaciones
3. Actualizar las importaciones en todos los archivos
4. Asegurar que los patrones singleton sigan funcionando
5. Verificar que la aplicación funcione correctamente

## Pasos Detallados

### 1. Crear la nueva estructura de directorios
Crear todos los directorios necesarios según la nueva estructura.

### 2. Mover archivos
Mover cada archivo a su nueva ubicación manteniendo su contenido.

### 3. Actualizar importaciones
Actualizar todas las declaraciones de importación en cada archivo para reflejar las nuevas rutas.

### 4. Verificar patrones singleton
Asegurar que los patrones singleton (como en DatabaseConnection y AuthController) sigan funcionando correctamente.

### 5. Pruebas
Ejecutar la aplicación para verificar que todo funcione correctamente después de la reorganización.

## Beneficios de la Nueva Arquitectura

- **Claridad de propósito**: La estructura del código comunica claramente los casos de uso del sistema.
- **Cohesión**: Los componentes relacionados están agrupados juntos.
- **Mantenibilidad**: Facilita encontrar y modificar código relacionado con una funcionalidad específica.
- **Escalabilidad**: Permite agregar nuevas funcionalidades como nuevos módulos sin afectar a los existentes.