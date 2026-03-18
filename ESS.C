

/****************************************************************/
/*								*/
/*		Simulationssystem ESS				*/
/*								*/
/****************************************************************/


#include	<stdio.h>
#include	"ess.h"

/* Diese Struktur darf nicht veraendert werden!			*/

struct	sy_suak	{
	struct	sy_sxak	*sy_lpsxak;
	struct	sy_sak	*sy_lpsak[1]; /* wird erweitert */
	};

struct	sy_sak	sy_hsak;
struct	sy_sak	*sy_mpsak;

/* Die folgenden Definitionen duerfen nicht veraendert werden.	*/

#define	SUBJ		1
#define	CLASS		2
#define	ACT		3

#define	OK		0
#define	NO_REACT	-1
#define ACT_ERR		-2
#define	ERROR		-3

#define	GO		-1
#define	STOP		0

#define	CH_ACT(a,s) if(sy_look(ACT,(unsigned)a)==0)return(sy_err(s,1,ACT_ERR))
#define	CH_LZP(s)   if(lzp<1||lzp>n_log)return(sy_err(s,0,ACT_ERR))

char *sy_errme[] = {
	"Fehler bei logischem Zeitpunkt",
	"Unbekannte Aktion",
	"Falsche Adresse",
	"Subjekt existiert nicht",
	"Falsche Parameter",
	"Kein Platz fuer weitere Aktion",
	"Einfuegungszeit falsch"
	};

/****************************************************************/
/*								*/
/* Das Hauptprogramm ruft nach einer Initialisierung solange	*/
/* den Ablauf einer Periode auf, bis durch die Fini Funktion	*/
/* die Simulation beendet wird.					*/
/*								*/
/****************************************************************/

int ende = 1;

main()
      	{
      	register l;

    
        
        for(;;) /* NEU: ENDLOSSCHLEIFE-> d.h. Programm muss in Init mit */
         { /* exit(0) verlassen werden */                                 
          sy_sysinit();
          Init((struct sy_suak *)0);
       	  l = n_log;
       	  period = 1;
      	  logtime = 1;
      	  for(;Fini((struct sy_suak *)0); period++,logtime=1)
      	         for(; logtime<=l; logtime++)
      	    	     	 sy_simltp();
         }                          
      	}


/****************************************************************/
/*    								*/
/* Diese Funktion steuert den Ablauf einer Periode, indem fuer	*/
/* jedes Subjekt erst die ausserplanmaessigen und dann die	*/
/* Aktionen des Verhaltenplans ausgefuehrt werden.		*/
/*    								*/
/****************************************************************/

sy_simltp()
      	{
      	register	i,k;
      	register struct sy_suak *ps;
      	register struct sy_sxak *px;

      	for( i=1; i<=sy_anzsubj; i++ )
      		{
      		if( sy_mix == 1 )
      			{
      			k = Random(i,sy_anzsubj);
      			ps = sy_rtasu[k];
      			sy_rtasu[k] = sy_rtasu[i];
      			sy_rtasu[i] = ps;
      			}
      		else
      			ps = sy_tasu[i];
      		while( (px=ps->sy_lpsxak) != 0
      				&& px->sy_pexa == period
      				&& px->sy_loxa == logtime )
      			sy_xaktion(ps);

      		for(sy_mpsak=ps->sy_lpsak[logtime];
      		    sy_mpsak != 0; sy_mpsak = sy_mpsak->sy_psak)
			(*sy_mpsak->sy_pa)(ps);
		}
	}

/****************************************************************/
/*								*/
/* Hiermit werden ausserplanmaessige Aktionen ausgefuehrt.	*/
/*								*/
/****************************************************************/

sy_xaktion(ps)
struct sy_suak	*ps;
	{
	register	(*akt)();
	register	ab;
	register struct sy_sxak *p;

	p = ps->sy_lpsxak;
	akt = p->sy_pxa;
	ps->sy_lpsxak = p->sy_psxak;	/* abhaengen */
	if( (ab=p->sy_abxa) != 0 )
		{
		p->sy_pexa += ab;
		sy_xeinfak(ps, p);
		}
	else
		{
		p->sy_psxak = sy_frsxak;
		sy_frsxak = p;
		}
	(*akt)(ps);
}

/****************************************************************/
/*								*/
/* Einfuegen ausserplanmaessiger Aktionen in verkettete Liste	*/
/* geordnet nach Ausfuehrzeiten.				*/
/*								*/
/****************************************************************/

sy_xeinfak(ps, p)
struct sy_suak	*ps;
struct sy_sxak *p;
	{
	register	pde;
	register	lgz;
	register struct sy_sxak **pp;

	pde = p->sy_pexa;
	lgz = p->sy_loxa;
	pp = &ps->sy_lpsxak;
	while( (*pp != 0) && (((*pp)->sy_pexa < pde)
	     ||(((*pp)->sy_pexa == pde)&&((*pp)->sy_loxa <= lgz))))
		pp = &(*pp)->sy_psxak;
	p->sy_psxak = *pp;
	*pp = p;
}

/****************************************************************/
/*								*/
/* Loeschen einer Aktion im Verhaltensplan auf Systemebene.	*/
/*								*/
/****************************************************************/

struct sy_sak*
sy_fak(vakt)
register struct sy_sak **vakt;
	{
	register struct sy_sak *nakt;

	nakt = *vakt;
	*vakt = nakt->sy_psak;
	nakt->sy_psak = sy_frsak;
	sy_frsak = nakt;
	return( *vakt );	/* naechste Aktion */
	}

/****************************************************************/
/*								*/
/* Einfuegen einer Aktion im Verhaltensplan auf Systemebene.	*/
/*								*/
/****************************************************************/

struct sy_sak*
sy_eak(vakt)
register struct sy_sak **vakt;
	{
	register struct sy_sak *nakt;

	if( sy_frsak->sy_psak == 0 )
		{
		if( (sy_frsak->sy_psak = (struct sy_sak *)
		    malloc(sizeof(struct sy_sak))) == 0 )
			return(0);
		sy_frsak->sy_psak->sy_psak = 0;
		}
	nakt = *vakt;
	*vakt = sy_frsak;
	sy_frsak = sy_frsak->sy_psak;
	(*vakt)->sy_psak = nakt;
	return( *vakt );	/* eingefuegte Aktion */
	}


/****************************************************************/
/*								*/
/* Senden einer Nachricht an ein einzelnes Subjekt.		*/
/*								*/
/****************************************************************/

sy_sna1(adrna,mess,absnr)
register struct sy_suak	*adrna;
int	mess;
int	absnr;
	{
	register struct sy_sak	*ps;

	if( (ps = adrna->sy_lpsak[0]) == 0 )
		return(NO_REACT); /* Nachricht nicht bearbeitet */
	(*ps->sy_pa)(absnr,mess,adrna);
	return(OK);
	}

/****************************************************************/
/*								*/
/* Diese Funktion liefert zu einem Pointer auf eine Klasse,	*/
/* ein Subjekt oder eine Aktion den Index in der zugehoerigen	*/
/* Tabelle.							*/
/*								*/
/****************************************************************/

sy_look(t,v)
int	t;
register unsigned v;
	{
	register u;
	register o;
	int	 m;
	unsigned vf;
	struct sy_taca *tp;

	switch(t) {
	case CLASS: for( tp = &sy_clatab[1];
		       (tp->sy_cp != 0) && ((unsigned)(tp->sy_cp) != v); tp++);
		       if( (tp->sy_cp != 0) &&
			 (((struct sy_suak *)tp->sy_cp)->sy_lpsak[0]
			 >((struct sy_suak *)tp->sy_cp)->sy_lpsak[1]))
				return(0);
		    return( 1 + (tp - &sy_clatab[1]) );
	case SUBJ:  u = 1;
		    o = sy_anzsubj;
		    while( u <= o )
			if( (vf = (unsigned) sy_tasu[m=(u+o)/2]) == v )
				return(m);
			else if( vf < v )
				u = ++m;
			else
				o = --m;
		    return(0);
	case ACT:   u = 1;
		    o = sy_anzak;
		    while( u <= o )
			if((vf = (unsigned)sy_taak[m=(u+o)/2].sy_pa) == v)
				return(m);
			else if( vf < v )
				u = ++m;
			else
				o = --m;
		    return(0);
	}
}

/****************************************************************/
/*								*/
/* Ausgabe einer Fehlermeldung					*/
/*								*/
/****************************************************************/

sy_err(str,errno,err)
char	*str;
int	errno;
int	err;
	{
	printf("\nZum Zeitpunkt (%d,%d) fataler Fehler in %s:\n%s\n",
		period,logtime,str,sy_errme[errno]);
	return(err);
	}

/****************************************************************/
/*								*/
/* Systemfunktionen						*/
/*								*/
/****************************************************************/

Xins(ps, pe, l, fp, akt)
struct sy_suak *ps;
int	pe;
int	l;
int	fp;
int	(*akt)();
	{
	register struct sy_sxak *p;

	if( pe < 0 || (pe == 0 && l <= logtime ) )
		return(sy_err("Xins",6, ACT_ERR));
	CH_ACT(akt,"Xins");
	if( ((p=sy_frsxak)->sy_psxak) == 0 )
		{
		if( (sy_frsxak->sy_psxak = (struct sy_sxak *)
		    malloc(sizeof(struct sy_sxak))) == 0 )
			return(sy_err("Xins",5,	ACT_ERR));
		sy_frsxak->sy_psxak->sy_psxak = 0;
		}
	sy_frsxak = sy_frsxak->sy_psxak;
	p->sy_pxa = akt;
	p->sy_abxa = fp ? pe : 0;
	p->sy_pexa = period + pe;
	p->sy_loxa = l;
	sy_xeinfak(ps, p);
	return(OK);
}

Xrem(su, akt)
struct sy_suak	*su;
register	(*akt)();
	{
	register struct sy_sxak	**p;
	register struct sy_sxak	*n;

	CH_ACT(akt,"Xrem");
	p = &su->sy_lpsxak;
	while( *p != 0 )
		{
		if( (*p)->sy_pxa != akt )
			p = &(*p)->sy_psxak;
		else
			{
			n = *p;
			*p = n->sy_psxak;
			n->sy_psxak = sy_frsxak;
			sy_frsxak = n;
			return(OK);
			}
		}
	return(ACT_ERR);
	}


Rem(su, lzp, akt)
struct sy_suak	*su;
int		lzp;
register	(*akt)();
	{
	register struct sy_sak	**vakt;

	CH_LZP("Rem");
	CH_ACT(akt,"Rem");
	vakt = &su->sy_lpsak[lzp];
	while( *vakt != 0 )
		if( (*vakt)->sy_pa != akt )
			vakt = &(*vakt)->sy_psak;
		else
			{
			if( *vakt == sy_mpsak )
				{
				sy_mpsak = &sy_hsak;
				sy_hsak.sy_psak = sy_fak(vakt);
				}
			else
				sy_fak(vakt);
			return(OK);
			}
	return(ACT_ERR);		/* Aktion nicht vorhanden */
	}

Chge(su, lzp, nakt, akt)
struct sy_suak	*su;
int		lzp;
register	(*nakt)();
register	(*akt)();
	{
	register struct sy_sak	*vakt;

	CH_LZP("Chge");
	CH_ACT(akt,"Chge");
	CH_ACT(nakt,"Chge");
	vakt = su->sy_lpsak[lzp];
	while( vakt != 0 )
		if( vakt->sy_pa != akt )
			vakt = vakt->sy_psak;
		else
			{
			vakt->sy_pa = nakt;
			return(OK);
			}
	return(ACT_ERR);		/* Aktion nicht vorhanden */
	}

Ins(su, lzp, nakt, akt)
struct sy_suak	*su;
int		lzp;
register	(*nakt)();
register	(*akt)();
	{
	register struct sy_sak	**vakt;
	register struct sy_sak	*sy_psak;

	CH_LZP("Ins");
	if( (unsigned)akt != 0 )
		CH_ACT(akt,"Ins");
	CH_ACT(nakt,"Ins");
	vakt = &su->sy_lpsak[lzp];
	if( (unsigned)akt == 0 )
			goto einf;
	while( *vakt != 0 )
		if( (*vakt)->sy_pa != akt )
			vakt = &(*vakt)->sy_psak;
		else
			{
			vakt = &(*vakt)->sy_psak;
einf:			if( (sy_psak = sy_eak(vakt)) == 0 )
				return(sy_err("Ins",5,ACT_ERR));
			sy_psak->sy_pa = nakt;
			return(OK);
			}
	return(ACT_ERR);		/* Aktion nicht vorhanden */
	}

Send(abs,flag,adrna,mess)
struct sy_suak	*abs;
int		flag;
struct sy_suak	*adrna;
int		mess;
	{
	register	i;
	register	ret = OK;
	register	absnr;

	absnr = Ownnr(abs);
	if( sy_look(flag,(unsigned)adrna) == 0 )
		return(sy_err("Send",2,NO_REACT));
	if( flag == SUBJ )
		return( sy_sna1(adrna,mess,absnr) );
	else if( flag == CLASS )
		{
		for(i=(int)adrna->sy_lpsak[0];
		    i<=(int)adrna->sy_lpsak[1]; i++)
			if(sy_sna1(sy_tasu[i],mess,absnr)==NO_REACT)
				ret = NO_REACT;
		return(ret);
		}
	}

Plan(p)
	{
	register struct sy_taca *tp = &sy_clatab[1];
	register struct sy_sak *ps;
	register struct sy_sxak *px;
	register i, m, pflag = 1;
	unsigned cmp = (unsigned)p;

	if( sy_look(SUBJ, cmp) == 0 )
		return( sy_err("Plan",3,ERROR) );
	while( tp->sy_cp != 0 && (unsigned)tp->sy_cp < cmp )
		tp++;
	printf("\nPlan von %s[%d] zur Periode %d, log. Zpkt. %d:\n",
	(--tp)->sy_cn, Ownnr((struct sy_suak *)p),period,logtime );
	if( (px = ((struct sy_suak *)p)->sy_lpsxak) != 0 )
		{
		printf("Ausserpl. Aktionen:\n");
		while( px != 0 )
			{
			m = sy_look(ACT, (unsigned)px->sy_pxa);
			printf("%d,%d,%c: %s\n",px->sy_pexa,px->sy_loxa,
				px->sy_abxa?'p':'n',sy_taak[m].sy_na);
			px = px->sy_psxak;
			}
		}
	if( (ps = ((struct sy_suak *)p)->sy_lpsak[0]) != 0 )
		{
		m = sy_look(ACT, (unsigned)ps->sy_pa);
		printf("Messagefunktion:\n%s\n", sy_taak[m].sy_na);
		}
	printf("Aktionen:", period);
	for(i=1; i<=n_log; i++)
		if( (ps = ((struct sy_suak *)p)->sy_lpsak[i]) != 0 )
			{
			pflag = 0;
			printf("\n%d:", i);
			while( ps != 0 )
				{
				m = sy_look(ACT, (unsigned)ps->sy_pa);
				printf(" %s",sy_taak[m].sy_na);
				ps = ps->sy_psak;
				}
			}
	if( pflag != 0 )
		printf(" keine Aktionen vorhanden.");
	printf("\n");
}

Ownnr(p)
struct sy_suak *p;
	{
	register struct sy_taca *tp;
	register anz;
	register unsigned cmp;

	cmp = (unsigned)p;
	for(tp= &sy_clatab[1];
	    (tp->sy_cp!=0)&&(((unsigned)(tp->sy_cp))<cmp);tp++);
	anz = (int)((struct sy_suak *)(--tp)->sy_cp)->sy_lpsak[0];
	return( sy_look(SUBJ,cmp) - anz + 1 );
	}


Random(u,o)
	{
	static long z = 1;
	if( u > o || u < 0 )
		return( sy_err("Random",4,ERROR) );
	z = (z * 1103515245L + 12345) & 0xffffffff;
	return( (((z>>16)&0x7fff)%(o-u+1)) + u );
}


Min(x,y) {
	return( x < y ? x : y );
}

Max(x,y) {
	return( x > y ? x : y );
}
