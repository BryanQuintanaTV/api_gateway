# Documentación de API Gateway

## Introducción
Este API Gateway actúa como intermediario entre el frontend y los microservicios de autenticación y gestión de productos/órdenes. Proporciona autenticación mediante JWT, gestión de usuarios y CRUD para productos y órdenes.

---

## Formato de Respuestas
Las respuestas se entregan en formato JSON con los siguientes códigos de estado:

| Código | Descripción                      |
|--------|----------------------------------|
| 200    | Solicitud exitosa                |
| 201    | Recurso creado                   |
| 400    | Solicitud inválida               |
| 401    | No autorizado o token inválido   |
| 404    | Recurso no encontrado            |
| 405    | Método de solicitud no permitido |

---

## Autenticación
La API utiliza JWT para proteger los endpoints. Los tokens deben enviarse en la cabecera Authorization con el formato:  
Authorization: Bearer *< token >*

---

## Endpoints

### Autenticación y Sesión

#### POST localhost:8000/api_gateway/api/v2/login/
*Descripción:* Genera tokens de acceso y refresco para autenticación.

| Parámetro  | Tipo   | Descripción            |
|------------|--------|------------------------|
| username   | string | Nombre de usuario      |
| password   | string | Contraseña del usuario |

*Respuesta:*
```json
{
  "access": "token",
  "refresh": "token"
}
```

#### POST localhost:8000/api_gateway/api/v2/refresh/
Descripción: Refresca el token de acceso utilizando el token de refresco.

| Parámetro  | Tipo   | Descripción              |
|------------|--------|--------------------------|
|  refresh   | string | Token de Refresco Valido |

Respuesta:

```json
{
  "access": "token"
}
```

---

### Gestión de Usuarios

> headers : {
> `Authorization` : 'Bearer *< token >*'
> }
<small>Todos los endpoints de usuario tienen que estar autentificados mediante un JWT válido</small>

#### GET localhost:8000/api_gateway/api/v2/users/

Descripción: Obtiene la lista de todos los usuarios.

| Parámetro        | Tipo   | Descripción                  |
|------------------|--------|--------------------------    |
|  Authorization   | string | JWT de acceso en la cabecera |



Respuesta:

```json
[
  { "id": 1, "username": "usuario1", "email": "email@usuario1com", "is_staff": true },
  { "id": 2, "username": "usuario2", "email": "email@usuario1com", "is_staff": false }
]
```

#### DELETE localhost:8000/api_gateway/api/v2/users/<int: id>/

Descripción: Obtiene la lista de todos los usuarios.

| Parámetro        | Tipo   | Descripción                  |
|------------------|--------|--------------------------    |
|  Authorization   | string | JWT de acceso en la cabecera |
|      id          |  int   |        Id del usuario        |


Respuesta `status 200`


#### PATCH localhost:8000/api_gateway/api/v2/users/<int: id>/

Descripción: Obtiene la lista de todos los usuarios.

| Parámetro        | Tipo   | Descripción                  |
|------------------|--------|--------------------------    |
|  Authorization   | string | JWT de acceso en la cabecera |
|      id          |  int   |        Id del usuario        |
| username, email, is_staff |  | Datos del usuario         |



---

### CRUD de Productos

> headers : {
> `Authorization` : 'Bearer *< token >*'
> }
<small>Todos los endpoints de usuario tienen que estar autentificados mediante un JWT válido</small>

#### GET localhost:8000/api_gateway/api/v2/rest/productos/
Descripción: Obtiene todos los productos almacenados.

|  Parámetro    |Tipo	|            Descripción          |
|---------------|-------|---------------------------------|
| Authorization |string	|  JWT de acceso en la cabecera   |

Respuesta:
```json
[
    {
        "id_product": 1,
        "name_product": "Agua Fresca",
        "price_product": 40.0,
        "image_product": "menu/aguasfrescas.webp"
    },
    ...
]

```

#### POST localhost:8000/api_gateway/api/v2/rest/productos/
Descripción: Crea un nuevo producto.

|   Parámetro   |  Tip o |          Descripción         |
|---------------|--------|------------------------------|
| Authorization | string | JWT de acceso en la cabecera |
|      body     |  JSON  |   Información del producto   |   

Ejemplo de cuerpo de solicitud:

```json
{
    "id_product": 1,
    "name_product": "Agua Fresca",
    "price_product": 21.0,
    "image_product": "menu/aguasfrescas.webp"
}
```

#### PATCH localhost:8000/api_gateway/api/v2/rest/productos/<int: id>/
Descripción: Edita un producto existente.

|   Parámetro   |  Tipo  |          Descripción         |
|---------------|--------|------------------------------|
| Authorization | string | JWT de acceso en la cabecera |
|      body     |  JSON  |   Información del producto   |   

Ejemplo de cuerpo de solicitud:

```json
{
    "id_product": 1,
    "name_product": "Aguas Frescas",
    "price_product": 101.0,
    "image_product": "menu/aguasfrescas.webp"
}
```

#### DELETE localhost:8000/api_gateway/api/v2/rest/productos/<int: id>/
Descripción: Elimina un producto existente.

|   Parámetro   |  Tipo  |          Descripción         |
|---------------|--------|------------------------------|
| Authorization | string | JWT de acceso en la cabecera |
|      body     |  JSON  |   Información del producto   |   

Ejemplo de cuerpo de solicitud: `Status: 200`

#### Códigos de respuesta específicos:

* `201`: Producto creado exitosamente.
* `400`: Datos inválidos.

---


### CRUD de Órdenes

> headers : {
> `Authorization` : 'Bearer *< token >*'
> }
<small>Todos los endpoints de usuario tienen que estar autentificados mediante un JWT válido</small>

#### GET localhost:8000/api_gateway/api/v2/rest/ordenes/
Descripción: Obtiene todas las órdenes existentes.

Ejemplo de respuesta
```json
[
    {
        "num_order": 1,
        "total_order": "160.00",
        "date_order": "2024-11-24",
        "id_user": 1,
        "order_products": [
            {
                "id_product": 1,
                "name_product": "Agua Fresca",
                "price_product": 40.0,
                "image_product": "menu/aguasfrescas.webp",
                "quantity": 2
            },
            {
                "id_product": 2,
                "name_product": "Banana Split",
                "price_product": 80.0,
                "image_product": "menu/bananasplit.webp",
                "quantity": 1
            }
        ]
    },
    ...
]
```

#### GET localhost:8000/api_gateway/api/v2/rest/ordenes/<id>/
Descripción: Obtiene una orden específica por ID.
|   Parámetro   |  Tipo  |          Descripción         |
|---------------|--------|------------------------------|
| Authorization | string | JWT de acceso en la cabecera |
|      ID       |  int   |   Información de la orden    |   

Ejemplo de respuesta:
```json
[
    {
        "num_order": 3,
        "total_order": "115.00",
        "date_order": "2024-12-03",
        "id_user": 3,
        "order_products": [
            {
                "id_product": 9,
                "name_product": "Nieve Vaso",
                "price_product": 45.0,
                "image_product": "menu/nievevasomedigran.webp",
                "quantity": 2
            },
            {
                "id_product": 8,
                "name_product": "Mangoneada",
                "price_product": 25.0,
                "image_product": "menu/mangoneadas.webp",
                "quantity": 1
            }
        ]
    }
]
```

#### PATCH localhost:8000/api_gateway/api/v2/rest/ordenes/<id>/
Descripción: Se Edita una orden existente mediante su ID

|   Parámetro   |  Tipo  |          Descripción                 |
|---------------|--------|--------------------------------------|
| Authorization | string | JWT de acceso en la cabecera         |
|      ID       |  int   |  identificador de la orden           |
|     body      |        |  Informacion de la orden a modificar | 

#### DELETE localhost:8000/api_gateway/api/v2/rest/ordenes/<id>/
Descripción: Se Elimina una orden existente mediante su ID

|   Parámetro   |  Tipo  |          Descripción                 |
|---------------|--------|--------------------------------------|
| Authorization | string | JWT de acceso en la cabecera         |
|      ID       |  int   |  identificador de la orden           |

Códigos de respuesta específicos:
* `404`: Orden no encontrada.


---

## Version 2
A la API_GATEWAY se le realizó la implementación de Caché con el uso de Redis

Funcionamiento:
Cuando un usuario realiza una solicitud **"GET"**, El API_GATEWAY compara si hay algun dato guardado dentro de caché, si no lo tiene guardado en Caché procederá a llamar al microservicio correspondiente y se guardará en Caché `cache.set('productos', response.json(), timeout=120)`.
Y cuando se realice alguno de los métodos que modifican los datos de la base de datos (**PATCH, PUT, DELETE**) se eliminará ese espacio en Caché para dejar que se guarde la información más actualizada.

```python
    if request.method == "GET":
        if cache.get('productos'):
            response = cache.get('productos')
            return JsonResponse(response, safe=False, status=200)
        else:
            response = requests.get(PRODUCT_REST_URL, headers=headers, params=request.GET)
            cache.set('productos', response.json(), timeout=120)
```
```python
 elif request.method == 'POST':
        response = requests.post(PRODUCT_REST_URL, headers=headers, json=json.loads(request.body.decode('utf-8')))
        cache.delete('productos')
    elif request.method == 'PATCH':
        response = requests.patch(PRODUCT_REST_URL, headers=headers, json=json.loads(request.body.decode('utf-8')))
        cache.delete('productos')
    elif request.method == 'DELETE':
        response = requests.delete(PRODUCT_REST_URL, headers=headers)
        cache.delete('productos')
    else:
        return JsonResponse({"error":"Método de solicitud inválido"}, status=405)
```
