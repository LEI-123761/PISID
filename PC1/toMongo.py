import paho.mqtt.client as mqtt

####################Fns####################
def receiveMsg(tipoMsg, msgRcv): #nao sei se os parametros estao bem feitos? Como e q se passa?
    if(tipoMsg == topics[0]):
        novaLinha= "db.soundsReceived.insertone("+msgRcv+")"
    elif(tipoMsg == topics[1]):
        novaLinha= "db.tempsReceived.insertone("+msgRcv+")"
    elif(tipoMsg == topics[2]):
        novaLinha= "db.movesReceived.insertone("+msgRcv+")"
    else:
        novaLinha= "db.actsReceived.insertone("+msgRcv+")"

    return novaLinha #e para fazer return?

####################Main Code####################
numeroJogador= 4 #valor temp, fazer isto um argumento
topics = ["pisid_mazesound_"+numeroJogador, "pisid_mazetemp_"+numeroJogador, "pisid_mazemov_"+numeroJogador]

#criar cliente para receber dados dos broker
c= mqtt.Client("toMongo")
c.on_message= receiveMsg #indica o q fazer quando recebe msgs

#conectar ao broker
c.connect("www.hivemq.com", 1883) #fazer estes argumentos tb (como o mazerun, assim se mudamos o mazerun tb podemos mudar este)
c.loop_start() #comeca a receber mensagens/callbacks

#subscribe aos topics (so recebemos valores dos sensores)
for i in range(len(topics)):
    c.subscribe(topics[i])

#nao temos msgs para fazer publish para os sensores

#no fim?
# c.loop_stop()
