#!/usr/bin/env python
# -*- coding: utf-8 -*-
#gckodriver esta copiado en /usr/local/bin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import Select

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from time import sleep
import random #random.random() da un numero randon entre el 0 y 1
import string, re, requests, os, sys, getopt

from minmail import mailbox
from proxy_list import grabProxiesHttp
from timeout import timeout
from private import *


#Comprueba si el proxy dado funciona correctamente
def checkProxy(proxy):
    try:
        print "Trying proxy: "+proxy
        http_p="http://"+proxy
        proxyDict = {"http" : http_p}
        r = requests.get("http://ip.42.pl/raw", proxies=proxyDict, timeout=5) #Nos devuelve la ip que debería ser la del proxy
        if (r.status_code == 200 and r.text == proxy.split(":")[0]):
            return True
        return False
    except:
        return False

#Crea un browser y a través de un proxy se conecta a una página
def createBrowser(url,proxy):
    global browser
    try:
        profile = webdriver.FirefoxProfile()
        p_split = proxy.split(":")
        ip = p_split[0]
        port = p_split[1]

        profile.set_preference("network.proxy.type", 1);
        profile.set_preference("network.proxy.http", ip);
        profile.set_preference("network.proxy.http_port", int(port));
        profile.set_preference("general.useragent.override", getRandLine(os.path.dirname(os.path.abspath(__file__))+"/useragents.txt"))
        #profile.add_extension(extension='/home/carlos/Desktop/selenium/adblock_for_firefox-3.4.0-an+fx-linux.xpi')

        browser = webdriver.Firefox(profile)
        browser.set_page_load_timeout(30)
        try:
            browser.get(url)
        except TimeoutException:
            print "TimeOut browser.get(url)"
            return False
        return True
    except:
        return False

#Dormir random
def my_sleep(n):
    sleep(random.random()+n)

#Escribir con retardo random
def elem_write(element, text):
    for letter in text:
        sleep(random.random()/2.8)
        element.send_keys(letter)

 #Le damos la primera acción a ejecutar para que compruebe si ha cargado bien la pagina
def checkLoadBrowser(): 
    global browser
    my_sleep(20)
    browser.execute_script('document.getElementsByTagName("button")[4].click()')

    try: 
        my_sleep(1)
        sign_up_box = browser.find_element_by_class_name("login-mail")
        ActionChains(browser).move_to_element(sign_up_box).click(sign_up_box).perform()
    except:
        my_sleep(1)#Repetimos la accion anterior pues por algun motivo alguna vez no funciona
        browser.execute_script('document.getElementsByTagName("button")[4].click()')
        my_sleep(1)
        sign_up_box = browser.find_element_by_class_name("login-mail")
        ActionChains(browser).move_to_element(sign_up_box).click(sign_up_box).perform()

    

def sign_in(mail, passw, name, last_name):
    global browser

    #Las dos primeras acciones del sign_in las realiza checkLoadBrowser() para comprobar
    #que la pagina se ha cargado correctamente

    my_sleep(1)
    name_box = browser.find_element_by_name("firstname") 
    elem_write(name_box, name)

    my_sleep(1)
    last_name_box = browser.find_element_by_name("lastname") 
    elem_write(last_name_box, last_name)

    my_sleep(1)
    mail_box = browser.find_element_by_xpath("//input[@type='email']")
    elem_write(mail_box, mail)

    my_sleep(1)
    pass_box = browser.find_element_by_xpath("//input[@type='password']")
    elem_write(pass_box, passw)

    pass_box.send_keys(Keys.RETURN)

#Devuelve una linea aleatoria de un texto dado
def getRandLine(path):
    array = []
    with open(path) as f:
        for line in f:
            array.append(line)
    return array[int( round( random.random()*(len(array)-1) ) )]
        


#Obtiene una contraseña random:mayus, minus y nº
def getPass():
    s = string.ascii_letters + string.digits
    passw = ""
    for i in range (0,8):
        passw += random.choice(s)
    return passw

#Pulsa el boton de reenviar mail
def resend_mail():
    browser.execute_script('document.getElementsByClassName("btn-send-login")[0].click()')

#Finaliza el registro completando los campos de compleaños y genero y pulsa el boton
def fin_reg(url_confirm, proxy):
    global browser

    browser.close()
    createBrowser(url_confirm,proxy)

    my_sleep(5)
    browser.execute_script('document.getElementById("formRegisterConfirmBirthday").value = "'+str(int(round(random.random()*12)))+'/'+str(int(round(random.random()*12)))+'/199'+str(int(round(random.random()*9)))+'"')
    
    my_sleep(1)
    select = Select(browser.find_element_by_id('formRegisterConfirmGender'))
    select.select_by_visible_text('Male')
    
    my_sleep(1)
    browser.execute_script('document.getElementsByClassName("btn-send-login")[0].removeAttribute("disabled")')
    browser.execute_script('document.getElementsByClassName("btn-send-login")[0].click()')

#Pilla el mail y saca la direccion para confirmar correo con http
def getConfirmUrl(msg_confirm):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg_confirm)
    confirm_url = urls[2].replace("https", "http")
    print confirm_url
    return confirm_url

#Recibe el mail de confirmación, si no lo recibe en 20seg pulsa el boton de reenviar y espera otros 20 seg
def getConfirmMail(mb):
    try: 
        with timeout(seconds=20):
            msg_confirm = mb.getCorreo() 
            return getConfirmUrl(msg_confirm)
    except:
        resend_mail()
        try:
            with timeout(seconds=20):
                msg_confirm = mb.getCorreo()
                return getConfirmUrl(msg_confirm)
        except:
            print "No ha llegado el correo"
            exit(90)

#Guarda el usuario y contraseña en un archivo
def saveNewUser(mail,passw,new_users_path):
    f = open(new_users_path, 'a')
    f.write(mail+":"+passw+'\n')
    f.close()


def logic(usernames_path, last_names_path, new_users_path):
    try:
        global browser
        proxies = grabProxiesHttp()
        for proxy in proxies:
            if checkProxy(proxy):
                print proxy
                if not createBrowser(URL, proxy): #Se da un timeout pasamos al siguiente proxy
                    browser.close()
                else:
                    try: #Miramos a ver si se ha cargado correctamente la página o sino probamos el siguiente proxy
                        checkLoadBrowser() 
                        break
                    except:
                        print "Ha fallado checkLoadBrowser()"
                        browser.close()
                        
        mb = mailbox()
        mail = mb.getMailAdd() #Obtenemos una dirección de 10minmail
        while "10mail" in mail: #No queremos que la dirección de mail contenga dicho string
            mb.close()
            mb = mailbox()
            mail = mb.getMailAdd()
        print mail
        
        passw = getPass() #Obtenemos una apass random
        print passw
        
        username = getRandLine(usernames_path)
        last_name = getRandLine(last_names_path)
        sign_in(mail, passw, username, last_name) #Realizamos el registro
        
        url_confirm = getConfirmMail(mb) #Epseramos a obtener en el correo el mensaje de confirmacion

        my_sleep(5)
        fin_reg(url_confirm, proxy) #Completamos el registro de la cuenta

        saveNewUser(mail,passw,new_users_path) #Guardamos el nuevo usuario
        return True
    except:
        print "Something went wrong"
        return False





def main(argv):
    global browser
    usernames_path = os.path.dirname(os.path.abspath(__file__))+"/usernames.txt"
    last_names_path = os.path.dirname(os.path.abspath(__file__))+"/last_names.txt"
    new_users_path = os.path.dirname(os.path.abspath(__file__))+"/users.txt"
    n_new_users = 50
    help_msg = 'webBot.py [-c <num_new_users>] [-n <usaernamesfile>] [-l <lastnamesfile>] [-o <newusersfile>]'
    try:
        opts, args = getopt.getopt(argv,"hc:n:l:o:",["numnewusers=","usernames=","lastnames=","newusers="])
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt in ("-n", "--usernames"):
            usernames_path = arg
        elif opt in ("-l", "--lastnames"):
            last_names_path = arg
        elif opt in ("-o", "--newusers"):
            new_users_path = arg
        elif opt in ("-c", "--numnewusers"):
            n_new_users = arg

    cont = 0
    while(cont < n_new_users):
        if logic(usernames_path, last_names_path, new_users_path):
            cont+=1
            print "Creados "+str(cont)+" usuarios"
            browser.close()


if __name__ == "__main__":
   main(sys.argv[1:])



