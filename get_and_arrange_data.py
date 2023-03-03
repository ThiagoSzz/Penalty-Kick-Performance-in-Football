from bs4 import BeautifulSoup
import os

'''
TODO:
1. arrumar erro que ocorre ao unir os 2 datasets quando encontra uma batida perdida
2. converter para json
3. fazer para todos os jogadores
'''

# nome dos arquivos com o html
jogadores = ['messi', 'cr7', 'benzema', 'mbappe']

for jogador in jogadores[:1]:
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

    # visita as tags 'svg' e coleta x, y e id
    # coloca em um dicionário e armazena na lista
    i = 0
    for svg in soup.find_all("svg"):
        x = float(svg.get("x", "0"))
        y = float(svg.get("y", "0"))

        if (x == 0 and y == 0) or (x == 16 and y == 16):
            pass
        else:
            if i <= int(valor1) and i != 0:
                new_dict = dict()
                new_dict['x'] = x
                new_dict['y'] = y
                new_dict['id'] = ''
                classe = svg.get("class")[2]
                new_dict['id'] = int(classe.split("actual-ball")[1])
                new_dict['resultado'] = 'acertou'

                batidas.append(new_dict)

            i += 1

    # faz o mesmo, porém nas tags 'circle'
    i = 0
    for circle in soup.find_all("circle"):
        cx = float(circle.get("cx", "0"))
        cy = float(circle.get("cy", "0"))

        if cx == 8 and cy == 8:
            pass
        else:        
            if i <= int(valor2)-int(valor1)+4 and i >= 5:
                new_dict = dict()
                new_dict['x'] = cx
                new_dict['y'] = cy
                new_dict['id'] = ''
                classe = circle.get("class")[2]
                new_dict['id'] = int(classe.split("actual-ball")[1])
                new_dict['resultado'] = 'perdeu'

                batidas.append(new_dict)

            i += 1

    # ordena baseado no id coletado
    sorted_list = sorted(batidas, key=lambda x: int(x['id']), reverse=True)
    
    # move valores 'inusitados' ao final da lista
    bigger = list()
    for i in range(len(sorted_list)):
        if int(sorted_list[i]['id']) > 17000:
            bigger.append(sorted_list[i])
            
    bigger = sorted(bigger, key=lambda x: int(x['id']))    
    for i in bigger:
        sorted_list.append(i)
        sorted_list.pop(0)
        
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
    
    # imprime as informações mais relevantes  
    print(jogador)
    for i in sorted_list:
        print(f'partida {i["partida"]}: {i["placar"]}')
        print(f'penalti {i["id"]}: {i["resultado"]}')
        print(f'x: {i["x"]}, y: {i["y"]}')
        print()
