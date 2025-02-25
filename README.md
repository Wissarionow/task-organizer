# Spis treści
- [Uruchomienie](#uruchomienie)
- [Autoryzacja](#autoryzacja)
- [Zarządzanie użytkownikami](#zarządzanie-użytkownikami)
- [Zarządzanie zadaniami](#zarządzanie-zadaniami)
- [Historia zadań](#historia-zadań)
- [Filtrowanie zadań](#filtrowanie-zadań)

## Uruchomienie
#### 1.Budowanie projektu
```sh
docker-compose up --build
```
### 1.1 Jeżeli projekt budowany jest pierwszy raz, po uruchomieniu bazy danych należy wywołać
```sh
docker exec -it backend python manage.py makemigrations                                          
docker exec -it backend python manage.py migrate
```
### 2. Aplikacja jest uruchomiona
Dostęp do poglądowego frontendu 
```sh
http://0.0.0.0:8501
```

Dostęp do django
```
http://localhost:8000/
```

## Autoryzacja

### Pobranie tokena JWT (logowanie użytkownika)
```sh
curl -X POST "http://localhost:8000/api/token/" \
    -H "Content-Type: application/json" \
    -d '{"username": "example_user", "password": "example_password"}'
```
**Odpowiedź:**
```json
{
    "refresh": "TOKEN_REFRESH",
    "access": "TOKEN_ACCESS"
}
```

## Zarządzanie użytkownikami

### Rejestracja nowego użytkownika
```sh
curl -X POST "http://localhost:8000/api/user/register/" \
    -H "Content-Type: application/json" \
    -d '{"username": "new_user", "email": "new_user@example.com", "password": "securepassword"}'
```
**Odpowiedź:**
```json
{
    "message": "User created successfully",
    "access": "TOKEN_ACCESS",
    "refresh": "TOKEN_REFRESH",
    "user_id": 1,
    "name": "new_user"
}
```

### Pobranie listy użytkowników
```sh
curl -X GET "http://localhost:8000/api/user/all/"
```
**Odpowiedź:**
```json
[
    {"id": 1, "username": "new_user"},
    {"id": 2, "username": "another_user"}
]
```

## Zarządzanie zadaniami

### Dodanie nowego zadania
```sh
curl -X POST "http://localhost:8000/api/task/create/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer TOKEN_ACCESS" \
    -d '{"name": "New Task", "description": "Task details", "status": "NEW", "assigned_user": 1}'
```
**Odpowiedź:**
```json
{
    "id": 10,
    "name": "New Task",
    "description": "Task details",
    "status": "NEW",
    "assigned_user": 1
}
```

### Pobranie wszystkich zadań
```sh
curl -X GET "http://localhost:8000/api/task/all/"
```
**Odpowiedź:**
```json
[
    {"id": 10, "name": "New Task", "status": "NEW", "assigned_user": 1}
]
```

### Pobranie konkretnego zadania
```sh
curl -X GET "http://localhost:8000/api/task/10/"
```
**Odpowiedź:**
```json
{
    "id": 10,
    "name": "New Task",
    "description": "Task details",
    "status": "NEW",
    "assigned_user": 1
}
```

### Edycja zadania
```sh
curl -X POST "http://localhost:8000/api/task/edit/10/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer TOKEN_ACCESS" \
    -d '{"name": "Updated Task", "description": "Updated details", "status": "IN_PROGRESS", "assigned_user": 2}'
```
**Odpowiedź:**
```json
{
    "id": 10,
    "name": "Updated Task",
    "description": "Updated details",
    "status": "IN_PROGRESS",
    "assigned_user": 2
}
```

### Usunięcie zadania
```sh
curl -X DELETE "http://localhost:8000/api/task/delete/10/" \
    -H "Authorization: Bearer TOKEN_ACCESS"
```
**Odpowiedź:**
Status 204 No Content (brak treści)

## Historia zadań

### Pobranie historii zmian dla konkretnego zadania
```sh
curl -X GET "http://localhost:8000/api/task/history/10/"
```
**Odpowiedź:**
```json
[
    {
       "name": "Updated Task",
       "description": "Updated details",
       "assigned_user": "another_user",
       "created_at": "2024-02-15 10:00:00",
       "updated_at": "2024-02-16 11:00:00",
       "deleted_at": null
    }
]
```

## Filtrowanie zadań

### Filtrowanie według statusu, słowa kluczowego i przypisanego użytkownika
```sh
curl -X GET "http://localhost:8000/api/task/filter/?status=NEW&keyword=task&assigned_user=1"
```
**Odpowiedź:**
```json
[
    {
       "id": 10,
       "name": "New Task",
       "description": "Task details",
       "status": "NEW",
       "assigned_user": 1
    }
]
```

