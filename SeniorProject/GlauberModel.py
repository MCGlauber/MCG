import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

data=np.loadtxt("PDG_Data.txt",float,usecols=(0,1,2,3,4,5,6,7,8))
Point=data[:,0]
Plab=data[:,1] #GeV/c
Plab_min=data[:,2]
Plab_max=data[:,3]
Sig=data[:,4]
StEr_H=data[:,5]
StEr_L=data[:,6]
SyEr_H=data[:,7]
SyEr_L=data[:,8]

Edata=np.loadtxt("EPNG_Data.txt",float,usecols=(0,1,2,3,4,5,6,7,8))
EPoint=Edata[:,0]
EPlab=Edata[:,1] #GeV/c
EPlab_min=Edata[:,2]
EPlab_max=Edata[:,3]
ESig=Edata[:,4]
EStEr_H=Edata[:,5]
EStEr_L=Edata[:,6]
ESyEr_H=Edata[:,7]
ESyEr_L=Edata[:,8]

def func(s,Z,M,Y1,Y2,n1,n2):
    m=.938
    sM=(2*m+M)**2
    hbar=6.58211928*10**-16
    c=3e8
    sigma=Z+np.pi*(hbar*c)**2/M**2*(np.log((s)**2/sM))**2+Y1*(sM/(s)**2)**n1-Y2*(sM/(s)**2)**n2
    return sigma

def func2(s,a,b):
    return a*np.e**(b*s)+.42

def func3(s,a,b):
    return np.log(a*s)+b

def func4(s,a,b):
    return np.e**(a*np.log(s)+b)

s=EPlab[:]
y=ESig[:]
p0=[5,2.15,12.72,7.35,.462,.55]
popt,pcov=curve_fit(func,s,y,p0)
sp=np.zeros(np.size(s)+1,float)
sp[:-1]=np.copy(s)
sp[-1]=200
sp2=np.arange(2e3,9e3,1000)
sp3=np.arange(8.6e3,6e8,1000)

s2=Plab[:]
y2=Sig[:]
p0=[34.71,2.15,12.72,7.35,.462,.550]
popt2,pcov2=curve_fit(func,s2,y2,p0)

g=np.arange(5,6*10**8,1000)
SigInel=func(g,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])-func(g,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])

def SigI(BE):
    """Returns the cross-sectional area [fm^2] for given beam energy [GeV]"""
    return .1*(func(BE,popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5])-func(BE,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5]))

def DisplayData():
    """Displays the Particle Data Group Data."""
    plt.loglog(Plab,Sig,ls=' ',marker='.',markersize=3,color='black')
    plt.loglog(EPlab,ESig,ls=' ',marker='.',markersize=3,color='black')
    plt.loglog(sp,func(sp,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5]),color='b',lw=1.5)
    plt.loglog(sp2,func2(sp2,6.566,.00001),lw=1.5)
    plt.loglog(sp3,func4(sp3,9*10**-2,1.21),color='b',lw=1.5)
    plt.loglog(s2[100:],func(s2[100:],popt2[0],popt2[1],popt2[2],popt2[3],popt2[4],popt2[5]),color='b',lw=1.5)
    plt.errorbar(Plab,Sig,xerr=[Plab-Plab_min,Plab_max-Plab],yerr=[StEr_L,StEr_H],ms=.5,mew=0,fmt=None,ecolor='black')
    plt.errorbar(EPlab,ESig,xerr=[EPlab-EPlab_min,EPlab_max-EPlab],yerr=[EStEr_L,EStEr_H],ms=.5,mew=0,fmt=None,ecolor='black')
    plt.annotate("$P_{lab}(GeV/c)$",fontsize=16,xy=(.1,1),xytext=(10e5,1.5))
    plt.annotate("total",fontsize=11,xy=(300,60),xytext=(300,60))
    plt.annotate("elastic",fontsize=11,xy=(300,10),xytext=(300,10))
    plt.annotate("pp",fontsize=11,xy=(70,15),xytext=(68,18))
    plt.ylabel("Cross Section (mb)",fontsize=12)
    plt.ylim(1,400)
    plt.grid(which='minor',axis='y')
    plt.grid(which='major',axis='x')

def WoodsSaxon(y):
    """Returns the Woods-Saxon Density profile for given element or atomic number"""
    A={'C':12,'O':16,'Al':27,'S':32,'Ca':40,'Ni':58,'Cu':63,'W':186,'Au':197,'Pb':208,'U':238}
    if type(y)==str:
        x=y
    else:
        for An,Val in A.iteritems():
            if Val==y:
                x=An
    a={'C':0,'O':.513,'Al':.519,'S':.61,'Ca':.586,'Ni':.516,'Cu':.596,'W':.535,'Au':.535,'Pb':.546,'U':.6}
    w={'C':0,'O':-.051,'Al':0,'S':0,'Ca':-.161,'Ni':-.1308,'Cu':0,'W':0,'Au':0,'Pb':0,'U':0}
    R={'C':2.47,'O':2.608,'Al':3.07,'S':3.458,'Ca':3.76,'Ni':4.309,'Cu':4.2,'W':6.51,'Au':6.38,'Pb':6.68,'U':6.68}
    r=np.arange(0,1.5*R[x]+.01,.01)
    Rho=(1+w[x]*(r**2)/(R[x]**2))/(1+np.e**((r-R[x])/a[x]))
    return Rho

def distribute1D(x,prob,N):
    """Takes any numerical distribution prob, on the interval defined by the array x, and returns an array of N sampled values that are statistically the same as the input data."""
    y=prob
    A=np.cumsum(y)/(np.cumsum(y)[(len(x)-1)])
    z=np.random.random_sample(N)
    B=np.searchsorted(A,z)
    return x[B]

def Collider(N,Particle,BeamEnergy):
    """
    Simulates N collisions given specific Element and Beam Energy [GeV]. 
    Returns the matrices that correspond to center-to-center seperation distance 
    (Random value between 0 and 150% of the Nucleus diameter [fm]), 
    Nuclei 1 and 2, number participating nucleons, and the number of binary 
    collisions. Additionally returns the interactions distance of the nucleons 
    given the choosen beam energy.
    """
    w={'C':0,'O':-.051,'Al':0,'S':0,'Ca':-.161,'Ni':-.1308,'Cu':0,'W':0,'Au':0,'Pb':0,'U':0}
    A={'C':12,'O':16,'Al':27,'S':32,'Ca':40,'Ni':58,'Cu':63,'W':186,'Au':197,'Pb':208,'U':238}
    R={'C':2.47,'O':2.608,'Al':3.07,'S':3.458,'Ca':3.76,'Ni':4.309,'Cu':4.2,'W':6.51,'Au':6.38,'Pb':6.68,'U':6.68}
    a={'C':0,'O':.513,'Al':.519,'S':.61,'Ca':.586,'Ni':.516,'Cu':.596,'W':.535,'Au':.535,'Pb':.546,'U':.6}
    Rp=R[Particle] 
    b=2*Rp*np.random.random_sample(N)
    r=np.arange(0,1.5*Rp+.01,.01)
    Npart=np.zeros(N,float)
    Ncoll=np.zeros(N,float)
    Maxr=(float(SigI(BeamEnergy))/np.pi)**.5
    for L in range(N):
        Nucleus1=np.zeros((A[Particle],2),float)
        Nucleus2=np.zeros((A[Particle],2),float)
        Nucleus1[:,0]=distribute1D(r,WoodsSaxon(Particle),A[Particle])[:]
        Nucleus2[:,0]=distribute1D(r,WoodsSaxon(Particle),A[Particle])[:]
        for i in range(A[Particle]):
            Nucleus1[i,1]=2*np.pi*np.random.random_sample(1)
            Nucleus2[i,1]=2*np.pi*np.random.random_sample(1)
        Colide1=np.copy(Nucleus1)
        Colide2=np.copy(Nucleus2)
        for p1 in range(A[Particle]):
            count=0
            for p2 in range(A[Particle]):
                if ((b[L]+Nucleus2[p2,0]*np.cos(Nucleus2[p2,1])-Nucleus1[p1,0]*np.cos(Nucleus1[p1,1]))**2+(Nucleus2[p2,0]*np.sin(Nucleus2[p2,1])-Nucleus1[p1,0]*np.sin(Nucleus1[p1,1]))**2)**.5 <= Maxr:
                    Ncoll[L]+=1
                if ((b[L]+Nucleus2[p2,0]*np.cos(Nucleus2[p2,1])-Nucleus1[p1,0]*np.cos(Nucleus1[p1,1]))**2+(Nucleus2[p2,0]*np.sin(Nucleus2[p2,1])-Nucleus1[p1,0]*np.sin(Nucleus1[p1,1]))**2)**.5 > Maxr:
                    count+=1
                if count==A[Particle]:
                    Colide1[p1]=1000
        for p2 in range(A[Particle]):
            count=0
            for p1 in range(A[Particle]):
                if ((b[L]+Nucleus2[p2,0]*np.cos(Nucleus2[p2,1])-Nucleus1[p1,0]*np.cos(Nucleus1[p1,1]))**2+(Nucleus2[p2,0]*np.sin(Nucleus2[p2,1])-Nucleus1[p1,0]*np.sin(Nucleus1[p1,1]))**2)**.5 > Maxr:
                    count+=1
                if count==A[Particle]:
                    Colide2[p2]=1000
        for i in Colide1[:,0]:
            if i<1000:
                Npart[L]+=1
        for i in Colide2[:,0]:
            if i<1000:
                Npart[L]+=1
    return b,Nucleus1,Nucleus2,Npart,Ncoll,Maxr,Colide1,Colide2

def PlotNuclei(Nucleus1,Nucleus2,Particle):
    """
    Plots a histogram showing the relation between radial distance and 
    the number of nucleons from each nucleus. 
    Blue corresponds to nucleus 1 and green to nucleus 2.
    """
    w={'C':0,'O':-.051,'Al':0,'S':0,'Ca':-.161,'Ni':-.1308,'Cu':0,'W':0,'Au':0,'Pb':0,'U':0}
    A={'C':12,'O':16,'Al':27,'S':32,'Ca':40,'Ni':58,'Cu':63,'W':186,'Au':197,'Pb':208,'U':238}
    R={'C':2.47,'O':2.608,'Al':3.07,'S':3.458,'Ca':3.76,'Ni':4.309,'Cu':4.2,'W':6.51,'Au':6.38,'Pb':6.68,'U':6.68}
    a={'C':0,'O':.513,'Al':.519,'S':.61,'Ca':.586,'Ni':.516,'Cu':.596,'W':.535,'Au':.535,'Pb':.546,'U':.6}
    Rp=R[Particle]
    r=np.arange(0,1.5*Rp+.01,.01)
    n1,bins,patches=plt.hist(Nucleus1[:,0],15,normed=True,alpha=1)
    n2,bins,patches=plt.hist(Nucleus2[:,0],15,normed=True,alpha=.8)
    if max(n1)<=max(n2):
        plt.plot(r,WoodsSaxon(Particle)*max(n2),lw=2.5)
    else:
        plt.plot(r,WoodsSaxon(Particle)*max(n1),lw=2.5)
    plt.xlabel("Radial Distance [fm]",fontsize=14)
    plt.ylabel("Density",fontsize=14)

def PlotCollision(N,Particle,ImpactDistance,Nucleus1,Nucleus2,Participants,BinaryCollisions,Maxr,Col1,Col2):
    """Plots a cross-sectional view of the colliding particles."""
    b=ImpactDistance
    Npart=Participants
    Ncoll=BinaryCollisions
    w={'C':0,'O':-.051,'Al':0,'S':0,'Ca':-.161,'Ni':-.1308,'Cu':0,'W':0,'Au':0,'Pb':0,'U':0}
    A={'C':12,'O':16,'Al':27,'S':32,'Ca':40,'Ni':58,'Cu':63,'W':186,'Au':197,'Pb':208,'U':238}
    R={'C':2.47,'O':2.608,'Al':3.07,'S':3.458,'Ca':3.76,'Ni':4.309,'Cu':4.2,'W':6.51,'Au':6.38,'Pb':6.68,'U':6.68}
    a={'C':0,'O':.513,'Al':.519,'S':.61,'Ca':.586,'Ni':.516,'Cu':.596,'W':.535,'Au':.535,'Pb':.546,'U':.6}
    Rp=R[Particle]
    N1=plt.Circle((Rp,Rp),Rp,color='b',fill=False,lw=2)
    N2=plt.Circle((Rp+b[N-1],Rp),Rp,color='g',fill=False,lw=2)
    fig = plt.gcf()
    ax = plt.gca()
    ax.plot(Rp+Nucleus1[:,0]*np.cos(Nucleus1[:,1]),Rp+Nucleus1[:,0]*np.sin(Nucleus1[:,1]),'b.',ms=26,alpha=.8,mew=1,mec='blue')
    ax.plot(Rp+b[N-1]+Nucleus2[:,0]*np.cos(Nucleus2[:,1]),Rp+Nucleus2[:,0]*np.sin(Nucleus2[:,1]),'g.',ms=26,alpha=.8,mew=1,mec='green')
    ax.plot(Rp+Col1[:,0]*np.cos(Col1[:,1]),Rp+Col1[:,0]*np.sin(Col1[:,1]),'r.',ms=26,alpha=.4,mew=1,mec='red')
    ax.plot(Rp+b[N-1]+Col2[:,0]*np.cos(Col2[:,1]),Rp+Col2[:,0]*np.sin(Col2[:,1]),'r.',ms=26,alpha=.4,mew=1,mec='red')
    ax.annotate('Npart='+str(Npart[N-1])+'\nNcoll='+str(Ncoll[N-1]),xy=(1,0),xytext=(-3,26.5),fontsize=16)
    ax.annotate('Maxr: '+str(Maxr)+' fm',xy=(0,2*Rp),xytext=(-3,24.5),fontsize=12)
    fig.gca().add_artist(N1)
    fig.gca().add_artist(N2)
    plt.plot([-2.5,Maxr-2.5],[24,24],color='r',ls='-',lw=3)
    plt.xlim((-4,26))
    plt.ylim((-4,26))
    plt.xlabel('Horizontal Position [fm]',fontsize=15)
    plt.ylabel('Vertical Position [fm]',fontsize=15)
    fig.set_size_inches(6,6)

def PlotResults(b,Npart,Ncoll):
    """Plots the number or wounded nucleons and binary collisions as a function of impact parameter."""
    plt.scatter(b,Npart,label='Participants',color='b',alpha=.6)
    plt.scatter(b,Ncoll,label='Collisions',color='r',alpha=.6)
    plt.xlabel('Separation distance [fm]',fontsize=14)
    plt.xlim((0,max(b)))
    plt.ylim((0,max(Ncoll)*1.1))
    plt.legend()