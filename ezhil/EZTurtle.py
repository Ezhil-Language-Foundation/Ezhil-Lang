## -*- coding: utf-8 -*-
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3

import turtle

class EZTurtle:
    """ EZTurtle class implements a singleton for famed Turtle module"""
    instance = None

    @staticmethod
    def getInstance( ):
        if not EZTurtle.instance:
            EZTurtle.instance = turtle.Pen();
        return EZTurtle.instance
    
    @staticmethod
    def functionAttributes():
        attrib = {0:['ht','home','showturtle','hideturtle','reset','penup','up','down','pendown','clear','isvisible',],
                  1:['rt','lt','left','right','forward','fd','bd','backward','color','fill'],
                  2:['goto'],
                  -1:['circle'] } #-1 => indicates varargs
        return attrib
    
    # 0-arg functions
    @staticmethod
    def home():
        apply(EZTurtle.getInstance().home,[])

    @staticmethod
    def clear():
        apply(EZTurtle.getInstance().clear,[])

    @staticmethod
    def showturtle( ):
        apply(EZTurtle.getInstance().showturtle,[])

    @staticmethod
    def hideturtle():
        apply(EZTurtle.getInstance().hideturtle,[])
    
    @staticmethod
    def penup():
        apply(EZTurtle.getInstance().penup,[])
    up = penup;
    #@staticmethod
    #def up():
    #   EZTurtle.penup()
    
    @staticmethod
    def pendown():
        apply(EZTurtle.getInstance().pendown,[])
        
    @staticmethod
    def down():
        EZTurtle.pendown()
    
    # 1-arg functions
    @staticmethod
    def rt(x):
        apply(EZTurtle.getInstance().rt,[x])

    @staticmethod
    def right(x):
        EZTurtle.rt(x)
    
    @staticmethod
    def lt(x):
        apply(EZTurtle.getInstance().lt,[x])
    
    @staticmethod
    def left(x):
        EZTurtle.lt(x)
        
    @staticmethod
    def forward(x):
        apply( EZTurtle.getInstance().forward,[x])

    @staticmethod
    def fd(x):
        EZTurtle.forward(x)
            
    @staticmethod
    def backward(x):
        apply(EZTurtle.getInstance().backward,[x])

    @staticmethod
    def bd(x):
        EZTurtle.backward(x)
    
    @staticmethod
    def back(x):
        apply(EZTurtle.getInstance().back,[x])

    @staticmethod
    def bk(x):
        apply(EZTurtle.getInstance().bk,[x])

    @staticmethod
    def circle(*x): #polymorphic invocation supported here
        apply(EZTurtle.getInstance().circle,x)

    @staticmethod
    def clearstamp(x):
        apply(EZTurtle.getInstance().clearstamp,[x])

    @staticmethod
    def clearstamps(x):
        apply(EZTurtle.getInstance().clearstamps,[x])

    @staticmethod
    def clone(x):
        apply(EZTurtle.getInstance().clone,[x])

    @staticmethod
    def color(x):
        apply(EZTurtle.getInstance().color,[x])

    @staticmethod
    def degrees(x):
        apply(EZTurtle.getInstance().degrees,[x])

    @staticmethod
    def distance(x):
        apply(EZTurtle.getInstance().distance,[x])

    @staticmethod
    def dot(x):
        apply(EZTurtle.getInstance().dot,[x])

    @staticmethod
    def fd(x):
        apply(EZTurtle.getInstance().fd,[x])

    @staticmethod
    def fill(x):
        apply(EZTurtle.getInstance().fill,[x])

    @staticmethod
    def fillcolor(x):
        apply(EZTurtle.getInstance().fillcolor,[x])

    @staticmethod
    def getpen(x):
        apply(EZTurtle.getInstance().getpen,[x])

    @staticmethod
    def getscreen(x):
        apply(EZTurtle.getInstance().getscreen,[x])

    @staticmethod
    def getturtle(x):
        apply(EZTurtle.getInstance().getturtle,[x])

    @staticmethod
    def goto(x,y):
        apply(EZTurtle.getInstance().goto,[x,y])

    @staticmethod
    def heading(x):
        apply(EZTurtle.getInstance().heading,[x])

    @staticmethod
    def ht():
        apply(EZTurtle.getInstance().ht,[])

    @staticmethod
    def isdown(x):
        apply(EZTurtle.getInstance().isdown,[x])

    @staticmethod
    def isvisible():
        apply(EZTurtle.getInstance().isvisible,[])

    @staticmethod
    def left(x):
        apply(EZTurtle.getInstance().left,[x])

    @staticmethod
    def ondrag(x):
        apply(EZTurtle.getInstance().ondrag,[x])

    @staticmethod
    def onrelease(x):
        apply(EZTurtle.getInstance().onrelease,[x])

    @staticmethod
    def pd(x):
        apply(EZTurtle.getInstance().pd,[x])

    @staticmethod
    def pen(x):
        apply(EZTurtle.getInstance().pen,[x])

    @staticmethod
    def pencolor(x):
        apply(EZTurtle.getInstance().pencolor,[x])

    @staticmethod
    def pensize(x):
        apply(EZTurtle.getInstance().pensize,[x])

    @staticmethod
    def pos(x):
        apply(EZTurtle.getInstance().pos,[x])
    
    @staticmethod
    def position(x):
        apply(EZTurtle.getInstance().position,[x])

    @staticmethod
    def pu(x):
        apply(EZTurtle.getInstance().pu,[x])

    @staticmethod
    def radians(x):
        apply(EZTurtle.getInstance().radians,[x])

    @staticmethod
    def reset(x):
        apply(EZTurtle.getInstance().reset,[x])

    @staticmethod
    def resizemode(x):
        apply(EZTurtle.getInstance().resizemode,[x])

    @staticmethod
    def right(x):
        apply(EZTurtle.getInstance().right,[x])

    @staticmethod
    def seth(x):
        apply(EZTurtle.getInstance().seth,[x])

    @staticmethod
    def setpos(x):
        apply(EZTurtle.getInstance().setpos,[x])

    @staticmethod
    def setposition(x):
        apply(EZTurtle.getInstance().setposition,[x])

    @staticmethod
    def settiltangle(x):
        apply(EZTurtle.getInstance().settiltangle,[x])

    @staticmethod
    def setundobuffer(x):
        apply(EZTurtle.getInstance().setundobuffer,[x])

    @staticmethod
    def setx(x):
        apply(EZTurtle.getInstance().setx,[x])

    @staticmethod
    def sety(x):
        apply(EZTurtle.getInstance().sety,[x])

    @staticmethod
    def shape(x):
        apply(EZTurtle.getInstance().shape,[x])

    @staticmethod
    def shapesize(x):
        apply(EZTurtle.getInstance().shapesize,[x])

    @staticmethod
    def speed(x):
        apply(EZTurtle.getInstance().speed,[x])

    @staticmethod
    def st(x):
        apply(EZTurtle.getInstance().st,[x])

    @staticmethod
    def stamp(x):
        apply(EZTurtle.getInstance().stamp,[x])

    @staticmethod
    def tilt(x):
        apply(EZTurtle.getInstance().tilt,[x])

    @staticmethod
    def tiltangle(x):
        apply(EZTurtle.getInstance().tiltangle,[x])

    @staticmethod
    def towards(x):
        apply(EZTurtle.getInstance().towards,[x])

    @staticmethod
    def tracer(x):
        apply(EZTurtle.getInstance().tracer,[x])

    @staticmethod
    def turtlesize(x):
        apply(EZTurtle.getInstance().turtlesize,[x])

    @staticmethod
    def undo(x):
        apply(EZTurtle.getInstance().undo,[x])

    @staticmethod
    def undobufferentries(x):
        apply(EZTurtle.getInstance().undobufferentries,[x])

    @staticmethod
    def width(x):
        apply(EZTurtle.getInstance().width,[x])

    @staticmethod
    def write(x):
        apply(EZTurtle.getInstance().write,[x])

    @staticmethod
    def xcor(x):
        apply(EZTurtle.getInstance().xcor,[x])

    @staticmethod
    def ycor(x):
        apply(EZTurtle.getInstance().ycor,[x])
