from bs4 import BeautifulSoup
import json
from datetime import datetime
from difflib import SequenceMatcher

# nome dos arquivos com o html
jogadores = ['messi', 'cr7', 'benzema', 'mbappe']

for jogador in jogadores:
    # arquivo html contendo as posições x, y e o id das batidas
    htmlfile = f'./html/{jogador}.html'
    # arquivo html contendo informações sobre a partida
    htmlfile1 = f'./html/{jogador}_1.html'
    # arquivo html contendo mais informações sobre o penalti
    htmlfile2 = f'./html/{jogador}_2.html'

    # le arquivo contendo as posições x, y e o id das batidas
    with open(htmlfile, encoding="UTF-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    batidas = list()

    # coleta batidas convertidas/batidas no total (valor1/valor2)
    div = soup.find('div', class_='sc-hLBbgP sc-eDvSVe dSBxWa bbcOkn')
    span = div.find_all('span')[1]
    valor = span.text
    valor1, valor2 = valor.split('/')
    
    # visita as tags 'svg' e 'circle' e coleta x, y e id
    # coloca em um dicionário e armazena na lista
    for tag in soup.find_all(["svg", "circle"]):
        if tag.has_attr("class") and any("virtual-ball" in c for c in tag["class"]):
            ball_num = int([c.split("virtual-ball")[1] for c in tag["class"] if "virtual-ball" in c][0])

            if tag.name == "svg":
                x = float(tag.get("x", "0"))
                y = float(tag.get("y", "0"))

                if (x == 0 and y == 0) or (x == 16 and y == 16):
                    pass
                else:
                    batidas.append({"id": ball_num,
                                    "campeonato": None,
                                    "partida": None,
                                    "placar": None,
                                    "data": None,
                                    "minutagem": None,
                                    "goleiro": None,
                                    "x": x,
                                    "y": y,
                                    "resultado": "acertou"})
            elif tag.name == "circle":
                cx = float(tag.get("cx", "0"))
                cy = float(tag.get("cy", "0"))

                if (cx == 8 and cy == 8):
                    pass
                else:
                    batidas.append({"id": ball_num,
                                    "campeonato": None,
                                    "partida": None,
                                    "placar": None,
                                    "data": None,
                                    "minutagem": None,
                                    "goleiro": None,
                                    "x": cx,
                                    "y": cy,
                                    "resultado": "perdeu"})
    
    # le arquivo contendo informações sobre a partida
    with open(htmlfile1, encoding="windows-1252") as f:
        soup = BeautifulSoup(f, "html.parser")

    # coleta nas tags 'div':
    # alt = nome do time
    # texto nas divs = resultado da partida no formato 'x-y'
    # texto nas spans = data em que foi realizada a partida
    i = 0
    for div in soup.find_all("div", class_="sc-4ce7d8a1-2 gcTWVx"):
        text_div = div.find("div", class_="sc-hLBbgP sc-eDvSVe cSnyOz fRddxb")
        text_values = text_div.get_text().strip().split("-")
        date = div.find("span", class_="sc-bqWxrE gTHHAa").get_text().strip()

        imgs = text_div.find_all("img")
        alt_values = []
        for img in imgs:
            alt_value = img.get("alt")
            if alt_value is not None:
                alt_values.append(alt_value)
        
        new_dict = dict()
        
        # junta as informações da partida em que ocorreu o penalti
        # com as posições e id da batida
        new_dict = batidas[i]
        new_dict['partida'] = f'{alt_values[0]} x {alt_values[1]}'
        new_dict['placar'] = f'{text_values[0]}-{text_values[1]}'
        new_dict['data'] = f'{date}'
        
        batidas[i] = new_dict
        i += 1
    
    with open(htmlfile2, encoding="windows-1252", errors="ignore") as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    important_values = list()
    lista_siglas = ['FC', 'AC', 'AS', 'SS', 'SC', 'EC', 'CR', 'CA', 'CD', 'CF', 'OGC']
    for tr in soup.find_all("tr"):
        td_values = [td.text.replace('\xa0','') for td in tr.find_all('td')]
        
        titles = list()
        for img in tr.find_all('img'):
            title = img.get('alt')
            titles.append(title)
            
        if td_values[1] != 'Jogos amistosos':
            time1 = titles[2]
            time2 = titles[3]
            if " " in titles[2]:
                prefixo, nome_time = titles[2].split(maxsplit=1)
                if prefixo in lista_siglas:
                    time1 = nome_time
                else:
                    time1 = titles[2]
            
            if " " in titles[3]:
                prefixo1, nome_time1 = titles[3].split(maxsplit=1)
                if prefixo1 in lista_siglas:
                    time2 = nome_time1
                else:
                    time1 = titles[2]
                
            data_objeto = datetime.strptime(td_values[3], "%d/%m/%Y")
            data_formatada = data_objeto.strftime("%d/%m/%y")
            important_values.append({'campeonato': td_values[1], 'data': data_formatada, 'minutagem do penalti': td_values[7].replace('\'',''), 'goleiro': td_values[9], 'partida': f'{time1} x {time2}'})

    for i, item1 in enumerate(batidas):
        for j, item2 in enumerate(important_values):
            s = SequenceMatcher(None, item1.get("partida", ""), item2.get("partida", ""))
            s = s.ratio()
            if i != j and s >= 0.75:
                item1['campeonato'] = item2['campeonato']
                item1['minutagem'] = item2['minutagem do penalti']
                item1['goleiro'] = item2['goleiro']
    
    # armazena algumas informações sobre o jogador ao final da lista
    batidas.append({"jogador": f"{jogador}", "total de batidas": int(valor2), "batidas convertidas": int(valor1), "batidas perdidas": int(valor2)-int(valor1)})
        
    # transforma em json e guarda no arquivo {jogador}.json
    json_file = f'./json_data/{jogador}.json'
    with open(json_file, 'w', encoding='windows-1252') as f1:
        json.dump(batidas, f1, indent=4, ensure_ascii=False)
        
    print(f'{jogador} OK')