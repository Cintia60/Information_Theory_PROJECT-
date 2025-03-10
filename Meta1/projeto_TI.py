#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 22:22:30 2022

@author: CintiaCumbane
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile 
import matplotlib.image as mpimg
from huffmancodec import HuffmanCodec
import string

#Exercicio 1,2,3

ficheiro="/Users/CintiaCumbane/Desktop/TP1_v2-2/DATA/soundMono.wav"
pic1 = "/Users/CintiaCumbane/Desktop/TP1_v2-2/DATA/MRIbin.bmp"
pic2 = "/Users/CintiaCumbane/Desktop/TP1_v2-2/DATA/landscape.bmp"
pic3 = "/Users/CintiaCumbane/Desktop/TP1_v2-2/DATA/MRI.bmp"

[fs, data] = wavfile.read(ficheiro)




imagem1 = plt.imread(pic1)
imagem2 = plt.imread(pic2)
imagem3 = plt.imread(pic3)

def um_canal (palavra):
   return palavra.flatten() 



Fre_abs = [ 3, 3, 4, 1, 5, 5, 6, 7, 8, 8]
A = [1, 2, 3, 4, 5, 6, 7, 8, 9]



def compara(Fre_abs):
    a = A
    d = {}
    for j in Fre_abs:
        if j in a:
            if j in d:
                d[j] += 1
            else:
                d[j] = 1
        
    return d





def palavras():
    f = open("/Users/CintiaCumbane/Desktop/TP1_v2-2/DATA/lyrics.txt", "r")
    lista = []
    for linha in f:
        for letra in linha:
            if letra in string.ascii_letters:
                lista.append(letra)
                
    return lista


def ultimo_dicio (palavra):
    dic = {}
    for i in palavra:
        if i in string.ascii_letters:
            if i not in dic:
                dic[i] = 1
            else:
                dic[i] += 1
    for k in string.ascii_letters:
        if k not in dic:
            dic.setdefault(k, 0)     
    return dict(sorted(dic.items()))




def simbolo_m(palavra):
    lista_2 = []
    count = {}
    for i in palavra:
        # acrescentar elementos a lista
        lista_2.append(i)
        # comparar os elementos da lista
    for j in lista_2:
        if j not in count:
            count[j] = 1
        else:
            count[j] += 1

    return dict(sorted(count.items()))





def calcula(palavra):
    lst = simbolo_m(palavra)
    return list(lst.values())




def probabilidade(palavra):
    lista = []
    num = calcula(palavra)
    total = sum(num)
    for i in num:
        if i != 0:
            prob = (i/total)
        lista.append(prob)
        return lista
                 

  



def entropia(palavra):
    return -np.sum(probabilidade(palavra) * np.log2(probabilidade(palavra)))/2


def histograma (d,nome):
    plt.ylabel("Número de Contagens")
    plt.title("Histograma " + '\n' + str(nome))
    plt.bar(d.keys(), d.values(), color= "green" )
    plt.show()
    
    
    
    
 


def huff (palavra):
    codec = HuffmanCodec.from_data(palavra)
    symbols,lenghts = codec.get_code_len() 
    return lenghts

def entropia_huff(palavra):
    lista = []
    for i in range (len(probabilidade(palavra))):
        a = probabilidade(palavra)[i] * huff(palavra)[i]
        lista.append(a)
    return np.sum(lista)


def variancia(palavra):
    return np.sum(probabilidade(palavra) * ((huff(palavra))-entropia_huff(palavra))**2)

# ponto 5
def agrupamento_simbolos(palavra):
    lista2 = []
    count = {}
    for a,b in zip(palavra[0::2], palavra[1::2]): 
        lista2.append((a,b))
    for i in lista2:
        if i not in count:
            count[i] = 1
        else:
            count[i] += 1
    return count

      
def prob_agrupamento_simbolos(palavra):
    lista = []
    a= agrupamento_simbolos(palavra)
    total =sum(a.values())
    for i in a.values():
        if i != 0:
            prob = i/total
            lista.append(prob)
    return lista 
  
def entropia_agrup_simbolos(palavra):  
    return (-np.sum(prob_agrupamento_simbolos(palavra) * np.log2(prob_agrupamento_simbolos(palavra))))/2
        

 


if __name__=="__main__":
    
 #Exercicio 1,2,3   

    
    print(entropia(Fre_abs))
    print(entropia(palavras()))
    print(entropia(um_canal(imagem1)))
    print(entropia(um_canal(imagem2)))
    print(entropia(um_canal(imagem3)))
    print(entropia(um_canal(data)))
   
    
    
    print(histograma(compara(Fre_abs),"compara"))
    print(histograma(ultimo_dicio(palavras()),"texto"))
    print(histograma(simbolo_m(um_canal(imagem1)),pic1))
    print(histograma(simbolo_m(um_canal(imagem2)),pic2))
    print(histograma(simbolo_m(um_canal(imagem3)),pic3,))
    print(histograma(simbolo_m(um_canal(data)),ficheiro))
    
   
    
#Exercicio 4
    print(entropia_huff(palavras()))
    print(entropia_huff(um_canal(imagem1)))
    print(entropia_huff(um_canal(imagem2)))
    print(entropia_huff(um_canal(imagem3)))
    print(entropia_huff(um_canal(data)))
     
    print(variancia(palavras()))
    print(variancia(um_canal(imagem1)))
    print(variancia(um_canal(imagem2)))
    print(variancia(um_canal(imagem3)))
    print(variancia(um_canal(data)))  
    
#Exercicio 5


    print(entropia_agrup_simbolos(palavras()))
    print(entropia_agrup_simbolos(um_canal(imagem1)))
    print(entropia_agrup_simbolos(um_canal(imagem2)))
    print(entropia_agrup_simbolos(um_canal(imagem3)))
    print(entropia_agrup_simbolos(um_canal(data)))
    
    
  
    
   
    