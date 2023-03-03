from bs4 import BeautifulSoup
import json

# nome dos arquivos com o html
jogadores = ['messi', 'cr7', 'benzema', 'mbappe']

for jogador in jogadores:
    # arquivo html contendo as posições x, y e o id das batidas
    htmlfile = f'{jogador}.html'
    # arquivo html contendo informações sobre a partida
    htmlfile1 = f'{jogador}_1.html'

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
                    batidas.append({"id": ball_num, "partida": None, "placar": None, "data": None, "x": x, "y": y, "resultado": "acertou"})
            elif tag.name == "circle":
                cx = float(tag.get("cx", "0"))
                cy = float(tag.get("cy", "0"))

                if (cx == 8 and cy == 8):
                    pass
                else:
                    batidas.append({"id": ball_num, "partida": None, "placar": None, "data": None, "x": cx, "y": cy, "resultado": "perdeu"})
    
    # le arquivo contendo informações sobre a partida
    with open(htmlfile1, encoding="windows-1252") as f:
        soup = BeautifulSoup(f, "html.parser")

    # procura nas tags 'div' pela classe abaixo
    divs = soup.find_all("div", class_="sc-4ce7d8a1-2 gcTWVx")

    # coleta nas tags 'div':
    # alt = nome do time
    # texto nas divs = resultado da partida no formato 'x-y'
    # texto nas spans = data em que foi realizada a partida
    i = 0
    for div in divs:
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
    
    # armazena algumas informações sobre o jogador ao final da lista
    batidas.append({"jogador": f"{jogador}", "total de batidas": int(valor2), "batidas convertidas": int(valor1), "batidas perdidas": int(valor2)-int(valor1)})

    # transforma em json e guarda no arquivo {jogador}.json
    json_file = f'{jogador}.json'
    with open(json_file, 'w', encoding='windows-1252') as f1:
        json.dump(batidas, f1, indent=4, ensure_ascii=False)
        
    print(f'{jogador} OK')