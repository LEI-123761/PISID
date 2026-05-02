def campo_estranho(campo_dado): #verifica se o campo tem caracters estranhas
    char_estranhas= ["@", "#", "!", "$", "%", "&", "*", "?", "~"]
    for char in campo_dado:
        if char in char_estranhas:
            return True

    return False

#timestamp format "2024-07-04 16:29:21.281898"
def timestamp_impossivel(timestamp):
    data, horas= timestamp.split(" ")

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
    elif(dia > 28): #se for fevereiro
        return True

    #verificar hora
    hora, min, seg= horas.split(":")
    hora= int(hora)
    min= int(min)
    seg= float(seg)
    if(hora > 24 or hora < 0 or min > 59 or min < 0 or seg < 0 or seg > 59):
        return True

    #se tudo valido
    return False

def temp_anomalo(registo, player): #vai precisar da msg como parametro (vao todos)
    if(player != 4):
        return True

    hora= registo["Hour"]
    temp= registo["Temperature"]
    if(campo_estranho(hora) or campo_estranho(str(temp))): #temp/hora inclui caraters estranhas?
        return True

    if(timestamp_impossivel(hora)): #data e hora possivel?
        return True

    if(temp > 100.0 or temp < -100.0): #valor temp e possivel?
        return True

    return False

def sound_anomalo(registo, player):
    if(player != 4):
        return True

    hora= registo["Hour"]
    som= registo["Sound"]
    if(campo_estranho(hora) or campo_estranho(str(som))): #som/hora inclui caraters estranhas?
        return True

    if(timestamp_impossivel(hora)): #data e hora possivel?
        return True

    if(som > 150.0 or som < 0): #som impossivel?
        return True

    return False

def move_anomalo(registo, player, origem_anterior):
    if(player != 4):
        return True

    for chave in registo: #algum campo inclui caraters estranhas?
        if(campo_estranho(str(registo[chave]))):
            return True

    status= registo["Status"]
    if(status > 2 or status < 0): #status valida?
        return True

    num_marsamis= 5 #get num de marsamis da cloud?
    marsami_num= registo["Marsami"]
    if(marsami_num < 1 or marsami_num > num_marsamis): #numero de marsami valido?
        return True

    origem= registo["RoomOrigin"]
    if(origem != origem_anterior[marsami_num-1]): #sala de origem certa?
        return True

    num_salas= 0 #get from cloud
    destino= registo["RoomDestiny"]
    if(destino < 1 or destino > num_salas): #sala destino existe?
        return True

    #ler cloud
    if(False): #sala de origem e destino conectadas?
        return True

    return False

def temp_outlier():
    #calcular media
    #calculo com valor atual
    #comparar com threshold
    return False

def sound_outlier():
    #calcular media
    #calculo com valor atual
    #comparar com threshold
    return False