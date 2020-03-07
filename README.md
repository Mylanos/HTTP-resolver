# IPK - Počítačové komunikace a sítě
##Projekt 1 - HTTP resolver doménových jmen
###Popis varianty:
První projekt očekává samostatné vypracování zadané úlohy z oblasti programování klient-server síťových aplikací. 
Předpokládá se použití základních knihoven a prostředků pro programování síťových soketů. 
Cílem projektu je implementace severu, který bude komunikovat protokolem HTTP a bude zajišťovat překlad doménových jmen. 
Pro překlad jmen bude server používat lokální resolver stanice na které běží - užijte přímo API, které poskytuje OS 
(například getnameinfo, getaddrinfo pro C/C++). 
###Stručný popis riešenia
####Makefile
Podporuje dva argumenty: 
```terminal
$ make build
```
Slúži len ako placeholder, zo zadania bol určený na preklad zdrojových súborov čož 
pri pythone nie je treba.
```terminal
$ make run PORT=1234
```
Spustí server a určí PORT na ktorom bude server bežať. PORT by malo byť
celočíselné číslo v rozmedzí uint_16.
####Funkcie
* main() -
Vytvorí objekt socketu, nastavuje možnosť okamžitého znovupoužitia socketu ktoré
boli používané na rovnakej adrese. Napojí socket na danú adresu, následne čaká na 
prichádzajúce spojenia a spracováva dáta prichádzajúce z daných spojení, ktoré 
posiela ďalej na spracovanie.

* parse_done() -
Rozdelí prichádzajúcu požiadavku na časti a rozdeľuje ich podľa podporovaných
metód.

* response_get() - Kontroluje formu požiadavky, z reťazca parsuje host_name a
typ požiadavky. Podľa typu požiadavky volá funkciu na preklad host_name.

* response_post() - Funguje podobne ako __response_get()__ len s tým rozdielom že
kontroluje prípadné prázdne riadky v prichádzajúcom súbore požiadavok. Všetky 
korektné požiadavky spracuje a odošle, v prípade že všetky požiadavky sú nesprávne
odosiela chybu

* resolve_host_name() - Prekladá názov hostiteľa do tvaru IP a kontroluje validitu daného hostiteľa.

* resolve_host_ip() - Prekladá host ip do tvaru názvu hostiteľa  a kontroluje validitu daného hostiteľa.

* ip_format() - Kontroluje či je daný argument vo formáte ipv4

* send_response() - Odosiela odpoveď na základe chyby alebo úspechu daných požiadavkov. 