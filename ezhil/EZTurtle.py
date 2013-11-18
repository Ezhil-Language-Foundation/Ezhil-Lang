## -*- coding: utf-8 -*-
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3

import turtle

class EZTurtle:
    """ EZTurtle class implements a singleton for famed Turtle module.
        Unfortunately turtle class does not take Unicode arguments.    """
    instance = None
    
    @staticmethod
    def getInstance( ):
        if not EZTurtle.instance:
            EZTurtle.instance = turtle.Pen();
        return EZTurtle.instance
    
    @staticmethod
    def functionAttributes():
        attrib = {0:['ht','home','showturtle','hideturtle','reset','penup','up','down','pendown','clear','isvisible',],
                  1:['rt','lt','left','right','forward','fd','bd','backward','color','fill','speed','pencolor','dot'],
                  2:['goto'],
                  -1:['circle','setworldcoordinates'] } #-1 => indicates varargs
        return attrib
    
    # 0-arg functions
    @staticmethod
    def home():
        EZTurtle.getInstance().home(*[])

    @staticmethod
    def clear():
        EZTurtle.getInstance().clear(*[])

    @staticmethod
    def showturtle( ):
        EZTurtle.getInstance().showturtle(*[])

    @staticmethod
    def hideturtle():
        EZTurtle.getInstance().hideturtle(*[])
    
    @staticmethod
    def penup():
        EZTurtle.getInstance().penup(*[])
    up = penup;

    @staticmethod
    def pendown():
        EZTurtle.getInstance().pendown(*[])
        
    @staticmethod
    def down():
        EZTurtle.pendown()
    
    # 1-arg functions
    @staticmethod
    def rt(x):
        EZTurtle.getInstance().rt(*[x])

    @staticmethod
    def right(x):
        EZTurtle.rt(x)
    
    @staticmethod
    def lt(x):
        EZTurtle.getInstance().lt(*[x])
    
    @staticmethod
    def left(x):
        EZTurtle.lt(x)
        
    @staticmethod
    def forward(x):
        EZTurtle.getInstance().forward(*[x])

    @staticmethod
    def fd(x):
        EZTurtle.forward(x)
            
    @staticmethod
    def backward(x):
        EZTurtle.getInstance().backward(*[x])

    @staticmethod
    def bd(x):
        EZTurtle.backward(x)
    
    @staticmethod
    def back(x):
        EZTurtle.getInstance().back(*[x])

    @staticmethod
    def bk(x):
        EZTurtle.getInstance().bk(*[x])
    
    @staticmethod
    def setworldcoordinates(*x): #polymorphic invocation supported here
        turtle.setworldcoordinates(*x)
    
    @staticmethod
    def circle(*x): #polymorphic invocation supported here
        EZTurtle.getInstance().circle(*x)

    @staticmethod
    def clearstamp(x):
        EZTurtle.getInstance().clearstamp(*[x])

    @staticmethod
    def clearstamps(x):
        EZTurtle.getInstance().clearstamps(*[x])

    @staticmethod
    def clone(x):
        EZTurtle.getInstance().clone(*[x])

    @staticmethod
    def color(x):        
        EZTurtle.getInstance().color(*[str(x)])
    
    @staticmethod
    def degrees(x):
        EZTurtle.getInstance().degrees(*[x])

    @staticmethod
    def distance(x):
        EZTurtle.getInstance().distance(*[x])

    @staticmethod
    def dot(x):
        EZTurtle.getInstance().dot(*[x])

    @staticmethod
    def fill(x):
        EZTurtle.getInstance().fill(*[x])

    @staticmethod
    def fillcolor(x):
        EZTurtle.getInstance().fillcolor(*[x])

    @staticmethod
    def getpen(x):
        EZTurtle.getInstance().getpen(*[x])

    @staticmethod
    def getscreen(x):
        EZTurtle.getInstance().getscreen(*[x])

    @staticmethod
    def getturtle(x):
        EZTurtle.getInstance().getturtle(*[x])

    @staticmethod
    def goto(x,y):
        EZTurtle.getInstance().goto(*[x,y])

    @staticmethod
    def heading(x):
        EZTurtle.getInstance().heading(*[x])

    @staticmethod
    def ht():
        EZTurtle.getInstance().ht(*[])

    @staticmethod
    def isdown(x):
        EZTurtle.getInstance().isdown(*[x])

    @staticmethod
    def isvisible():
        EZTurtle.getInstance().isvisible(*[])

    @staticmethod
    def ondrag(x):
        EZTurtle.getInstance().ondrag(*[x])

    @staticmethod
    def onrelease(x):
        EZTurtle.getInstance().onrelease(*[x])

    @staticmethod
    def pd(x):
        EZTurtle.getInstance().pd(*[x])

    @staticmethod
    def pen(x):
        EZTurtle.getInstance().pen(*[x])

    @staticmethod
    def pencolor(x):
        EZTurtle.getInstance().pencolor(*[str(x)])

    @staticmethod
    def pensize(x):
        EZTurtle.getInstance().pensize(*[x])

    @staticmethod
    def pos(x):
        EZTurtle.getInstance().pos(*[x])
    
    @staticmethod
    def position(x):
        EZTurtle.getInstance().position(*[x])

    @staticmethod
    def pu(x):
        EZTurtle.getInstance().pu(*[x])

    @staticmethod
    def radians(x):
        EZTurtle.getInstance().radians(*[x])

    @staticmethod
    def reset():
        EZTurtle.getInstance().reset()
    
    @staticmethod
    def resizemode(x):
        EZTurtle.getInstance().resizemode(*[x])

    @staticmethod
    def seth(x):
        EZTurtle.getInstance().seth(*[x])

    @staticmethod
    def setpos(x):
        EZTurtle.getInstance().setpos(*[x])

    @staticmethod
    def setposition(x):
        EZTurtle.getInstance().setposition(*[x])

    @staticmethod
    def settiltangle(x):
        EZTurtle.getInstance().settiltangle(*[x])

    @staticmethod
    def setundobuffer(x):
        EZTurtle.getInstance().setundobuffer(*[x])

    @staticmethod
    def setx(x):
        EZTurtle.getInstance().setx(*[x])

    @staticmethod
    def sety(x):
        EZTurtle.getInstance().sety(*[x])

    @staticmethod
    def shape(x):
        EZTurtle.getInstance().shape(*[x])

    @staticmethod
    def shapesize(x):
        EZTurtle.getInstance().shapesize(*[x])

    @staticmethod
    def speed(x):
        EZTurtle.getInstance().speed(*[x])

    @staticmethod
    def st(x):
        EZTurtle.getInstance().st(*[x])

    @staticmethod
    def stamp(x):
        EZTurtle.getInstance().stamp(*[x])

    @staticmethod
    def tilt(x):
        EZTurtle.getInstance().tilt(*[x])

    @staticmethod
    def tiltangle(x):
        EZTurtle.getInstance().tiltangle(*[x])

    @staticmethod
    def towards(x):
        EZTurtle.getInstance().towards(*[x])

    @staticmethod
    def tracer(x):
        EZTurtle.getInstance().tracer(*[x])

    @staticmethod
    def turtlesize(x):
        EZTurtle.getInstance().turtlesize(*[x])

    @staticmethod
    def undo(x):
        EZTurtle.getInstance().undo(*[x])

    @staticmethod
    def undobufferentries(x):
        EZTurtle.getInstance().undobufferentries(*[x])

    @staticmethod
    def width(x):
        EZTurtle.getInstance().width(*[x])

    @staticmethod
    def write(x):
        EZTurtle.getInstance().write(*[x])

    @staticmethod
    def xcor(x):
        EZTurtle.getInstance().xcor(*[x])

    @staticmethod
    def ycor(x):
        EZTurtle.getInstance().ycor(*[x])
