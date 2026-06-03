## Lab 12

### Uruchomienie

polecenie: `docker compose up -d`

![](screenshots/1.png)

---

### Weryfikacja działania aplikacji

polecenie: `docker compose ps`

![](screenshots/2.png)

---

polecenie: `docker network ls`

![](screenshots/3.png)

---

polecenie: `docker inspect lab12_front | jq '.[].Containers'`

![](screenshots/4.png)

---

polecenie: `docker inspect lab12_back | jq '.[].Containers'`

![](screenshots/5.png)

---

### Test działania strony PHP

przeglądarka:

![](screenshots/6.png)

---

### Test phpMyAdmin

przeglądarka:

![](screenshots/7.png)
![](screenshots/8.png)

Panel phpMyAdmin dostępny pod `http://localhost:6001` 
Logowanie: użytkownik `root`, hasło `rootpassword`

---

### Utworzenie testowej bazy danych przez GUI phpMyAdmin

wynik w GUI:

![](screenshots/9.png)

---

wynik w CLI:

polecenie: `docker exec lab12_mysql mysql -uroot -prootpassword -e "SHOW DATABASES;"`

![](screenshots/10.png)

---

### Zatrzymanie i usunięcie

polecenie: `docker compose down`

![](screenshots/11.png)
