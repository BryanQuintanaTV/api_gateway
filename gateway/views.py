import requests
from django.http import JsonResponse,HttpResponse
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json

# Every view has @csrf_exempt tag
# The objective is that our API Gateway ignores the use of the session token (CSRF)
# This is required when we obtain data from external resources
#
# It is important to emphasize that this is not secure
# In production environment, it recommends to add a Middlewares of tokens auth CSRF.
load_dotenv()
from django.views.decorators.csrf import csrf_exempt
# Endpoints collections that our API Gateways are going to consume
AUTH_URL = os.getenv('AUTH_URL')
REFRESH_URL = os.getenv('REFRESH_URL')
VALIDATE_URL = os.getenv('VALIDATE_URL')
USERS_REST_URL = os.getenv('USERS_REST_URL')
ORDER_REST_URL = os.getenv('ORDER_REST_URL')
PRODUCT_REST_URL = os.getenv('PRODUCT_REST_URL')

# Login's view
@csrf_exempt
def login(request):
    # Se realiza una simple solicitud POST con los datos recibidos atraves del API Gateway
    # Se entrega la respuesta recibida del endpoint original
    if request.method == "POST":
        response = requests.post(AUTH_URL, data=request.POST)
        return JsonResponse(response.json(), status=response.status_code)

    # Si el método solicitado no es POST, se manda un error
    return JsonResponse({"error":"Método de solicitud inválido"}, status=405)

# Vista de refrescado de access token
# Esta vista se debe utilizar para refrescar el token de acceso en el frontend.
@csrf_exempt
def refresh_token(request):
    # Se realiza una simple solicitud POST con los datos recibidos a través de API Gateway
    # Se entrega la respuesta recibida del endpoint original
    if request.method == "POST":
        response = requests.post(REFRESH_URL, data=request.POST)
        return JsonResponse(response.json(), status=response.status_code)

    # Si el método solicitado no es POST, se manda un error
    return JsonResponse({"error":"Método de solicitud inválido"})

# Vista CRUD de usuarios
# Esta vista funciona a través de una implementación proxy
# La diferencia clave entre esta vista y las anteriores es el requisito del JWT
@csrf_exempt
def users_proxy(request):
    # Se obtienen los datos dentro de la cabecera Authorization
    token = request.headers.get('Authorization')

    # Se verifica que el token se encuentre dentro de la cabecera Authorization:
    # Bearer {token}
    if not token:
        return JsonResponse({"error":"No se ha recibido ningún token"}, status=401)

    # Se manda la solicitud al Micro Servicio REST de usuarios con los siguientes datos.
    headers = {
        'Authorization': token,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }
    url = f"{USERS_REST_URL}{request.path[len('/api_gateway/api/v2/users/'):]}"
    print("URL",url)
    print("headers",headers)
    print("BODY",request.body.decode("utf-8"))

    # Se verifican los métodos aceptados de la solicitud
    if request.method == 'GET':
        response = requests.get(url, headers=headers, params=request.GET)
    elif request.method == 'POST':
        response = requests.post(url, headers=headers, json=json.loads(request.body.decode('utf-8')))
    elif request.method == 'PATCH':
        response = requests.patch(url, headers=headers, json=request.body.decode('utf-8'))
    elif request.method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        return JsonResponse({"error":"Método de solicitud inválido"}, status=405)

    # Se manda la respuesta obtenida del micro servicio con una verificación de respuestas
    # Sin contenido (O contenido inválido).
    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except ValueError:
        return HttpResponse(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))

# Vista CRUD del micro servicio REST_Productos
# Esta vista funciona a través de una implementación proxy.
# La diferencia clave entre esta vista y la anterior, es el uso del micro servicio de verificación JWT.
@csrf_exempt
def rest_productos_proxy(request):
    # Se obtienen los datos dentro de la cabecera Authorization
    token = request.headers.get('Authorization')
    print("AUTH", token)

    # Se verifica que el token se encuentre dentro de la cabecera Authorization:
    #   Bearer {token}
    if not token or not token.startswith("Bearer "):
        return JsonResponse({"error":"No se ha recibido ningún token"}, status=401)

    # Se utiliza el micro servicio de validación JWT
    access_token = token.split(" ")[1]
    validation_response = requests.post(VALIDATE_URL, data={"token": access_token})

    # Si la respuesta del micro servicio es inválida, se devuelve un error
    if validation_response.status_code != 200:
        return JsonResponse({"error":"Token inválido"}, status=401)

    # Se manda la solicitud al micro servicio REST de usuarios con los siguientes datos:
    headers = {
        'Authorization': token,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }

    # Se verifican los métodos aceptados de la solicitud
    if request.method == "GET":
        if cache.get('productos'):
            print("I HAVE IT ON CACHE")
            response = cache.get('productos')
            return JsonResponse(response, safe=False, status=200)
        else:
            response = requests.get(PRODUCT_REST_URL, headers=headers, params=request.GET)
            print("I DO NOT HAVE IT ON CACHE")
            cache.set('productos', response.json(), timeout=120)
    elif request.method == 'POST':
        response = requests.post(PRODUCT_REST_URL, headers=headers, json=request.body)
        cache.delete('productos')
    elif request.method == 'PATCH':
        response = requests.patch(PRODUCT_REST_URL, headers=headers, json=request.body)
        cache.delete('productos')
    elif request.method == 'DELETE':
        response = requests.delete(PRODUCT_REST_URL, headers=headers)
        cache.delete('productos')
    else:
        return JsonResponse({"error":"Método de solicitud inválido"}, status=405)

    # Se manda la respuesta obtenida del Micro Servicio con una verificación de respuestas
    # sin contenido (o contenido inválido).
    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except ValueError:
        return HttpResponse(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))


# Vista CRUD del micro servicio REST_Productos con ID
# Esta vista funciona a través de una implementación proxy.
# La diferencia clave entre esta vista y la anterior, es el uso del micro servicio de verificación JWT.
@csrf_exempt
def rest_productos_proxy_by_id(request, id):
    # Se obtienen los datos dentro de la cabecera Authorization
    token = request.headers.get('Authorization')
    API_PATH_ID = f"{PRODUCT_REST_URL}{id}/"
    print("PATH,", API_PATH_ID)
    print("AUTH", token)

    # Se verifica que el token se encuentre dentro de la cabecera Authorization:
    #   Bearer {token}
    if not token or not token.startswith("Bearer "):
        return JsonResponse({"error":"No se ha recibido ningún token"}, status=401)

    # Se utiliza el micro servicio de validación JWT
    access_token = token.split(" ")[1]
    validation_response = requests.post(VALIDATE_URL, data={"token": access_token})

    # Si la respuesta del micro servicio es inválida, se devuelve un error
    if validation_response.status_code != 200:
        return JsonResponse({"error":"Token inválido"}, status=401)

    # Se manda la solicitud al micro servicio REST de usuarios con los siguientes datos:
    headers = {
        'Authorization': token,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }


    # Se verifican los métodos aceptados de la solicitud
    if request.method == "GET":
        if cache.get(f"producto{id}"):
            print("I HAVE IT ON CACHE")
            response = cache.get(f"producto{id}")
            return JsonResponse(response, safe=False, status=200)
        else:
            response = requests.get(API_PATH_ID, headers=headers, params=request.GET)
            print("I DO NOT HAVE IT ON CACHE")
            cache.set(f"producto{id}", response.json(), timeout=120)
    elif request.method == 'POST':
        response = requests.post(API_PATH_ID, headers=headers, json=request.body)
        cache.delete(f"producto{id}")
    elif request.method == 'PATCH':
        response = requests.patch(API_PATH_ID, headers=headers, json=json.loads(request.body.decode('utf-8')))
        cache.delete(f"producto{id}")
    elif request.method == 'DELETE':
        response = requests.delete(API_PATH_ID, headers=headers)
        cache.delete(f"producto{id}")
    else:
        return JsonResponse({"error":"Método de solicitud inválido"}, status=405)

    # Se manda la respuesta obtenida del Micro Servicio con una verificación de respuestas
    # sin contenido (o contenido inválido).
    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except ValueError:
        return HttpResponse(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))



# Vista CRUD del micro servicio REST_Ordenes
# Esta vista funciona a través de una implementación proxy.
# La diferencia clave entre esta vista y la anterior, es el uso del micro servicio de verificación JWT.
@csrf_exempt
def rest_ordenes_proxy(request):
    # Se obtienen los datos dentro de la cabecera Authorization
    token = request.headers.get('Authorization')

    # Se verifica que el token se encuentre dentro de la cabecera Authorization:
    #   Bearer {token}
    if not token or not token.startswith("Bearer "):
        return JsonResponse({"error": "No se ha recibido ningún token"}, status=401)

    # Se utiliza el micro servicio de validación JWT
    access_token = token.split(" ")[1]
    validation_response = requests.post(VALIDATE_URL, data={"token": access_token})

    # Si la respuesta del micro servicio es inválida, se devuelve un error
    if validation_response.status_code != 200:
        return JsonResponse({"error": "Token inválido"}, status=401)

    # Se manda la solicitud al micro servicio REST de usuarios con los siguientes datos:
    headers = {
        'Authorization': token,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }

    # Se verifican los métodos aceptados de la solicitud
    if request.method == "GET":
        if cache.get('ordenes'):
            print("I HAVE IT ON CACHE")
            response = cache.get('ordenes')
            return JsonResponse(response, safe=False, status=200)
        else:
            response = requests.get(ORDER_REST_URL, headers=headers, params=request.GET)
    elif request.method == 'POST':
        response = requests.post(ORDER_REST_URL, headers=headers, json=json.loads(request.body.decode("UTF-8")))
        cache.delete('ordenes')
    elif request.method == 'PATCH':
        response = requests.patch(ORDER_REST_URL, headers=headers, json=request.body)
        cache.delete('ordenes')
    elif request.method == 'DELETE':
        response = requests.delete(ORDER_REST_URL, headers=headers)
        cache.delete('ordenes')
    else:
        return JsonResponse({"error": "Método de solicitud inválido"}, status=405)

    # Se manda la respuesta obtenida del Micro Servicio con una verificación de respuestas
    # sin contenido (o contenido inválido).
    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except ValueError:
        return HttpResponse(response.content, status=response.status_code,
                            content_type=response.headers.get('Content-Type'))


# Vista CRUD del micro servicio REST_Ordenes por id
# Esta vista funciona a través de una implementación proxy.
# La diferencia clave entre esta vista y la anterior, es el uso del micro servicio de verificación JWT.
@csrf_exempt
def rest_ordenes_by_id_proxy(request, id):
    # Se obtienen los datos dentro de la cabecera Authorization
    token = request.headers.get('Authorization')
    API_PATH_ID = f"{ORDER_REST_URL}{id}/"

    # Se verifica que el token se encuentre dentro de la cabecera Authorization:
    #   Bearer {token}
    if not token or not token.startswith("Bearer "):
        return JsonResponse({"error": "No se ha recibido ningún token"}, status=401)

    # Se utiliza el micro servicio de validación JWT
    access_token = token.split(" ")[1]
    validation_response = requests.post(VALIDATE_URL, data={"token": access_token})

    # Si la respuesta del micro servicio es inválida, se devuelve un error
    if validation_response.status_code != 200:
        return JsonResponse({"error": "Token inválido"}, status=401)

    # Se manda la solicitud al micro servicio REST de usuarios con los siguientes datos:
    headers = {
        'Authorization': token,
        'Content-Type': request.headers.get('Content-Type', 'application/json'),
    }

    # Se verifican los métodos aceptados de la solicitud
    if request.method == "GET":
        if cache.get(f"orden{id}"):
            print("I HAVE IT ON CACHE")
            response = cache.get(f"orden{id}")
            return JsonResponse(response, safe=False, status=200)
        else:
            response = requests.get(API_PATH_ID, headers=headers, params=request.GET)
    elif request.method == 'POST':
        response = requests.post(API_PATH_ID, headers=headers, json=request.body)
        cache.delete(f"orden{id}")
    elif request.method == 'PATCH':
        response = requests.patch(API_PATH_ID, headers=headers, json=request.body)
        cache.delete(f"orden{id}")
    elif request.method == 'DELETE':
        response = requests.delete(API_PATH_ID, headers=headers)
        cache.delete(f"orden{id}")
    else:
        return JsonResponse({"error": "Método de solicitud inválido"}, status=405)

    # Se manda la respuesta obtenida del Micro Servicio con una verificación de respuestas
    # sin contenido (o contenido inválido).
    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except ValueError:
        return HttpResponse(response.content, status=response.status_code,
                            content_type=response.headers.get('Content-Type'))