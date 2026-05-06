def campo_estranho(campo_dado): #verifica se o campo tem caracters estranhas
    char_estranhas= ["@", "#", "!", "$", "%", "&", "*", "?", "~"]
    for char in campo_dado:
        if char in char_estranhas:
            return True

    return False

def is_leap(year):
    if(year%4 == 0):
        if(year%100 == 0):
            if(year%400 == 0):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

#timestamp format "2024-07-04 16:29:21.281898"
def timestamp_impossivel(timestamp):
    split_timestamp= timestamp.split(" ")
    if(len(split_timestamp) != 2):
        return True

    data= split_timestamp[0]
    horas= split_timestamp[1]

    #verificar data
    split_data= data.split("-")
    if(len(split_data) != 3): #ou tem valores negativos ou falta campos
        return True

    ano= int(split_data[0]) #VERIFICAR SE E ANO BISEXTO
    mes= int(split_data[1])
    dia= int(split_data[2])
    if(ano > 2026 or mes > 12 or mes == 0 or dia == 0):
        return True

    dias_31= (1, 3, 5, 7, 8, 10, 12)
    dias_30= (4, 6, 9, 11)
    if((mes in dias_31) and dia > 31):
        return True
    elif((mes in dias_30) and dia > 30):
        return True
    elif((is_leap(ano) == False) and dia > 28): #se for fevereiro
        return True
    elif((is_leap(ano) == True) and dia > 29): #se for fevereiro e um ano bissexto
        return True

    #verificar hora
    hora, min, seg= horas.split(":")
    hora= int(hora)
    min= int(min)
    seg= float(seg)
    if(hora > 24 or hora < 0 or min > 59 or min < 0 or seg < 0 or seg >= 60):
        return True

    #se tudo valido
    return False

def temp_anomalo(registo, player): #vai precisar da msg como parametro (vao todos)
    if(player != 4):
        return True, "Jogador Invalido"

    hora= registo["Hour"]
    temp= registo["Temperature"]
    if(campo_estranho(hora) or campo_estranho(str(temp))): #temp/hora inclui caraters estranhas?
        return True, "Carater Estranha Detetada"

    if(timestamp_impossivel(hora)): #data e hora possivel?
        return True, "Timestamp Invalido"

    if(temp > 100.0 or temp < -100.0): #valor temp e possivel?
        return True, "Valor Som Invalido"

    return False, ""

def sound_anomalo(registo, player):
    if(player != 4):
        return True, "Jogador Invalido"

    hora= registo["Hour"]
    som= registo["Sound"]
    if(campo_estranho(hora) or campo_estranho(str(som))): #som/hora inclui caraters estranhas?
        return True, "Carater Estranha Detetada"

    if(timestamp_impossivel(hora)): #data e hora possivel?
        return True, "Timestamp Invalido"

    if(som > 150.0 or som < 0): #som impossivel?
        return True, "Valor Som Invalido"

    return False, ""

def move_anomalo(registo, player, num_marsamis, origem_anterior, num_salas):
    if(player != 4):
        return True, "Jogador Invalido"

    for chave in registo: #algum campo inclui caraters estranhas?
        if(campo_estranho(str(registo[chave]))):
            return True, "Carater Estranha Detetada"

    status= registo["Status"]
    if(status > 2 or status < 0): #status valida?
        return True, "Status Invalida"

    marsami_num= registo["Marsami"]
    if(marsami_num < 1 or marsami_num > num_marsamis): #numero de marsami valido?
        return True, "Marsami Invalido"

    origem= registo["RoomOrigin"]
    if(origem != origem_anterior): #sala de origem certa?
        return True, "Room Origin Invalido"

    destino= registo["RoomDestiny"]
    if(destino < 1 or destino > num_salas): #sala destino existe?
        return True, "Room Destiny Invalido"

    #ler cloud
    if(False): #sala de origem e destino conectadas?
        return True, "Corredor Nao Existe"

    return False, ""

def temp_outlier(temp_atual, threshold, last_three):
    if(len(last_three) == 3):
        media= (last_three[0]+last_three[1]+last_three[2])/3
    elif(len(last_three) == 2): #se for o 3o a ser inserido
        media= (last_three[0]+last_three[1])/2
    elif(len(last_three) == 1): #se for o 2o a ser inserido
        media= last_three[0]
    else: #se for o 1o a ser inserido
        return False

    variacao= abs(temp_atual - media)
    if(variacao < threshold): #comparar com threshold
        return False
    else:
        return True

def sound_outlier(sound_atual, threshold, last_three):
    if(len(last_three) == 3):
        media= (last_three[0]+last_three[1]+last_three[2])/3
    elif(len(last_three) == 2): #se for o 3o a ser inserido
        media= (last_three[0]+last_three[1])/2
    elif(len(last_three) == 1): #se for o 2o a ser inserido
        media= last_three[0]
    else: #se for o 1o a ser inserido
        return False

    variacao= abs(sound_atual - media)
    if(variacao < threshold): #comparar com threshold
        return False
    else:
        return True