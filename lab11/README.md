## Sprawozdanie
---
### Utworzenie dedykowanej sieci mostkowej
polecenie: 

`docker network create lab11net`

![](screenshots/1.png)

---
### Utworzenie oraz uruchomienie trzech kontenerów
polecenia (dla różnych kontenerów różni się tylko port oraz nazwa kontenera): 
```docker run -d --name web1 \
  --network lab11net \
  -p 8081:80 \
  -v $PWD/index.html:/usr/share/nginx/html/index.html:ro \
  -v $PWD/web1_logs:/var/log/nginx \
  nginx:latest
```
![](screenshots/2.png)

---
### Działanie
Przeglądarka

![](screenshots/3.png)
![](screenshots/4.png)

`curl`:

![](screenshots/5.png)

---
### Logi

![](screenshots/6.png)

Zawartość `web1_logs/access.log`:

![](screenshots/7.png)

Zawartość `web1_logs/error.log`:

![](screenshots/8.png)