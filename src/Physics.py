from random import randint
import numpy as np

class Physics:
    
    def __init__(self, PosInicial, dt = 0.1, k = 3, m = 800, miu = 1, maxVel = 15):
        self.Pos = PosInicial
        self.PastPos = None
        self.PastDer = None
        self.PastVel = [0, 0]
        self.maxVel = maxVel
        
        self.TimeStep = 1
        self.long = np.arange(-10, 10, 0.2)
        
        self.dt = dt
        self.k = k
        
        self.miu = miu
        
        self.miu_hist = [miu] * 100
        
        self.m = m
        self.N = m * 9.8
        self.Fr = self.N*miu
        self.aant = [0, 0]
        self.Fant = [0, 0]
        self.corr = 4.4 
        
        
    def update_miu(self, miu, inside = True):
        
        self.miu_hist.append(miu)
        if inside:
            self.miu = np.mean(self.miu_hist[-60:])
        else:
            self.miu = np.mean(self.miu_hist[-60:])
        
    def accelerate(self, x):
        vel = self.maxVel / (1 + 3.8*np.exp(-0.08 * x + 3.3) ) - 0.2
        vel = vel if vel > 0 else 0
        return vel
        
    
    def getFirstDerivate(self, Pos):
        """
        y' = ( f(x) - f(x - h) ) / h
        
        In:
        Pos [tuple] - Posicion actual (x,y)
        
        Out:
        Derivada [float] - derivada en ese punto
        """
        
        h = (Pos[0] - self.PastPos[0])
        
        return (Pos[1] - self.PastPos[1]) / h
    
    
    def getSecondDerivate(self, Pos):
        """
        y' = ( f'(x) - f'(x - h) ) / h
        
        In:
        Pos [tuple] - Posicion actual (x,y)
        
        Out:
        Derivada [float] - segunda derivada en ese punto
        """
        h = (Pos[0] - self.PastPos[0])
        
        return (self.getFirstDerivate(Pos) - self.PastDer) / h
        
    
    def Update(self, Vel, Direccion, miu = None):
        
        """
        In:
        Direccion [tuple] - Posición actual [x,y]
        Vel [float] - Velocidad actual

        Out:
        NewPoss [tuple] - Posición actualizada [x,y]
        NewVel [float] - Velocidad actualizada
        """
        miu = miu if miu != None else self.miu
        
        x, y = self.Pos
        
        Dirx, Diry = Direccion
        # ======= Derivadas =========
        PrimDer = None
        if self.TimeStep > 1 :    
            PrimDer = self.getFirstDerivate((x,y))
            
        if self.TimeStep > 2:
            SegDer = self.getSecondDerivate((x,y))
        
        self.PastPos = [x, y]    
        # ======= Componentes de la posición =========
        alpha = np.arctan(Diry/Dirx)
        Vx = np.cos(alpha) * Vel
        Vy = np.sin(alpha) * Vel
        #print(f"Vx {Vx} y Vy {Vy} ")
        
        
        if self.TimeStep == 1 :
            self.Vel = [Vx, Vy]
            self.UpdateVelocityFirst(Vx, miu, ind = 0)
            self.UpdateVelocityFirst(Vy, miu, ind = 1)
        else:
            self.UpdateVelocity(Vx, miu, ind = 0)
            self.UpdateVelocity(Vy, miu, ind = 1)
        
        Vx = self.Vel[0]
        Vy = self.Vel[1]
        
        xa = self.PastPos[0]
        ya = self.PastPos[1]
        
        x = xa + Vx * self.dt + 0.5 * self.aant[0] * self.dt ** 2
        y = ya + Vy * self.dt + 0.5 * self.aant[1] * self.dt ** 2
        
        self.Pos = [x,y]
        
        # ====== Actualizando los parámetros =======
        self.PastDer = PrimDer
        self.TimeStep += 1
        
        
    def UpdateVelocity(self, v, miu = None, ind = 0):
        miu = miu if miu != None else self.miu
        #global aant, Fant, vi, vf
        Fr = self.m * 9.8 * miu
        Drag = self.k * ( ( ( self.Vel[ind] + self.PastVel[ind] )/2 )**2 )
        a = (self.Fant[ind] - Drag - Fr ) / self.m
        
        self.Vel[ind] = self.PastVel[ind] + self.dt*(a + self.aant[ind])/2 - self.corr
        self.Vel[ind] -= self.miu
        
        self.Vel[ind] = self.Vel[ind] if self.Vel[ind] > 0 else 0
        self.Vel[ind] = self.maxVel if self.Vel[ind] > self.maxVel else self.Vel[ind]
        

        self.Fant[ind] = self.m*self.aant[ind] + Fr + Drag
        self.PastVel[ind] = (v + self.Vel[ind])/2
        
        self.PastVel[ind] = self.PastVel[ind] if self.PastVel[ind] > 0 else 0
        
        self.aant[ind] = a
        self.aant[ind] = self.aant[ind] if self.aant[ind] > 0 else 0
        
    def UpdateVelocityFirst(self,v, miu = None, ind = 0):
        miu = miu if miu != None else self.miu
        
        Fr = self.m * 9.8 * miu
        
        Drag = self.k * (self.PastVel[ind]**2)
        self.Vel[ind] = v
        
        a = (self.Vel[ind] - self.PastVel[ind])/self.dt
        F = self.m*(a) + Fr + Drag
        
        self.PastVel[ind] = self.Vel[ind] 
        self.aant[ind] = a
        self.Fant[ind] = F    