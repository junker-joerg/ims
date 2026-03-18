/* ***************************************************************** */
/*               IMS, The Insurance Market Simulation                */
/*                       (c) Martin Koehler                          */
/*                             1995                                  */
/* ***************************************************************** */
#define MAXNLOG   10
ims (n_log=MAXNLOG)      /* ESL-Programmkopf                         */
#include <time.h>        /* Einbinden von Standard-C  Header-Files   */
#include <math.h>
#include <malloc.h>
#include <stdlib.h>
#include "imsrnd.c"      /* Einbinden der IMS-internen Programmteile */
#include "imssurfe.c"
#include "imsdata.c"

/* ***************************************************************** */
/* class BAV: Definition der ESL-class BAV und ihrer Aktionen. BAV   */
/*            verwaltet die Fremdinformationen, die von den class VU */
/*            und VN benoetigt werden.                               */
/* ***************************************************************** */
class BAV {
            classBAV DatenBAV;
            } subj[1] =
            {
            xact: (1,1,1) Myinitbv
             act: 1 Newinibv Frmdinf
                 10 Agrsich
            };
/* ***************************************************************** */
/* Initialisierungsfunktion der class BAV. Sie wird NUR in der ersten*/
/* Periode des ersten Simulationslaufs ausgefuehrt. Die Neu-Initia-  */
/* lisierung in den Laeufen > 1 erfolgt in der act <Newinibv>        */
/* ***************************************************************** */
act Myinitbv {
int i;                                  /* Schleifenvariable         */
if ( ( rl == 1 ) &&  (period == 1) )
 {
  for(i = 0 ; i < MAXSPARTEN ; i++ )
   {
    BAV[Ownnr()].DatenBAV.Pm[i] = 0.0;/* Minimalpraemie,Sparte   :{0}*/
    BAV[Ownnr()].DatenBAV.Wm[i] = 0.0;/* Maximalwerbung,Sparte   :{0}*/
    BAV[Ownnr()].DatenBAV.Dp[i] = 0.0;/* Durchschn.praemie,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Dw[i] = 0.0;/* Durchschn.werbung,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Mp[i] = 0.0;/* Marktfueh.praemie,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Mw[i] = 0.0;/* Marktfueh.werbung,Spart.:{0}*/
   }
  for( i = 0  ; i < MAXRISKS  ; i++  )
   {
    BAV[Ownnr()].DatenBAV.Dg[i] = 0.0;/* Durchschnl. Versich.grad {0}*/
   }
   fprintf(runreport, "Myinitbv:[%d,%d]\n",logtime,period );
 } /* END: if ( ( rl == 1 ) &&  (period == 1) ) */
} /* END: act Myinitbv */

/* ***************************************************************** */
/* Re-Initialisierungsfunktion der class BAV. Sie wird in aller      */
/* Laeufen NACH dem ersten Lauf immer in der ersten Periode aus -    */
/* gefuehrt.                                                         */
/* ***************************************************************** */
act Newinibv {
int i;                                 /* Wird nur AB dem 2. Lauf in */
if ( (rl >= 2) && ( period == 1) ) /* der 1. Periode ausgefuehrt */
 {
  for(i = 0 ; i < MAXSPARTEN ; i++ )
   {
    BAV[Ownnr()].DatenBAV.Pm[i] = 0.0;/* Minimalpraemie,Sparte   :{0}*/
    BAV[Ownnr()].DatenBAV.Wm[i] = 0.0;/* Maximalwerbung,Sparte   :{0}*/
    BAV[Ownnr()].DatenBAV.Dp[i] = 0.0;/* Durchschn.praemie,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Dw[i] = 0.0;/* Durchschn.werbung,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Mp[i] = 0.0;/* Marktfueh.praemie,Spart.:{0}*/
    BAV[Ownnr()].DatenBAV.Mw[i] = 0.0;/* Marktfueh.werbung,Spart.:{0}*/
   }
  for( i = 0  ; i < MAXRISKS  ; i++  )
   {
    BAV[Ownnr()].DatenBAV.Dg[i] = 0.0;/* Durchschnl. Versich.grad {0}*/
   }
  fprintf(runreport, "Newinibv:[%d,%d]\n",logtime,period );
 } /* END: if ( (rl >= 2) && ( period == 1) ) */
} /* END: act Newinibv */

/* ***************************************************************** */
/* act Frmdinf: Zentrale Berechnung der FREMDINFORMATIONEN           */
/* VUs: VR DUMPING: braucht Minimalpraemie in beiden Sparten in t-1  */
/*                          Maximalwerbung in beiden Sparten in t-1  */
/*         DURCHSCHNITT:    Durchschnittspraemie in b. Sparten in t-1*/
/*                          Durchschnittswerbung in b. Sparten in t-1*/
/*         ANGRIFF:         Praemie der VU mit den hoechsten Reserven*/
/*                          Werbung der VU ( = Marktfuehrer )        */
/* VNs: VR SUCHE:           Durchschnittl. Versichg.grad in Risiko i */
/*         BESTE INFOS.     Durchschhnittl. Versich.grad in Risiko i */
/* ***************************************************************** */
act Frmdinf {
int i, j;                      /* Schleifenzaehler                   */
float r;                       /* Hilfsvariable                      */
if ( period > 1 )              /* Durchschnittspraemie in Sparte 1   */
 {
  BAV[Ownnr()].DatenBAV.Dp[0] = 0.0;
  for( i = 1; i <= MAXVU ; i++)/* ACHTUNG: muss VOR der NEUBerechnung*/
   {                           /* von akvu passieren, sonst wird in  */
    BAV[Ownnr()].DatenBAV.Dp[0] =  /* Perioden mit Aktivierungsschock*/
    BAV[Ownnr()].DatenBAV.Dp[0] +  /* mit Praemien aus t-1 und der   */
    VU[i].DatenVU->Sp[1].l.Pr[(period-1)]; /* Versichereranzahl aus  */
   }                               /* t gerechnet !                  */
  if ( akvu != 0)              /* Division durch Null vermeiden...   */
   {
    BAV[Ownnr()].DatenBAV.Dp[0] = BAV[Ownnr()].DatenBAV.Dp[0] / akvu ;
   }
   else /* akvu == 0 */
    {
     BAV[Ownnr()].DatenBAV.Dp[0] = 0.0;
    }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
  {
  BAV[Ownnr()].DatenBAV.Dp[0] = 0.0; /* .. zur Vollstaendigkeit...   */
  }
if ( period > 1 )              /* Durchschnittspraemie in Sparte 2   */
 {
  BAV[Ownnr()].DatenBAV.Dp[1] = 0.0;
  for( i = 1; i <= MAXVU ; i++)/* ACHTUNG: muss VOR der NEUBerechnung*/
   {                           /* von akvu passieren, sonst wird in  */
    BAV[Ownnr()].DatenBAV.Dp[1] =  /* Perioden mit Aktivierungsschock*/
    BAV[Ownnr()].DatenBAV.Dp[1] +  /* mit Praemien aus t-1 und der   */
    VU[i].DatenVU->Sp[2].k.Pr[(period-1)]; /* Versichereranzahl aus  */
   }                               /* t gerechnet !                  */
  if ( akvu != 0)              /* Division durch Null vermeiden...   */
   {
    BAV[Ownnr()].DatenBAV.Dp[1] = BAV[Ownnr()].DatenBAV.Dp[1] / akvu ;
   }
   else /* akvu == 0 */
    {
     BAV[Ownnr()].DatenBAV.Dp[1] = 0.0;
    }
 } /* END: if ( period > 1 ) */
 else /* period = 0 */
  {
  BAV[Ownnr()].DatenBAV.Dp[1] = 0.0; /* .. zur Vollstaendigkeit...   */
  }
if ( period > 1 )              /* Durchschnittswerbung in Sparte 1   */
 {
  BAV[Ownnr()].DatenBAV.Dw[0] = 0.0;
  for( i = 1; i <= MAXVU ; i++)/* ACHTUNG: muss VOR der NEUBerechnung*/
   {                           /* von akvu passieren, sonst wird in  */
    BAV[Ownnr()].DatenBAV.Dw[0] =  /* Perioden mit Aktivierungsschock*/
    BAV[Ownnr()].DatenBAV.Dw[0] +  /* mit Werbung  aus t-1 und der   */
    VU[i].DatenVU->Sp[1].l.Wa[(period-1)]; /* Versichereranzahl aus  */
   }                               /* t gerechnet !                  */
  if ( akvu != 0)              /* Division durch Null vermeiden...   */
   {
    BAV[Ownnr()].DatenBAV.Dw[0] = BAV[Ownnr()].DatenBAV.Dw[0] / akvu ;
   }
   else /* akvu == 0 */
    {
     BAV[Ownnr()].DatenBAV.Dw[0] = 0.0;
    }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
  {
   BAV[Ownnr()].DatenBAV.Dw[0] = 0.0; /* .. zur Vollstaendigkeit...   */
  }
if ( period > 1 )               /* Durchschnittswerbung in Sparte 2   */
 {
  BAV[Ownnr()].DatenBAV.Dw[1] = 0.0;
  for( i = 1; i <= MAXVU ; i++)/* ACHTUNG: muss VOR der NEUBerechnung*/
   {                           /* von akvu passieren, sonst wird in  */
    BAV[Ownnr()].DatenBAV.Dw[1] =  /* Perioden mit Aktivierungsschock*/
    BAV[Ownnr()].DatenBAV.Dw[1] +  /* mit Werbung  aus t-1 und der   */
    VU[i].DatenVU->Sp[2].k.Wa[(period-1)]; /* Versichereranzahl aus  */
   }                               /* t gerechnet !                  */
  if ( akvu != 0)              /* Division durch Null vermeiden...   */
   {
    BAV[Ownnr()].DatenBAV.Dw[1] = BAV[Ownnr()].DatenBAV.Dw[1] / akvu ;
   }
   else /* akvu == 0 */
    {
     BAV[Ownnr()].DatenBAV.Dw[1] = 0.0;
    }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
  {
   BAV[Ownnr()].DatenBAV.Dw[1] = 0.0; /* .. zur Vollstaendigkeit...  */
  }
j = 0;                         /* Durchschnittlicher Vs.grad Risiko 1*/
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Dg[0] = 0.0;
  for(i = 1; i <= MAXVN ; i++ )/* Versicherungsstatus der Vorperiode */
   {                           /* auslesen und aufaddieren ...       */
    if ( VN[i].DatenVN->Rk[1].l.Vs[(period-1)] == 1 )
     {                          /* j ist die Anzahl der Versicherter,*/
      j++;                      /* die in der Vorperiode fremdver-   */
     }                          /* sichert waren ...                 */
    if ( akvn != 0 )            /* Division durch Null vermeiden ... */
     {
      BAV[Ownnr()].DatenBAV.Dg[0] = (float) j / (float) akvn ;
     }
     else /* akvn == 0 */
      {
       BAV[Ownnr()].DatenBAV.Dg[0] = 0.0;
      }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {                             /* In der 1. Periode ist der Versiche-*/
  BAV[Ownnr()].DatenBAV.Dg[0] = 0.0; /* rungsgrad auf Null gesetzt...*/
 }
j = 0;                         /* Durchschnittlicher Vs.grad Risiko 2*/
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Dg[1] = 0.0;
  for(i = 1; i <= MAXVN ; i++ )/* Versicherungsstatus der Vorperiode */
   {                           /* auslesen und aufaddieren ...       */
    if ( VN[i].DatenVN->Rk[2].k.Vs[(period-1)] == 1 )
     {                          /* j ist die Anzahl der Versicherter,*/
      j++;                      /* die in der Vorperiode fremdver-   */
     }                          /* sichert waren ...                 */
    if ( akvn != 0 )            /* Division durch Null vermeiden ... */
     {
      BAV[Ownnr()].DatenBAV.Dg[1] = (float) j / (float) akvn ;
     }
     else /* akvn == 0 */
      {
       BAV[Ownnr()].DatenBAV.Dg[1] = 0.0;
      }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {                             /* In der 1. Periode ist der Versiche-*/
  BAV[Ownnr()].DatenBAV.Dg[1] = 0.0; /* rungsgrad auf Null gesetzt...*/
 }
for ( i = 1; i <= MAXVU; i++) { aktiVU[i] = 0; } /* ..erst alle auf  */
for ( i = 1; i <= MAXVN; i++) { aktiVN[i] = 0; } /* Null setzen ...  */
akvu = 0;                      /* Berechnen von aktiVU[.], akvu      */
for( i = 1; i <= MAXVU ; i++)  /* aktiVU[i] zeigt, ob VU[i] in t ge- */
 {                             /* waehlt werden kann und wieviel VUs */
  if ( (VU[i].DatenVU->Ap * VU[i].DatenVU->Al[rl] ) != 0 )
   {                           /* in t aktiv sind ...                */
    aktiVU[i] = 1;             /* Das wird von den VNs gebraucht,    */
    akvu++;                    /* sie einen aktiven VU waehlen wollen*/
   }
  else
   {
    aktiVU[i] = 0;
   }
 }
akvn = 0;                      /* Berechnen von aktiVN[.], akvn      */
for( i = 1; i <= MAXVN ; i++)  /* Wird u.a. von VR Mark-Up III ge-   */
 {                             /* braucht...                         */
  if ( ( VN[i].DatenVN->Ap * VN[i].DatenVN->Al[rl] ) != 0 )
   {
    aktiVN[i] = 1;
    akvn++;
   }
  else
   {
    aktiVN[i] = 0;
   }
 }
if ( period > 1 ) /* Minimalpraemien berechnen: Sparte 1             */
 {                /* Wird von der VR DUMPING benutzt                 */
  BAV[Ownnr()].DatenBAV.Pm[0] = 1000.0; /* ... auf fiktives Maximum  */
  for( i = 1; i <= MAXVU ; i++ )        /* initialisieren...         */
   {
    if ( ( VU[i].DatenVU->Sp[1].l.Pr[(period-1)] <
          BAV[Ownnr()].DatenBAV.Pm[0]  )                 &&
         ( VU[i].DatenVU->Sp[1].l.Pr[(period-1)] > 0.0 ) )
     {
      BAV[Ownnr()].DatenBAV.Pm[0]=VU[i].DatenVU->Sp[1].l.Pr[(period-1)];
     }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {
  BAV[Ownnr()].DatenBAV.Pm[0] = 0.0;
 }
if ( period > 1 ) /* Minimalpraemien berechnen: Sparte 2             */
 {                /* Wird von der VR DUMPING benutzt                 */
  BAV[Ownnr()].DatenBAV.Pm[1] = 1000.0; /* ... auf fiktives Maximum  */
  for( i = 1; i <= MAXVU ; i++ )        /* initialisieren...         */
   {
    if ( ( VU[i].DatenVU->Sp[2].k.Pr[(period-1)] <
           BAV[Ownnr()].DatenBAV.Pm[1] )                &&
         ( VU[i].DatenVU->Sp[2].k.Pr[(period-1)] > 0.0 ) )
     {
      BAV[Ownnr()].DatenBAV.Pm[1]=VU[i].DatenVU->Sp[2].k.Pr[(period-1)];
     }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {
  BAV[Ownnr()].DatenBAV.Pm[1] = 0.0;
 }
if ( period > 1 ) /* Maximalwerbung berechnen: Sparte 1              */
 {
  BAV[Ownnr()].DatenBAV.Wm[0] = 0.0;
  for( i = 1; i <= MAXVU ; i++)
   {
    if ( VU[i].DatenVU->Sp[1].l.Wa[(period-1)] >
         BAV[Ownnr()].DatenBAV.Wm[0]            )
     {
      BAV[Ownnr()].DatenBAV.Wm[0]=VU[i].DatenVU->Sp[1].l.Wa[(period-1)];
     }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {
  BAV[Ownnr()].DatenBAV.Wm[0] = 0.0;
 }
if ( period > 1 ) /* Maximalwerbung berechnen: Sparte 2              */
 {
  BAV[Ownnr()].DatenBAV.Wm[1] = 0.0;
  for( i = 1; i <= MAXVU ; i++)
   {
    if ( VU[i].DatenVU->Sp[2].k.Wa[(period-1)] >
         BAV[Ownnr()].DatenBAV.Wm[1]            )
     {
      BAV[Ownnr()].DatenBAV.Wm[1]=VU[i].DatenVU->Sp[2].k.Wa[(period-1)];
     }
   }
 } /* END: if ( period > 1 ) */
 else /* period == 0 */
 {
  BAV[Ownnr()].DatenBAV.Wm[1] = 0.0;
 }
r = 0.0;                       /* Marktfuehrerpraemie Sparte 1       */
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Mp[0] = 0.0; /* Versicherer in Sparte 1 mit  */
  for( i = 1; i <= MAXVU ; i++)      /* den groessten Reserven in der*/
   {                                 /* Vorperiode finden ...        */
    if ( VU[i].DatenVU->Sp[1].l.Rs[(period-1)] > r  )
     {                               /* ... und merken ...           */
      r = VU[i].DatenVU->Sp[1].l.Rs[(period-1)];
      BAV[Ownnr()].DatenBAV.Mp[0]=VU[i].DatenVU->Sp[1].l.Pr[(period-1)];
     }
   }
 }
 else /* period == 1 */
 {
  BAV[Ownnr()].DatenBAV.Mp[0] = 0.0; /* ... zur Vollstaendigkeit...  */
 }
r = 0.0;                       /* Marktfuehrerpraemie Sparte 2       */
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Mp[1] = 0.0; /* Versicherer in Sparte 2 mit  */
  for( i = 1; i <= MAXVU ; i++)      /* den groessten Reserven in der*/
   {                                 /* Vorperiode finden ...        */
    if ( VU[i].DatenVU->Sp[2].k.Rs[(period-1)] > r  )
     {                               /* ... und merken ...           */
      r = VU[i].DatenVU->Sp[2].k.Rs[(period-1)];
      BAV[Ownnr()].DatenBAV.Mp[1]=VU[i].DatenVU->Sp[2].k.Pr[(period-1)];
     }
   }
 }
 else /* period == 1 */
 {
  BAV[Ownnr()].DatenBAV.Mp[1] = 0.0; /* ... zur Vollstaendigkeit...  */
 }
r = 0.0;                       /* Marktfuehrerwerbung Sparte 1       */
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Mw[0] = 0.0; /* Versicherer in Sparte 1 mit  */
  for( i = 1; i <= MAXVU ; i++)      /* den groessten Reserven in der*/
   {                                 /* Vorperiode finden ...        */
    if ( VU[i].DatenVU->Sp[1].l.Rs[(period-1)] > r  )
     {                               /* ... und merken ...           */
      r = VU[i].DatenVU->Sp[1].l.Rs[(period-1)];
      BAV[Ownnr()].DatenBAV.Mw[0]=VU[i].DatenVU->Sp[1].l.Wa[(period-1)];
     }
   }
 }
 else /* period == 1 */
 {
  BAV[Ownnr()].DatenBAV.Mw[0] = 0.0; /* ... zur Vollstaendigkeit...  */
 }
r = 0.0;                       /* Marktfuehrerwerbung Sparte 2       */
if ( period > 1 )
 {
  BAV[Ownnr()].DatenBAV.Mw[1] = 0.0; /* Versicherer in Sparte 2 mit  */
  for( i = 1; i <= MAXVU ; i++)      /* den groessten Reserven in der*/
   {                                 /* Vorperiode finden ...        */
    if ( VU[i].DatenVU->Sp[2].k.Rs[(period-1)] > r  )
     {                               /* ... und merken ...           */
      r = VU[i].DatenVU->Sp[2].k.Rs[(period-1)];
      BAV[Ownnr()].DatenBAV.Mw[1]=VU[i].DatenVU->Sp[2].k.Wa[(period-1)];
     }
   }
 }
 else /* period == 1 */
 {
  BAV[Ownnr()].DatenBAV.Mw[1] = 0.0; /* ... zur Vollstaendigkeit...  */
 }
 fprintf(runreport, "Frmdinf(%d,%d).akvu(%d),akvn(%d)\n",
                     logtime,period,akvu,akvn);
}/* END: act Frmdinf */

/* ***************************************************************** */
/* class BAV: ESL-act zur Sicherung der Simulationsdaten in exter-   */
/*            nen Files. Die Daten werden auf den Aggragatstufen     */
/*            I..IV in ACSII-Files geschrieben.                      */
/* ***************************************************************** */
act Agrsich {
int i,j,k;                                     /* Schleifenzaehler   */
file *t;         /* Es ist immer nur EINE Aggregatdatei offen ...    */
float pr1,wa1,rs1,sh1,pr2,wa2,rs2,sh2; /* Hilfsvariable fuer         */
int vn1, sa1, vn2, sa2;                /* Aggregatbildung            */
int vu1,vu2,a1[MAXVU+1],a2[MAXVU+1],l,m;
float vp1,vp2,ev1,ev2,vs1,vs2,vm;
for( i = 1 ; i <= MAXVU ; i++ )/* Aggregat: Versicherer: Stufe I ... */
 {                             /*         : Einzelsubjekt            */
  if ( agvu1[i] == 1 )         /* WENN Aggregat erzeugt werden soll..*/
   {                              /* WENN Datei agvu1nm[i] existiert:*/
    t = fopen(agvu1nm[i], "a+t"); /* im Textmodus geoeffnen, SONST   */
    if ( t != ( file *) 0 )       /* wird sie neu angelegen ...      */
     {
      if ( (rl == 1) && ( period == 1) ) /* ERSTE period, ERSTER */
       {                          /* Lauf: Dateikopf schreiben ...   */
        fprintf(t,"#t  ");
        fprintf(t," Pr1   Wa1    Rs1     Vn1 Sa1 Sh1   ");
        fprintf(t," Pr2   Wa2    Rs2     Vn2 Sa2 Sh2\n");
       } /* END: if ( (rl == 1) && ( period == 1) ) */
       fprintf(t,"%04d",(rl-1)*sl+period);
       fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f",
               VU[i].DatenVU->Sp[1].l.Pr[period],
               VU[i].DatenVU->Sp[1].l.Wa[period],
               VU[i].DatenVU->Sp[1].l.Rs[period],
               VU[i].DatenVU->Sp[1].l.Vn[period],
               VU[i].DatenVU->Sp[1].l.Sa[period],
               VU[i].DatenVU->Sp[1].l.Sh[period]
              );
       fprintf(t," %05.1f %05.1f %+09.1f %03d %03d %06.1f\n",
               VU[i].DatenVU->Sp[2].k.Pr[period],
               VU[i].DatenVU->Sp[2].k.Wa[period],
               VU[i].DatenVU->Sp[2].k.Rs[period],
               VU[i].DatenVU->Sp[2].k.Vn[period],
               VU[i].DatenVU->Sp[2].k.Sa[period],
               VU[i].DatenVU->Sp[2].k.Sh[period]
               );
       fclose(t);
     } /* END: if (t != ( file *) 0) */
     else /*  (t == ( file *) 0) */
      {
       fprintf(runreport, "Kann %12s nicht oeffnen\n", agvu1nm[i]);
      }
   } /* END: if ( agvu1[i] == 1 ) */
 } /* END: for( i = 1 ; i <= MAXVU ; i++ )  */

 pr1=0.0;wa1=0.0;rs1=0.0;sh1=0.0;pr2=0.0;wa2=0.0;rs2=0.0;sh2=0.0;
 vn1=0  ;sa1=0  ;vn2=0  ;sa2=0  ;
 for( j = 1; j < 10 ; j++ )         /* Aggregatberechnung : VU II    */
  {                                 /* ..ueber alle Verhaltenregeln..*/
   if ( agvu2[j] == 1 )             /* Wenn Aggregat erzeugt werden  */
    {                               /* soll ...                      */
     for( i = 1; i <= MAXVU ; i++ ) /* ... ueber alle VUs ...        */
      {                             /* Daten aller VUs mit gleicher  */
       if (( VU[i].DatenVU->Vr == j ) && ( aktiVU[i] == 1 ))
        {                           /* VR zusammenaddieren ....      */
         pr1 = pr1 + VU[i].DatenVU->Sp[1].l.Pr[period];
         wa1 = wa1 + VU[i].DatenVU->Sp[1].l.Wa[period];
         rs1 = rs1 + VU[i].DatenVU->Sp[1].l.Rs[period];
         vn1 = vn1 + VU[i].DatenVU->Sp[1].l.Vn[period];
         sa1 = sa1 + VU[i].DatenVU->Sp[1].l.Sa[period];
         sh1 = sh1 + VU[i].DatenVU->Sp[1].l.Sh[period];
         pr2 = pr2 + VU[i].DatenVU->Sp[2].k.Pr[period];
         wa2 = wa2 + VU[i].DatenVU->Sp[2].k.Wa[period];
         rs2 = rs2 + VU[i].DatenVU->Sp[2].k.Rs[period];
         vn2 = vn2 + VU[i].DatenVU->Sp[2].k.Vn[period];
         sa2 = sa2 + VU[i].DatenVU->Sp[2].k.Sa[period];
         sh2 = sh2 + VU[i].DatenVU->Sp[2].k.Sh[period];
        } /* END: (( VU[i].DatenVU->Vr == j ) && ( aktiVU[i] == 1 )) */
      } /* END: for( i = 1; i <= MAXVU ; i++ ) */
    if ( BAV[Ownnr()].DatenBAV.Vuag2[j] != 0 ) /* Division durch Null */
     {                                         /* vermeiden...        */
      k  = BAV[Ownnr()].DatenBAV.Vuag2[j];
      pr1=pr1/(float)k; wa1=wa1/(float)k; rs1=rs1/(float)k;
      vn1=vn1/k       ; sa1=sa1/k       ; sh1=sh1/(float)k;
      pr2=pr2/(float)k; wa2=wa2/(float)k; rs2=rs2/(float)k;
      vn2=vn2/k       ; sa2=sa2/k       ; sh2=sh2/(float)k;
     } /* END: if ( BAV[Ownnr()].DatenBAV.Vuag2[j] != 0 ) */
    t = fopen(agvu2nm[j], "a+t");      /* Aggregatdatei beschreiben   */
    if ( t != ( file *) 0 )
     {
      if ( (rl == 1) && ( period == 1) )  /* ERSTE period, ERSTER */
       {                           /* Lauf: Dateikopf schreiben ...   */
        fprintf(t,"#t  ");
        fprintf(t," Pr1   Wa1    Rs1     Vn1 Sa1 Sh1   ");
        fprintf(t," Pr2   Wa2    Rs2     Vn2 Sa2 Sh2\n");                           
       } /* END: if ( (rl == 1) && ( period == 1) ) */
       fprintf(t,"%04d",(rl-1)*sl+period);
       fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f",
                   pr1,   wa1,   rs1,   vn1, sa1, sh1 );
       fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f\n",
                   pr2,   wa2,   rs2,   vn2, sa2, sh2 );
       fclose(t);
     } /* END: if ( t != ( file *) 0 ) */
     else /* ( t == ( file *) 0 ) */
      {
       fprintf(runreport, "Kann %12s nicht oeffnen\n", agvu2nm[j]);
      } /* END: else,if ( t != ( file *) 0 ) */
    } /* END: if ( agvu2[j] == 1 ) */
  } /* END: for( j = 1; j <= 10 ; j++ ) */
 pr1=0.0;wa1=0.0;rs1=0.0;sh1=0.0;pr2=0.0;wa2=0.0;rs2=0.0;sh2=0.0;
 vn1=0  ;sa1=0  ;vn2=0  ;sa2=0  ;
 for( j = 1; j <= 3 ; j++ )         /* Aggregatberechnung : VU III   */
  {                                 /* ..alle Verhaltensregelklassen */
   if ( agvu3[j] == 1 )             /* Wenn Aggregat erzeugt werden  */
    {                               /* soll ...                      */
     for( i = 1; i <= MAXVU ; i++ ) /* ... ueber alle VUs ...        */
      {                             /* Daten aller VUs mit gleicher  */
       if (( VU[i].DatenVU->Vk == j ) && ( aktiVU[i] == 1 ))
        {                           /* VR zusammenaddieren ....      */
         pr1 = pr1 + VU[i].DatenVU->Sp[1].l.Pr[period];
         wa1 = wa1 + VU[i].DatenVU->Sp[1].l.Wa[period];
         rs1 = rs1 + VU[i].DatenVU->Sp[1].l.Rs[period];
         vn1 = vn1 + VU[i].DatenVU->Sp[1].l.Vn[period];
         sa1 = sa1 + VU[i].DatenVU->Sp[1].l.Sa[period];
         sh1 = sh1 + VU[i].DatenVU->Sp[1].l.Sh[period];
         pr2 = pr2 + VU[i].DatenVU->Sp[2].k.Pr[period];
         wa2 = wa2 + VU[i].DatenVU->Sp[2].k.Wa[period];
         rs2 = rs2 + VU[i].DatenVU->Sp[2].k.Rs[period];
         vn2 = vn2 + VU[i].DatenVU->Sp[2].k.Vn[period];
         sa2 = sa2 + VU[i].DatenVU->Sp[2].k.Sa[period];
         sh2 = sh2 + VU[i].DatenVU->Sp[2].k.Sh[period];
        } /* END: (( VU[i].DatenVU->Vr == j ) && ( aktiVU[i] == 1 )) */
      } /* END: for( i = 1; i <= MAXVU ; i++ ) */

    if ( BAV[Ownnr()].DatenBAV.Vuag3[j] != 0 ) /* Division durch Null */
     {                                         /* vermeiden...        */
      k  = BAV[Ownnr()].DatenBAV.Vuag3[j];
      pr1=pr1/(float)k; wa1=wa1/(float)k; rs1=rs1/(float)k;
      vn1=vn1/k       ; sa1=sa1/k       ; sh1=sh1/(float)k;
      pr2=pr2/(float)k; wa2=wa2/(float)k; rs2=rs2/(float)k;
      vn2=vn2/k       ; sa2=sa2/k       ; sh2=sh2/(float)k;
     } /* END: if ( BAV[Ownnr()].DatenBAV.Vuag3[j] != 0 ) */
    t = fopen(agvu3nm[j], "a+t");      /* Aggregatdatei beschreiben   */
    if ( t != ( file *) 0 )
     {
      if ( (rl == 1) && ( period == 1) )  /* ERSTE period, ERSTER */
       {                           /* Lauf: Dateikopf schreiben ...   */
        fprintf(t,"#t  ");
        fprintf(t," Pr1   Wa1    Rs1     Vn1 Sa1 Sh1   ");
        fprintf(t," Pr2   Wa2    Rs2     Vn2 Sa2 Sh2\n");   
       } /* END: if ( (rl == 1) && ( period == 1) ) */
       fprintf(t,"%04d",(rl-1)*sl+period);
       fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f",
                   pr1,   wa1,   rs1,   vn1, sa1, sh1 );
       fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f\n",
                   pr2,   wa2,   rs2,   vn2, sa2, sh2 );
      fclose(t);
     } /* END: if ( t != ( file *) 0 ) */
     else /* ( t == ( file *) 0 ) */
      {
       fprintf(runreport, "Kann %12s nicht oeffnen\n", agvu3nm[j]);
      } /* END: else,if ( t != ( file *) 0 ) */
    } /* END: if ( agvu3[j] == 1 ) */
  } /* END: for( j = 1; j <= 3 ; j++ ) */
 pr1=0.0;wa1=0.0;rs1=0.0;sh1=0.0;pr2=0.0;wa2=0.0;rs2=0.0;sh2=0.0;
 vn1=0  ;sa1=0  ;vn2=0  ;sa2=0  ;
 if ( agvu4[1] == 1 )             /* Aggregatberechnung: VU IV     */
  {
   for( i = 1; i <= MAXVU ; i++ ) /* ... ueber alle VUs ...        */
    {                             /* ... zusammenaddieren ....     */
     if ( aktiVU[i] == 1 )
      {
       pr1 = pr1 + VU[i].DatenVU->Sp[1].l.Pr[period];
       wa1 = wa1 + VU[i].DatenVU->Sp[1].l.Wa[period];
       rs1 = rs1 + VU[i].DatenVU->Sp[1].l.Rs[period];
       vn1 = vn1 + VU[i].DatenVU->Sp[1].l.Vn[period];
       sa1 = sa1 + VU[i].DatenVU->Sp[1].l.Sa[period];
       sh1 = sh1 + VU[i].DatenVU->Sp[1].l.Sh[period];
       pr2 = pr2 + VU[i].DatenVU->Sp[2].k.Pr[period];
       wa2 = wa2 + VU[i].DatenVU->Sp[2].k.Wa[period];
       rs2 = rs2 + VU[i].DatenVU->Sp[2].k.Rs[period];
       vn2 = vn2 + VU[i].DatenVU->Sp[2].k.Vn[period];
       sa2 = sa2 + VU[i].DatenVU->Sp[2].k.Sa[period];
       sh2 = sh2 + VU[i].DatenVU->Sp[2].k.Sh[period];
      } /* END: if ( aktiVU[i] == 1 ) */
    } /* END: for( i = 1; i <= MAXVU ; i++ ) */
  if ( akvu != 0 )                           /* Division durch Null */
   {                                         /* vermeiden...        */
    k  = akvu;
    pr1=pr1/(float)k; wa1=wa1/(float)k; rs1=rs1/(float)k;
    vn1=vn1/k       ; sa1=sa1/k       ; sh1=sh1/(float)k;
    pr2=pr2/(float)k; wa2=wa2/(float)k; rs2=rs2/(float)k;
    vn2=vn2/k       ; sa2=sa2/k       ; sh2=sh2/(float)k;
   } /* END: if ( akvu != 0 ) */
  t = fopen(agvu4nm[1], "a+t");      /* Aggregatdatei beschreiben   */
  if ( t != ( file *) 0 )
   {
    if ( (rl == 1) && ( period == 1) )  /* ERSTE period, ERSTER */
     {                           /* Lauf: Dateikopf schreiben ...   */
      fprintf(t,"#t  ");
      fprintf(t," Pr1   Wa1    Rs1     Vn1 Sa1 Sh1   ");
      fprintf(t," Pr2   Wa2    Rs2     Vn2 Sa2 Sh2\n");
     } /* END: if ( (rl == 1) && ( period == 1) ) */
     fprintf(t,"%04d",(rl-1)*sl+period);
     fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f",
                 pr1,   wa1,   rs1,   vn1, sa1, sh1 );
     fprintf(t," %05.1f %05.1f %+09.1f %02d %03d %06.1f\n",
                   pr2,   wa2,   rs2,   vn2, sa2, sh2 );
     fclose(t);
   } /* END: if ( t != ( file *) 0 ) */
   else /* ( t == ( file *) 0 ) */
    {
     fprintf(runreport, "Kann %12s nicht oeffnen\n", agvu4nm[1]);
    } /* END: else,if ( t != ( file *) 0 ) */
  } /* END: if ( agvu4[1] == 1 ) */
 for( i = 1 ; i <= MAXVN ; i++ )  /* Aggregatberechnung: VN  I       */
  {
  if ( agvn1[i] == 1 )            /*WENN Aggregat erzeugt werden soll*/
   {                              /* WENN Datei agvn1nm[i] existiert,*/
    t = fopen(agvn1nm[i], "a+t"); /* im Textmodus geoeffnen, SONST   */
    if ( t != ( file *) 0 )       /* wird sie neu angelegen...       */
     {
      if ( (rl == 1) && ( period == 1) ) /* ERSTE period, ERSTER */
       {                          /* Lauf: Dateikopf schreiben ...   */
        fprintf(t,"#t ");
        fprintf(t," Vu1 Vs1  Vp1  Ev1   Sh1  ");
        fprintf(t," Vu2 Vs2  Vp2  Ev2   Sh2    Vm\n");
       } /* END: if ( (rl == 1) && ( period == 1) ) */
       fprintf(t,"%04d",(rl-1)*sl+period);
       fprintf(t," %03d %03d %04.1f %05.1f %05.1f",
                  VN[i].DatenVN->Rk[1].l.Vu[period],
                  VN[i].DatenVN->Rk[1].l.Vs[period],
                  VN[i].DatenVN->Rk[1].l.Vp[period],
                  VN[i].DatenVN->Rk[1].l.Ev[period],
                  VN[i].DatenVN->Rk[1].l.Sh[period]
              );
       fprintf(t," %03d %03d %04.1f %05.1f %05.1f",
                  VN[i].DatenVN->Rk[2].k.Vu[period],
                  VN[i].DatenVN->Rk[2].k.Vs[period],
                  VN[i].DatenVN->Rk[2].k.Vp[period],
                  VN[i].DatenVN->Rk[2].k.Ev[period],
                  VN[i].DatenVN->Rk[2].k.Sh[period]
              );
       fprintf(t," %+09.1f\n", VN[i].DatenVN->Vm[period]);
       fclose(t);
     } /* END: ( t != ( file *) 0 ) */
     else /* ( t == ( file *) 0 ) */
     {
      fprintf(runreport, "Kann %12s nicht oeffnen\n", agvn1nm[i]);
     } /* END: else, if ( t != ( file *) 0 ) */
   } /* END: if ( agvn1[i] == 1 )*/
  } /* END: for( i = 1 ; i <= MAXVN ; i++ )*/

 vu1=0  ; vu2=0  ;   /* Haeufigster von diesem Aggregat gewaehltes VU*/
 vs1=0.0; vs2=0.0;   /* Durchschnittlicher Versich.grad d. Aggregats */
 vp1=0.0; vp2=0.0;   /* Durchschnittlich gezahlte Praemie d. Aggregts*/
 ev1=0.0; ev2=0.0;   /* Durchschnittlich eigenversicherter Schaden " */
 sh1=0.0; sh1=0.0;   /* Durchschnittlicher Schaden des Aggregats     */
 vm =0.0;            /* Durchschnittsvermoegen des Aggregats         */
 for( k = 1; k <= MAXVU; k ++) /* Haeufigkeitsverteilung der vom     */
  {                            /* Aggregat gewaehlten VU fuer beide  */
   a1[k] = 0;                  /* Risiken...                         */
   a2[k] = 0;
  }
 for( j = 1; j < 7 ; j++ )          /* Aggregatberechnung : VN II    */
  {                                 /* ..ueber alle Verhaltenregeln..*/
   if ( agvn2[j] == 1 )             /* Wenn Aggregat erzeugt werden  */
    {                               /* soll ...                      */
     for( i = 1; i <= MAXVN ; i++ ) /* ... ueber alle VNs ...        */
      {
       if (( VN[i].DatenVN->Vr == j ) && ( aktiVN[i] == 1 ))
        {
         l = VN[i].DatenVN->Rk[1].l.Vu[period]; /* Gewaehlten VU in  */
         if ( ( l >= 0) && ( l <= MAXVU))/* die Haeufigkeitstabelle  */
          {                              /* aufnehmen...             */
           a1[l]++;
          }
         vs1 = vs1 + (float) VN[i].DatenVN->Rk[1].l.Vs[period];
         vp1 = vp1 + VN[i].DatenVN->Rk[1].l.Vp[period];
         ev1 = ev1 + VN[i].DatenVN->Rk[1].l.Ev[period];
         sh1 = sh1 + VN[i].DatenVN->Rk[1].l.Sh[period];
         l = VN[i].DatenVN->Rk[2].k.Vu[period]; /* Gewaehlten VU in  */
         if ( ( l >= 0) && ( l <= MAXVU))/* die Haeufigkeitstabelle  */
          {                              /* aufnehmen...             */
           a2[l]++;
          }
         vs2 = vs2 + (float) VN[i].DatenVN->Rk[2].k.Vs[period];
         vp2 = vp2 + VN[i].DatenVN->Rk[2].k.Vp[period];
         ev2 = ev2 + VN[i].DatenVN->Rk[2].k.Ev[period];
         sh2 = sh2 + VN[i].DatenVN->Rk[2].k.Sh[period];
         vm  = vm  + VN[i].DatenVN->Vm[period];
        } /* END: if((VN[i].DatenVN->Vr==j)&&(aktiVN[i]==1))*/
      } /* END: for( i = 1; i <= MAXVN ; i++ ) */
    if ( BAV[Ownnr()].DatenBAV.Vnag2[j] != 0 )
     {
      l = 0;                        /* Maximum der Haeufigkeitstabelle*/
      for( k = 1; k <= MAXVU; k++)  /* des 1. Risikos finden ...      */
       {
        if ( a1[k] > l )
         {
          l   = a1[k];
          vu1 = k;
         }
       }
      l = 0;                        /* Maximum der Haeufigkeitstabelle*/
      for( k = 1; k <= MAXVU; k++)  /* des 2. Risikos finden ...      */
       {
        if ( a2[k] > l )
         {
          l   = a2[k];
          vu2 = k;
         }
       }
      m = BAV[Ownnr()].DatenBAV.Vnag2[j];
      if ( m != 0)
      {                             /* Division durch Null vermeiden  */
       vs1 = vs1/(float) m; vp1 = vp1/(float) m;
       ev1 = ev1/(float) m; sh1 = sh1/(float) m;
       vs2 = vs2/(float) m; vp2 = vp2/(float) m;
       ev2 = ev2/(float) m; sh2 = sh2/(float) m;
       vm  = vm/(float) m;
      }
     } /* END: BAV[Ownnr()].DatenBAV.Vnag2[j] != 0 )*/
    t = fopen(agvn2nm[j], "a+t");     /* Aggregatdatei beschreiben   */
    if ( t != ( file *) 0 )
    {
     if ( (rl == 1) && ( period == 1) )  /* ERSTE period, ERSTER */
      {                           /* Lauf: Dateikopf schreiben ...   */
       fprintf(t,"#t  ");
       fprintf(t," Vu1 Vs1  Vp1  Ev1   Sh1  ");
       fprintf(t," Vu2 Vs2  Vp2  Ev2   Sh2    Vm\n");
      } /* END: if ( (rl == 1) && ( period == 1) )*/
      fprintf(t,"%04d",(rl-1)*sl+period);
      fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                  vu1, vs1, vp1,   ev1,   sh1
             );
      fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                   vu2, vs2, vp2,   ev2,   sh2
             );
      fprintf(t," %+09.1f\n", vm);
      fclose(t);
    } /* END: if ( t != ( file *) 0 ) */
    else /* t == ( file *) 0 ) */
     {
      fprintf(runreport, "Kann %12s nicht oeffnen\n", agvn2nm[j]);
     }
   } /* END: if ( agvn2[j] == 1 )*/
  } /* END: for( j = 1; j < 7 ; j++ ) */
 vu1=0  ; vu2=0  ;   /* Haeufigster von diesem Aggregat gewaehltes VU*/
 vs1=0.0; vs2=0.0;   /* Durchschnittlicher Versich.grad d. Aggregats */
 vp1=0.0; vp2=0.0;   /* Durchschnittlich gezahlte Praemie d. Aggregts*/
 ev1=0.0; ev2=0.0;   /* Durchschnittlich eigenversicherter Schaden " */
 sh1=0.0; sh1=0.0;   /* Durchschnittlicher Schaden des Aggregats     */
 vm =0.0;            /* Durchschnittsvermoegen des Aggregats         */
 for( k = 1; k <= MAXVU; k ++) /* Haeufigkeitsverteilung der vom     */
  {                            /* Aggregat gewaehlten VU fuer beide  */
   a1[k] = 0;                  /* Risiken...                         */
   a2[k] = 0;
  }
 for( j = 1; j <= 3 ; j++ )         /* Aggregatberechnung : VN III   */
  {                                 /* ..ueber alle Verhaltenregeln..*/
   if ( agvn3[j] == 1 )             /* Wenn Aggregat erzeugt werden  */
    {                               /* soll ...                      */
     for( i = 1; i <= MAXVN ; i++ ) /* ... ueber alle VNs ...        */
      {
       if (( VN[i].DatenVN->Vk == j ) && ( aktiVN[i] == 1 ))
        {
         l = VN[i].DatenVN->Rk[1].l.Vu[period]; /* Gewaehlten VU in  */
         if ( ( l > 0) && ( l <= MAXVU))/* die Haeufigkeitstabelle  */
          {                              /* aufnehmen...             */
           a1[l]++;
          }
         vs1 = vs1 + (float) VN[i].DatenVN->Rk[1].l.Vs[period];
         vp1 = vp1 + VN[i].DatenVN->Rk[1].l.Vp[period];
         ev1 = ev1 + VN[i].DatenVN->Rk[1].l.Ev[period];
         sh1 = sh1 + VN[i].DatenVN->Rk[1].l.Sh[period];
         l = VN[i].DatenVN->Rk[2].k.Vu[period]; /* Gewaehlten VU in  */
         if ( ( l > 0) && ( l <= MAXVU))/* die Haeufigkeitstabelle  */
          {                              /* aufnehmen...             */
           a2[l]++;
          }
         vs2 = vs2 + (float) VN[i].DatenVN->Rk[2].k.Vs[period];
         vp2 = vp2 + VN[i].DatenVN->Rk[2].k.Vp[period];
         ev2 = ev2 + VN[i].DatenVN->Rk[2].k.Ev[period];
         sh2 = sh2 + VN[i].DatenVN->Rk[2].k.Sh[period];
         vm  = vm  + VN[i].DatenVN->Vm[period];
        } /* END: if((VN[i].DatenVN->Vk==j)&&(aktiVN[i]==1))*/
      } /* END: for( i = 1; i <= MAXVN ; i++ ) */

    if ( BAV[Ownnr()].DatenBAV.Vnag3[j] != 0 )
     {
      l = 0;                        /* Maximum der Haeufigkeitstabelle*/
      for( k = 1; k <= MAXVU; k++)  /* des 1. Risikos finden ...      */
       {
        if ( a1[k] > l )
         {
          l   = a1[k];
          vu1 = k;
         }
       }
      l = 0;                        /* Maximum der Haeufigkeitstabelle*/
      for( k = 1; k <= MAXVU; k++)  /* des 2. Risikos finden ...      */
       {
        if ( a2[k] > l )
         {
          l   = a2[k];
          vu2 = k;
         }
       }
      m = BAV[Ownnr()].DatenBAV.Vnag3[j];
      if ( m > 0 )                  /* Division durch Null vermeiden  */
      {
       vs1 = vs1/(float) m; vp1 = vp1/(float) m;
       ev1 = ev1/(float) m; sh1 = sh1/(float) m;
       vs2 = vs2/(float) m; vp2 = vp2/(float) m;
       ev2 = ev2/(float) m; sh2 = sh2/(float) m;
       vm  = vm/(float) m;
      }
     } /* END: BAV[Ownnr()].DatenBAV.Vnag3[j] != 0 )*/
    t = fopen(agvn3nm[j], "a+t");     /* Aggregatdatei beschreiben   */
    if ( t != ( file *) 0 )
    {
     if ( (rl == 1) && ( period == 1) )  /* ERSTE period, ERSTER */
      {                           /* Lauf: Dateikopf schreiben ...   */
       fprintf(t,"#t  ");
       fprintf(t," Vu1 Vs1  Vp1  Ev1   Sh1  ");
       fprintf(t," Vu2 Vs2  Vp2  Ev2   Sh2   Vm\n");
      } /* END: if ( (rl == 1) && ( period == 1) )*/
      fprintf(t,"%04d",(rl-1)*sl+period);
      fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                  vu1, vs1, vp1,   ev1,   sh1
               );
      fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                  vu2, vs2, vp2,   ev2,   sh2
             );
      fprintf(t," %+09.1f\n", vm);
      fclose(t);
    } /* END: if ( t != ( file *) 0 ) */
    else /* t == ( file *) 0 ) */
     {
      fprintf(runreport, "Kann %12s nicht oeffnen\n", agvn3nm[j]);
     }
   } /* END: if ( agvn3[j] == 1 )*/
  } /* END: for( j = 1; j <= 3 ; j++ ) */
 vu1=0  ; vu2=0  ;   /* Haeufigster von diesem Aggregat gewaehltes VU*/
 vs1=0.0; vs2=0.0;   /* Durchschnittlicher Versich.grad d. Aggregats */
 vp1=0.0; vp2=0.0;   /* Durchschnittlich gezahlte Praemie d. Aggregts*/
 ev1=0.0; ev2=0.0;   /* Durchschnittlich eigenversicherter Schaden " */
 sh1=0.0; sh1=0.0;   /* Durchschnittlicher Schaden des Aggregats     */
 vm =0.0;            /* Durchschnittsvermoegen des Aggregats         */
 for( k = 1; k <= MAXVU; k ++) /* Haeufigkeitsverteilung der vom     */
  {                            /* Aggregat gewaehlten VU fuer beide  */
   a1[k] = 0;                  /* Risiken...                         */
   a2[k] = 0;
  }                            /* Aggregatberechnung : VN IV         */
 if ( agvn4[1] == 1 )             /* Wenn Aggregat erzeugt werden    */
  {                               /* soll ...                        */
   for( i = 1; i <= MAXVN ; i++ ) /* ... ueber alle VNs ...          */
    {
     if ( aktiVN[i] == 1 )
      {
       l = VN[i].DatenVN->Rk[1].l.Vu[period];   /* Gewaehlten VU in  */
       if ( ( l > 0) && ( l <= MAXVU) )  /* die Haeufigkeitstabelle  */
        {                                /* aufnehmen...             */
         a1[l]++;
        }
       vs1 = vs1 + VN[i].DatenVN->Rk[1].l.Vs[period];
       vp1 = vp1 + VN[i].DatenVN->Rk[1].l.Vp[period];
       ev1 = ev1 + VN[i].DatenVN->Rk[1].l.Ev[period];
       sh1 = sh1 + VN[i].DatenVN->Rk[1].l.Sh[period];
       l = VN[i].DatenVN->Rk[2].k.Vu[period];   /* Gewaehlten VU in  */
       if ( ( l >= 0) && ( l <= MAXVU) ) /* die Haeufigkeitstabelle  */
        {                                /* aufnehmen...             */
         a2[l]++;
        }
       vs2 = vs2 + VN[i].DatenVN->Rk[2].k.Vs[period];
       vp2 = vp2 + VN[i].DatenVN->Rk[2].k.Vp[period];
       ev2 = ev2 + VN[i].DatenVN->Rk[2].k.Ev[period];
       sh2 = sh2 + VN[i].DatenVN->Rk[2].k.Sh[period];
       vm  = vm  + VN[i].DatenVN->Vm[period];
      } /* END: if( aktiVN[i]==1 )*/
    } /* END: for( i = 1; i <= MAXVN ; i++ ) */

  if ( akvn != 0 )
   {
    l = 0;                         /* Maximum der Haeufigkeitstabelle*/
    for( k = 1; k <= MAXVU; k++)   /* des 1. Risikos finden ...      */
     {
      if ( a1[k] > l )
       {
        l   = a1[k];
        vu1 = k;
       }
     }
    l = 0;                         /* Maximum der Haeufigkeitstabelle*/
    for( k = 1; k <= MAXVU; k++)   /* des 2. Risikos finden ...      */
     {
      if ( a2[k] > l )
       {
        l   = a2[k];
        vu2 = k;
       }
     }
    m = akvn;
    if ( akvn > 0 )
     {
      vs1 = vs1/(float) m; vp1 = vp1/(float) m;
      ev1 = ev1/(float) m; sh1 = sh1/(float) m;
      vs2 = vs2/(float) m; vp2 = vp2/(float) m;
      ev2 = ev2/(float) m; sh2 = sh2/(float) m;
      vm  = vm/(float) m;
     }
   } /* END: akvn != 0 */
  t = fopen(agvn4nm[1], "a+t");      /* Aggregatdatei beschreiben   */
  if ( t != ( file *) 0 )
  {
   if ( (rl == 1) && ( period == 1) )   /* ERSTE period, ERSTER */
    {                            /* Lauf: Dateikopf schreiben ...   */
     fprintf(t,"#t  ");
     fprintf(t," Vu1 Vs1  Vp1  Ev1   Sh1  ");
     fprintf(t," Vu2 Vs2  Vp2  Ev2   Sh2    Vm\n");
    } /* END: if ( (rl == 1) && ( period == 1) )*/
    fprintf(t,"%04d",(rl-1)*sl+period);
    fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                vu1, vs1, vp1,   ev1,   sh1
           );
    fprintf(t," %03d %1.2f %04.1f %05.1f %05.1f",
                vu2, vs2, vp2,   ev2,   sh2
           );
    fprintf(t," %+09.1f\n", vm);
    fclose(t);
  } /* END: if ( t != ( file *) 0 ) */
  else /* t == ( file *) 0 ) */
   {
    fprintf(runreport, "Kann %12s nicht oeffnen\n", agvn4nm[1]);
   }
 } /* END: ( agvn4[1] == 1 )*/
 fprintf(runreport, "Agrsich(%d,%d)\n", logtime,period);
 fprintf(runreport,"Vuag2[.]:{\n");
 for(i=1;i<=10;i++)
  {
   fprintf(runreport," %d ", BAV[Ownnr()].DatenBAV.Vuag2[i] );
  }
 fprintf(runreport,"}\n");
 fprintf(runreport,"Vuag3[.]:{\n");
 for(i=1;i<=3;i++)
  {
   fprintf(runreport," %d ", BAV[Ownnr()].DatenBAV.Vuag3[i] );
  }
 fprintf(runreport,"}\n");
 fprintf(runreport,"Vnag2[.]:{\n");
 for(i=1;i<=6;i++)
  {
   fprintf(runreport," %d ", BAV[Ownnr()].DatenBAV.Vnag2[i] );
  }
 fprintf(runreport,"}\n");
 fprintf(runreport,"Vnag3[.]:{\n");
 for(i=1;i<=3;i++)
  {
   fprintf(runreport," %d ", BAV[Ownnr()].DatenBAV.Vnag3[i] );
  }
 fprintf(runreport,"}\n");
 /* Alle Aggregatzaehler auf Null setzen fuer naechste Periode      */
 /* wieder auf Null setzen ...                                      */
 for( i = 0;  i <= MAXVU ; i++ ) { BAV[Ownnr()].DatenBAV.Vuag1[i] = 0;}
 for( i = 0;  i <=    10 ; i++ ) { BAV[Ownnr()].DatenBAV.Vuag2[i] = 0;}
 for( i = 0;  i <=     3 ; i++ ) { BAV[Ownnr()].DatenBAV.Vuag3[i] = 0;}
 for( i = 0;  i <= MAXVN ; i++ ) { BAV[Ownnr()].DatenBAV.Vnag1[i] = 0;}
 for( i = 0;  i <=     7 ; i++ ) { BAV[Ownnr()].DatenBAV.Vnag2[i] = 0;}
 for( i = 0;  i <=     3 ; i++ ) { BAV[Ownnr()].DatenBAV.Vnag3[i] = 0;}
} /* END: act Agrsich */

/* ***************************************************************** */
/* class VU: Definition der ESL-class VU und ihrer Verhaltensregeln. */
/*           Die ESL-Definitionen werden durch einen #include-Befehl */
/*           aus der Datei "imsvu.e" geladen.                        */
/* ***************************************************************** */
class VU {
           classVU *DatenVU;
         } subj[MAXVU]=
#include "imsvu.e"

/* ***************************************************************** */
/* class VU: Myinitvu            Initialisierungsfunktion            */
/*           Wird NUR in der ersten Periode des ERSTEN Simulations-  */
/*           laufs ausgefuehrt, DANACH in Periode 1 IMMER <Newinivu> */
/* ***************************************************************** */
act Myinitvu {
int i;                                           /* Schleifenzaehler */
gOwnnr   = Ownnr(); /* Sichern der globalen ESL-Steuervariable fuer  */
glogtime = logtime; /* die indirekten Aufrufe der Verhaltensregel-   */
gperiod  = period;  /* aktionen                                      */
if ( ( rl == 1) && ( load == 0 ) ) /* NUR im 1. Lauf wenn KEINE  */
 {                                   /* Konfig geladen ist...        */
  for( i = 2 ;i <= SIMLAENGE ; i++ )   /* Initialisierung der Sparten*/
  {                                         /* Sparte 1 ....         */
   VU[gOwnnr].DatenVU->Sp[1].l.Pr[i] = 0.0; /* Praemienvektor        */
   VU[gOwnnr].DatenVU->Sp[1].l.Wa[i] = 0.0; /* Werbeaufwandsvektor   */
   VU[gOwnnr].DatenVU->Sp[1].l.Rs[i] = 0.0; /* Reservenvektor        */
   VU[gOwnnr].DatenVU->Sp[1].l.Vn[i] = 0  ; /* Versichertenvektor    */
   VU[gOwnnr].DatenVU->Sp[1].l.Sa[i] = 0  ; /* Schadenanzahlvektor   */
   VU[gOwnnr].DatenVU->Sp[1].l.Sh[i] = 0.0; /* Schadensummenvektor   */
                                            /* Sparte 2 ....         */
   VU[gOwnnr].DatenVU->Sp[2].k.Pr[i] = 0.0; /* Praemienvektor        */
   VU[gOwnnr].DatenVU->Sp[2].k.Wa[i] = 0.0; /* Werbeaufwandsvektor   */
   VU[gOwnnr].DatenVU->Sp[2].k.Rs[i] = 0.0; /* Reservenvektor        */
   VU[gOwnnr].DatenVU->Sp[2].k.Vn[i] = 0  ; /* Versichertenvektor    */
   VU[gOwnnr].DatenVU->Sp[2].k.Sa[i] = 0  ; /* Schadenanzahlvektor   */
   VU[gOwnnr].DatenVU->Sp[2].k.Sh[i] = 0.0; /* Schadensummenvektor   */
  }
    /* VU[gOwnnr].DatenVU->Ac[1].lt=1;VU[gOwnnr].DatenVU->Ac[1].st=1;*/
    /* VU[gOwnnr].DatenVU->Vr = 1; VU[gOwnnr].DatenVU->Vk = 1;       */
 }                 /* ENDE:.. if ( ( rl == 1) && ( load == 0 ) ) */
  /*fprintf(runreport, "Myinitvu VU[%d] im Lauf [%d]\n", gOwnnr, rl);*/
}

/* ***************************************************************** */
/* class VU: Newinivu         Re-Initialisierungsfunktion            */
/*           Wird immer in der ersten Periode in alle  Simulations-  */
/*           laeufen NACH dem ersten Lauf durchgefuehrt              */
/* ***************************************************************** */
act Newinivu {
int i; /* Schleifenvariable */
gOwnnr   = Ownnr();
glogtime = logtime;
gperiod  = period; /* printf("Newinivu[%d](a)\n",gOwnnr); */
if( (rl >= 2) && (period == 1) )
 {
  for(i = 2;i <= SIMLAENGE ; i++ ) /* Re-Initialisierung der Sparten */
  {                                         /* Sparte 1 .....        */
   VU[gOwnnr].DatenVU->Sp[1].l.Pr[i] = 0.0; /* Praemienvektor        */
   VU[gOwnnr].DatenVU->Sp[1].l.Wa[i] = 0.0; /* Werbeaufwandsvektor   */
   VU[gOwnnr].DatenVU->Sp[1].l.Rs[i] = 0.0; /* Reservenvektor        */
   VU[gOwnnr].DatenVU->Sp[1].l.Vn[i] = 0  ; /* Versichertenvektor    */
   VU[gOwnnr].DatenVU->Sp[1].l.Sa[i] = 0  ; /* Schadenanzahlvektor   */
   VU[gOwnnr].DatenVU->Sp[1].l.Sh[i] = 0.0; /* Schadensummenvektor   */
                                            /* Sparte 2 ....         */
   VU[gOwnnr].DatenVU->Sp[2].k.Pr[i] = 0.0; /* Praemienvektor        */
   VU[gOwnnr].DatenVU->Sp[2].k.Wa[i] = 0.0; /* Werbeaufwandsvektor   */
   VU[gOwnnr].DatenVU->Sp[2].k.Rs[i] = 0.0; /* Reservenvektor        */
   VU[gOwnnr].DatenVU->Sp[2].k.Vn[i] = 0  ; /* Versichertenvektor    */
   VU[gOwnnr].DatenVU->Sp[2].k.Sa[i] = 0  ; /* Schadenanzahlvektor   */
   VU[gOwnnr].DatenVU->Sp[2].k.Sh[i] = 0.0; /* Schadensummenvektor   */
  }
  /* fprintf(runreport, "Newinivu[%d], Lauf:[%d]\n",gOwnnr, rl); */
 }
} /* END: act Newinivu*/

/* Leer Aktion:         wird von der Koordinationsfunktion benoetigt */
act Leer { fprintf(runreport,"VULeer, Logtime %2d\n",glogtime); }

/* ***************************************************************** */
/* class VU: PlanVU   Koordinationsfunktion der Verhaltensregeln.    */
/*           Sie nimmt dem Aufruf der Verhaltensregel vor, die dem   */
/*           VU zugeordnet ist. Kriterien: VR und logischer Zeitpunkt*/
/* ***************************************************************** */
act PlanVU {
int i;                                           /* Schleifenzaehler */
gOwnnr   = Ownnr();
glogtime = logtime;
gperiod  = period;
for( i=1; i <= MAXNLOG; i++)
 {
  if ( (VU[ gOwnnr ].DatenVU->Ac[i].st  != 0        ) &&
       (VU[ gOwnnr ].DatenVU->Ac[i].lt  == glogtime )
     )
   {
    (StratdVU[1].S[ VU[gOwnnr].DatenVU->Ac[i].st])();
   } /* END: if */
 } /*  END: for */
} /* END: act PlanVU */

/* ***************************************************************** */
/* class StratdVU: ESL-class zur Verwaltung der Verhaltensregeln der */
/*                 class VU. Wird von act <PlanVU> benoetigt, um aus */
/*                 Aktionsvektor die Verhaltensregel auszulesen      */
/* ***************************************************************** */
class StratdVU
 {
  pact S[MAXNLOG+1];
 } subj[1] =
 {
   val:   Leer, Vrvu01, Vrvu02, Vrvu03, Vrvu04, Vrvu05, Vrvu06,
                Vrvu07, Vrvu08, Vrvu09, Vrvu10

 };

/* Leer Aktion:         wird von der Koordinationsfunktion benoetigt */
act Leer { fprintf(runreport,"Leer-Act der class VU "); }
/* ***************************************************************** */
/* act Vrvu01: Versicherung:    Verhaltensregel: Zufall I            */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.1.                   */
/* ***************************************************************** */
act Vrvu01 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 * myrndf();
    pr2t1 = b0 * myrndf();
    wa1t1 = c0 * myrndf();
    wa2t1 = d0 * myrndf();
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 * myrndf();
    pr2t1 = b1 * myrndf();
    wa1t1 = c1 * myrndf();
    wa2t1 = d1 * myrndf();
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu01 */

/* ***************************************************************** */
/* act Vrvu02: Versicherung:    Verhaltensregel:  Zufall II          */
/*                                                                   */
/*                            vgl. Kapitel 3.3.1.1.                  */
/* ***************************************************************** */
act Vrvu02 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
  /* ** Verhaltensregel:                vgl. Kapitel:      ********* */
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 + b0 * normal();
    pr2t1 = c0 + d0 * normal();
    wa1t1 = e0 + f0 * normal();
    wa2t1 = g0 + h0 * normal();
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 + b1 * normal();
    pr2t1 = c1 + d1 * normal();
    wa1t1 = e1 + f1 * normal();
    wa2t1 = g1 + h1 * normal();
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu02 */

/* ***************************************************************** */
/* act Vrvu03: Versicherung:    Verhaltensregel:  Mark-Up I          */
/*                                                                   */
/*                           vgl. 3.3.1.2.                           */
/* ***************************************************************** */
act Vrvu03 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,r1,r2;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z  = BAV[1].DatenBAV.Zs[gperiod];
r1 = VU[gOwnnr].DatenVU->A1[1]; /* Anspruchsniveaus der Reserven: ...*/
r2 = VU[gOwnnr].DatenVU->A2[1];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    if ( rs1t0 <= r1  ) { pr1t1 = a0 * pr1t0; }
      else              { pr1t1 = b0 * pr1t0; }
    if ( rs2t0 <= r2  ) { pr2t1 = c0 * pr2t0; }
      else              { pr2t1 = d0 * pr2t0; }
    if ( rs1t0 <= r1  ) { wa1t1 = e0 * wa1t0; }
      else              { wa1t1 = f0 * wa1t0; }
    if ( rs2t0 <= r2  ) { wa2t1 = g0 * wa2t0; }
      else              { wa2t1 = h0 * wa2t0; }
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    if ( rs1t0 <= 0.0 ) { pr1t1 = a1 * pr1t0; }
      else              { pr1t1 = b1 * pr1t0; }
    if ( rs2t0 <= 0.0 ) { pr2t1 = c1 * pr2t0; }
      else              { pr2t1 = d1 * pr2t0; }
    if ( rs1t0 <= 0.0 ) { wa1t1 = e1 * wa1t0; }
      else              { wa1t1 = f1 * wa1t0; }
    if ( rs2t0 <= 0.0 ) { wa2t1 = g1 * wa2t0; }
      else              { wa2t1 = h1 * wa2t0; }
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu03 */

/* ***************************************************************** */
/* act Vrvu04: Versicherung:    Verhaltensregel: Mark-Up II          */
/*                                                                   */
/*                            vgl. Kapitel 3.3.1.2.                  */
/* ***************************************************************** */
act Vrvu04 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z;
int   vn1t0,sa1t0,vn2t0,sa2t0,vn1t02,vn2t02,nw1,nw2;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
if (gperiod > 2)
{
 vn1t02 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-2];
 vn2t02 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-2];
}
z   = BAV[1].DatenBAV.Zs[gperiod];
nw1 = (int) VU[gOwnnr].DatenVU->A1[2]; /* Anspruchsniveaus */
nw2 = (int) VU[gOwnnr].DatenVU->A2[2]; /* der Nettowechsler*/
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod < 3) /* Periode 1 und 2: Startwerte benutzen         */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode >= 3: Verhaltensregel anwenden */
   {
    if ((vn1t0-vn1t02) <= nw1) { pr1t1 = a0 * pr1t0; }
      else                     { pr1t1 = b0 * pr1t0; }
    if ((vn2t0-vn2t02) <= nw2) { pr2t1 = c0 * pr2t0; }
      else                     { pr2t1 = d0 * pr2t0; }
    if ((vn1t0-vn1t02) <= nw1) { wa1t1 = e0 * wa1t0; }
      else                     { wa1t1 = f0 * wa1t0; }
    if ((vn2t0-vn2t02) <= nw2) { wa2t1 = g0 * wa2t0; }
      else                     { wa2t1 = h0 * wa2t0; }
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod < 3) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode >= 3: Verhaltensregel anwenden */
   {
    if ((vn1t0-vn1t02) <= nw1) { pr1t1 = a1 * pr1t0; }
      else                     { pr1t1 = b1 * pr1t0; }
    if ((vn2t0-vn2t02) <= nw2) { pr2t1 = c1 * pr2t0; }
      else                     { pr2t1 = d1 * pr2t0; }
    if ((vn1t0-vn1t02) <= nw1) { wa1t1 = e1 * wa1t0; }
      else                     { wa1t1 = f1 * wa1t0; }
    if ((vn2t0-vn2t02) <= nw2) { wa2t1 = g1 * wa2t0; }
      else                     { wa2t1 = h1 * wa2t0; }
   }
  } /* END: else Aenderungsschock */
  /* fprintf(runreport,"VU[%3d] Wechsler(%d,%d) A.niveau:(%d,%d) \n",
           gOwnnr, vn1t0-vn1t02 , vn2t0-vn2t02 ,nw1,nw2 ); */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu04 */

/* ***************************************************************** */
/* act Vrvu05: Versicherung:    Verhaltensregel:  Mark-Up III        */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.2.                   */
/* ***************************************************************** */
act Vrvu05 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,m1,m2,m1a,m2a;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z  = BAV[1].DatenBAV.Zs[gperiod];
m1 = VU[gOwnnr].DatenVU->A1[3]; /* Anspruchsniveaus: Marktanteil     */
m2 = VU[gOwnnr].DatenVU->A2[3];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    if ( akvn != 0 ) /* Division durch Null vermeiden                */
            { m1a = ((float) vn1t0) / ((float) akvn ) ; }
      else  { m1a = 0.0 ; }
    if ( akvn != 0 ) /* Division durch Null vermeiden                */
            { m2a = ((float) vn2t0) / ((float) akvn ) ; }
      else  { m2a = 0.0 ; }
    if ( m1a <= m1 )           { pr1t1 = a0 * pr1t0; }
      else                     { pr1t1 = b0 * pr1t0; }
    if ( m2a <= m2 )           { pr2t1 = c0 * pr2t0; }
      else                     { pr2t1 = d0 * pr2t0; }
    if ( m1a <= m1 )           { wa1t1 = e0 * wa1t0; }
      else                     { wa1t1 = f0 * wa1t0; }
    if ( m2a <= m2 )           { wa2t1 = g0 * wa2t0; }
      else                     { wa2t1 = h0 * wa2t0; }
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    if ( akvn != 0 ) /* Division durch Null vermeiden                */
            { m1a = ((float) vn1t0) / ((float) akvn ) ; }
      else  { m1a = 0.0 ; }
    if ( akvn != 0 ) /* Division durch Null vermeiden                */
            { m2a = ((float) vn2t0) / ((float) akvn ) ; }
      else  { m2a = 0.0 ; }
    if ( m1a <= m1 )           { pr1t1 = a1 * pr1t0; }
      else                     { pr1t1 = b1 * pr1t0; }
    if ( m2a <= m2 )           { pr2t1 = c1 * pr2t0; }
      else                     { pr2t1 = d1 * pr2t0; }
    if ( m1a <= m1 )           { wa1t1 = e1 * wa1t0; }
      else                     { wa1t1 = f1 * wa1t0; }
    if ( m2a <= m2 )           { wa2t1 = g1 * wa2t0; }
      else                     { wa2t1 = h1 * wa2t0; }
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu05 */

/* ***************************************************************** */
/* act Vrvu06: Versicherung:    Verhaltensregel: Erwartungsschaden   */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.2.                   */
/* ***************************************************************** */
act Vrvu06 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,s1,s2;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden                     */
   {
    if ( sa1t0 != 0 ) /* Division durch Null vermeiden               */
      { s1 = (sh1t0 / ((float) sa1t0)); }
     else
      { s1 = 0.0; }
    if ( sa2t0 != 0 ) /* Division durch Null vermeiden               */
     { s2 = (sh2t0 / ((float) sa2t0));  }
     else
      { s2 = 0.0; }
    if ( pr1t0 <= s1 )         { pr1t1 = a0 * pr1t0; }
      else                     { pr1t1 = b0 * pr1t0; }
    if ( pr2t0 <= s2 )         { pr2t1 = c0 * pr2t0; }
      else                     { pr2t1 = d0 * pr2t0; }
    if ( pr1t0 <= s1 )         { wa1t1 = e0 * wa1t0; }
      else                     { wa1t1 = f0 * wa1t0; }
    if ( pr2t0 <= s2 )         { wa2t1 = g0 * wa2t0; }
      else                     { wa2t1 = h0 * wa2t0; }
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    if ( sa1t0 != 0 ) /* Division durch Null vermeiden               */
      { s1 = (sh1t0 / ((float) sa1t0)); }
     else
      { s1 = 0.0; }
    if ( sa2t0 != 0 ) /* Division durch Null vermeiden               */
      { s2 = (sh2t0 / ((float) sa2t0));  }
     else
      { s2 = 0.0; }
    if ( pr1t0 <= s1 )         { pr1t1 = a1 * pr1t0; }
      else                     { pr1t1 = b1 * pr1t0; }
    if ( pr2t0 <= s2 )         { pr2t1 = c1 * pr2t0; }
      else                     { pr2t1 = d1 * pr2t0; }
    if ( pr1t0 <= s1 )         { wa1t1 = e1 * wa1t0; }
      else                     { wa1t1 = f1 * wa1t0; }
    if ( pr2t0 <= s2 )         { wa2t1 = g1 * wa2t0; }
      else                     { wa2t1 = h1 * wa2t0; }
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu06 */

/* ***************************************************************** */
/* act Vrvu07: Versicherung:    Verhaltensregel:  DUMPING            */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.3.                   */
/* ***************************************************************** */
act Vrvu07 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,pr1fi,wa1fi,pr2fi,wa2fi;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1]; /* Fremdinform. */
 pr1fi =  BAV[1].DatenBAV.Pm[0]; /* Kleinste Praemie in t-1, Sparte 1*/
 wa1fi =  BAV[1].DatenBAV.Wm[0]; /* Groesste Werbung in t-1, "       */
 pr2fi =  BAV[1].DatenBAV.Pm[1]; /* Kleinste Praemie in t-1, Sparte 2*/
 wa2fi =  BAV[1].DatenBAV.Wm[1]; /* Groesste Werbung in t-1, "       */
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 + b0 * pr1fi;
    pr2t1 = c0 + d0 * pr2fi;
    wa1t1 = e0 + f0 * wa1fi;
    wa2t1 = g0 + h0 * wa2fi;
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 + b1 * pr1fi;
    pr2t1 = c1 + d1 * pr2fi;
    wa1t1 = e1 + f1 * wa1fi;
    wa2t1 = g1 + h1 * wa2fi;
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu07 */

/* ***************************************************************** */
/* act Vrvu08: Versicherung:    Verhaltensregel:  DURCHSCHNITT       */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.3.                   */
/* ***************************************************************** */
act Vrvu08 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,pr1fi,wa1fi,pr2fi,wa2fi;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1]; /* Fremdinform. */
 pr1fi =  BAV[1].DatenBAV.Dp[0]; /* Durchschnittspraemie in Sparte 1 */
 wa1fi =  BAV[1].DatenBAV.Dw[0]; /* Durchschnittswerbung in Sparte 1 */
 pr2fi =  BAV[1].DatenBAV.Dp[1]; /* Durchschnittspraemie in Sparte 2 */
 wa2fi =  BAV[1].DatenBAV.Dw[1]; /* Durchschnittswerbung in Sparte 2 */
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 + b0 * pr1fi;
    pr2t1 = c0 + d0 * pr2fi;
    wa1t1 = e0 + f0 * wa1fi;
    wa2t1 = g0 + h0 * wa2fi;
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 + b1 * pr1fi;
    pr2t1 = c1 + d1 * pr2fi;
    wa1t1 = e1 + f1 * wa1fi;
    wa2t1 = g1 + h1 * wa2fi;
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu08 */

/* ***************************************************************** */
/* act Vrvu09: Versicherung:    Verhaltensregel:  ANGRIFF            */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.3.                   */
/* ***************************************************************** */
act Vrvu09 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z,pr1fi,wa1fi,pr2fi,wa2fi;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1]; /* Fremdinform. */
 pr1fi =  BAV[1].DatenBAV.Mp[0]; /* Marktfuehrerpraemie in Sparte 1  */
 wa1fi =  BAV[1].DatenBAV.Mw[0]; /* Marktfuehrerwerbung in Sparte 1  */
 pr2fi =  BAV[1].DatenBAV.Mp[1]; /* Marktfuehrerpraemie in Sparte 2  */
 wa2fi =  BAV[1].DatenBAV.Mw[1]; /* Marktfuehrerwerbung in Sparte 2  */
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 + b0 * pr1fi;
    pr2t1 = c0 + d0 * pr2fi;
    wa1t1 = e0 + f0 * wa1fi;
    wa2t1 = g0 + h0 * wa2fi;
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 + b1 * pr1fi;
    pr2t1 = c1 + d1 * pr2fi;
    wa1t1 = e1 + f1 * wa1fi;
    wa2t1 = g1 + h1 * wa2fi;
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
} /* END: Vrvu09 */

/* ***************************************************************** */
/* act Vrvu10: Versicherung:    Verhaltensregel:  frei definierbar   */
/*                                                                   */
/*                           vgl. Kapitel 3.3.1.3.                   */
/* ***************************************************************** */
act Vrvu10 {             /* Vereinbarung der Hilfsvariablen          */
float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,pr1t0,pr1t1,
      wa1t0,wa1t1,rs1t0,rs1t1,sh1t0,pr2t0,pr2t1,wa2t0,wa2t1,rs2t0,
      rs2t1,sh2t0,z;
int   vn1t0,sa1t0,vn2t0,sa2t0;
/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen          */
if (gperiod > 1)
{                          /* Der Parametervektor der VR             */
 a0 = VU[gOwnnr].DatenVU->Pv[0 ]; a1 = VU[gOwnnr].DatenVU->Pv[1 ];
 b0 = VU[gOwnnr].DatenVU->Pv[2 ]; b1 = VU[gOwnnr].DatenVU->Pv[3 ];
 c0 = VU[gOwnnr].DatenVU->Pv[4 ]; c1 = VU[gOwnnr].DatenVU->Pv[5 ];
 d0 = VU[gOwnnr].DatenVU->Pv[6 ]; d1 = VU[gOwnnr].DatenVU->Pv[7 ];
 e0 = VU[gOwnnr].DatenVU->Pv[8 ]; e1 = VU[gOwnnr].DatenVU->Pv[9 ];
 f0 = VU[gOwnnr].DatenVU->Pv[10]; f1 = VU[gOwnnr].DatenVU->Pv[11];
 g0 = VU[gOwnnr].DatenVU->Pv[12]; g1 = VU[gOwnnr].DatenVU->Pv[13];
 h0 = VU[gOwnnr].DatenVU->Pv[14]; h1 = VU[gOwnnr].DatenVU->Pv[15];
 pr1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod-1]; /* Sparte 1     */
 wa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod-1];
 rs1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod-1];
 vn1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Vn[gperiod-1];
 sa1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sa[gperiod-1];
 sh1t0 =  VU[gOwnnr].DatenVU->Sp[1].l.Sh[gperiod-1];
 pr2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod-1]; /* Sparte 2     */
 wa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod-1];
 rs2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod-1];
 vn2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Vn[gperiod-1];
 sa2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sa[gperiod-1];
 sh2t0 =  VU[gOwnnr].DatenVU->Sp[2].k.Sh[gperiod-1];
}
z = BAV[1].DatenBAV.Zs[gperiod];
if(gperiod>=((VU[gOwnnr].DatenVU->Ap) * (VU[gOwnnr].DatenVU->Al[rl])))
 {
  /* ***************** Verwaltungsroutinen ************************* */
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vuag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vuag2[ VU[gOwnnr].DatenVU->Vr ]++;
  BAV[1].DatenBAV.Vuag3[ VU[gOwnnr].DatenVU->Vk ]++;
  /* Reserven in beiden Sparten fuer eine Periode verzinsen: ....    */
  rs1t1 = ( 1 + z ) * rs1t0;
  rs2t1 = ( 1 + z ) * rs2t0;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {/* KEIN Aenderungsschock */
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a0 + b0 * pr1t1; /* HIER KOENNEN EIGENE VERHALTENSREGELN */
    pr2t1 = c0 + d0 * pr2t1; /* EINGESETZT WERDEN                    */
    wa1t1 = e0 + f0 * wa1t1;
    wa2t1 = g0 + h0 * wa2t1;
   }
  } /* END !(BAV[1].Daten.As[ ... */
 else /* Aenderungsschock */
  {
   if ( gperiod == 1) /* Erste Periode: Startwerte benutzen */
   {
    pr1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Pr[1];
    pr2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Pr[1];
    wa1t1 = VU[gOwnnr].DatenVU->Sp[1].l.Wa[1];
    wa2t1 = VU[gOwnnr].DatenVU->Sp[2].k.Wa[1];
   }
   else /* Periode > 1: Verhaltensregel anwenden */
   {
    pr1t1 = a1 + b1 * pr1t1; /* HIER KOENNEN EIGENE VERHALTENSREGELN */
    pr2t1 = c1 + d1 * pr2t1; /* EINGESETZT WERDEN                    */
    wa1t1 = e1 + f1 * wa1t1;
    wa2t1 = g1 + h1 * wa2t1;
   }
  } /* END: else Aenderungsschock */
 } /* END: IF (gperiod>=... */
 /* KURZE VR-Variable wieder in LANGE IMS-Variable speichern         */
 VU[gOwnnr].DatenVU->Sp[1].l.Pr[gperiod] = pr1t1; /* Zielgroessen in */
 VU[gOwnnr].DatenVU->Sp[1].l.Wa[gperiod] = wa1t1; /* die Vektoren    */
 VU[gOwnnr].DatenVU->Sp[2].k.Pr[gperiod] = pr2t1; /* zurueckspeichern*/
 VU[gOwnnr].DatenVU->Sp[2].k.Wa[gperiod] = wa2t1;
 VU[gOwnnr].DatenVU->Sp[1].l.Rs[gperiod] = rs1t1; /* Ergebnisgroessen*/
 VU[gOwnnr].DatenVU->Sp[2].k.Rs[gperiod] = rs2t1; /* zurueckspeichern*/
 /* fprintf(runreport,"[%d,%d] %3.1f %3.1f %3.1f %3.1f %4.1f %4.1f\n",
         gOwnnr,gperiod,pr1t1,wa1t1,pr2t1,wa2t1,rs1t1,rs2t1); */
} /* END: Vrvu10 */

/* ***************************************************************** */
/* class VN: Definition der ESL-class VU und ihrer Verhaltensregeln  */
/*           Die ESL-Definitionen werden durch einen #include-Befehl */
/*           aus der Datei "imsvn.e" geladen                         */
/* ***************************************************************** */
class VN {
          classVN *DatenVN;
         } subj[MAXVN]=
#include "imsvn.e"

/* ***************************************************************** */
/* class VN: Initialisierungaktion der class VN. Hier werden die     */
/*           Subjekte der Klasse Versicherungsnehmer in der ERSTEN   */
/*           Periode des ERSTEN Laufes initialisiert                 */
/* ***************************************************************** */
act Myinitvn {
 int i;                                  /*         Schleifenzaehler */
 gOwnnr   = Ownnr();                     /* Globale ESL-Vars fuer in-*/
 gperiod  = period;                      /* direkte act-Aufrufe spei-*/
 glogtime = logtime;                     /* chern                    */
 if ( ( rl == 1 ) && ( load == 0 ) ) /* NUR im 1. Lauf, wenn KEI-*/
  {                                      /* NE Konfig geladen ist... */
   for( i = 2; i<= SIMLAENGE; i++ )
    {                                    /* Gesamtvermoegensvektor   */
     VN[gOwnnr].DatenVN->Vm[i] = 0.0;    /* auf {0} initialisieren   */
    }
   for ( i = 2; i <= SIMLAENGE; i++ )
    {                                    /* Risiko 1:                */
     VN[gOwnnr].DatenVN->Rk[1].l.Vu[i]=0;/* Anbieternummer = {0}     */
     VN[gOwnnr].DatenVN->Rk[1].l.Vs[i]=0;/* Versicherungsstatus = {0}*/
     VN[gOwnnr].DatenVN->Rk[1].l.Vp[i]=0.0;/*Gezahlte Praemie = {0}  */
     VN[gOwnnr].DatenVN->Rk[1].l.Ev[i]=0.0;/*Eigenversicherte S. ={0}*/
     VN[gOwnnr].DatenVN->Rk[1].l.Sw[i]=myrndf();/*Schadenws.=Zufall()*/
     VN[gOwnnr].DatenVN->Rk[1].l.Sh[i]=0.0;/*Schadenhoehe = {0}      */
                                         /* Risiko 2:                */
     VN[gOwnnr].DatenVN->Rk[2].k.Vu[i]=0;/* Anbieternummer = {0}     */
     VN[gOwnnr].DatenVN->Rk[2].k.Vs[i]=0;/* Versicherungsstatus = {0}*/
     VN[gOwnnr].DatenVN->Rk[2].k.Vp[i]=0.0;/*Gezahlte Praemie = {0}  */
     VN[gOwnnr].DatenVN->Rk[2].k.Ev[i]=0.0;/*Eigenversicherte S. ={0}*/
     VN[gOwnnr].DatenVN->Rk[2].k.Sw[i]=myrndf();/*Schadenws.=Zufall()*/
     VN[gOwnnr].DatenVN->Rk[2].k.Sh[i]=0.0;/*Schadenhoehe = {0}      */
    }
 }                   /* END: if ( ( rl == 1 ) && ( load == 0 ) )     */
 /* fprintf(runreport,"Myinitvn[%d] im Lauf[%d]\n", gOwnnr,rl);      */
} /* END: act Myinitvn */

/* ***************************************************************** */
/* class VN: Re-Initialisierungsfunktion der class VN. Jeder VN wird */
/*           vor allen Lauefen NACH dem ersten Lauf neu initiali-    */
/*           siert.                                                  */
/* ***************************************************************** */
act Newinivn {
int i;                                          /* Schleifenvariable */
gOwnnr   = Ownnr();
gperiod  = period;
glogtime = logtime;
if ( (rl >= 2) && (period == 1) )        /* Nur AB dem 2. Lauf immer */
 {                                       /* in der ersten Periode... */
  for( i = 2; i<= SIMLAENGE; i++ )
   {                                     /* Gesamtvermoegensvektor   */
    VN[gOwnnr].DatenVN->Vm[i] = 0.0;     /* auf {0} initialisieren   */
   }
  for ( i = 2; i <= SIMLAENGE; i++ )/* Re-Initialisierung der Risiken*/
   {                                     /* Risiko 1:                */
    VN[gOwnnr].DatenVN->Rk[1].l.Vu[i]=0; /* Anbieternummer = {0}     */
    VN[gOwnnr].DatenVN->Rk[1].l.Vs[i]=0; /* Versicherungsstatus = {0}*/
    VN[gOwnnr].DatenVN->Rk[1].l.Vp[i]=0.0;/* Gezahlte Praemie = {0}  */
    VN[gOwnnr].DatenVN->Rk[1].l.Ev[i]=0.0;/* Eigenversicherte S. ={0}*/
    VN[gOwnnr].DatenVN->Rk[1].l.Sw[i]=myrndf();/* Schadenws.=Zufall()*/
    VN[gOwnnr].DatenVN->Rk[1].l.Sh[i]=0.0;/* Schadenhoehe = {0}      */
                                         /* Risiko 2:                */
    VN[gOwnnr].DatenVN->Rk[2].k.Vu[i]=0; /* Anbieternummer = {0}     */
    VN[gOwnnr].DatenVN->Rk[2].k.Vs[i]=0; /* Versicherungsstatus = {0}*/
    VN[gOwnnr].DatenVN->Rk[2].k.Vp[i]=0.0;/* Gezahlte Praemie = {0}  */
    VN[gOwnnr].DatenVN->Rk[2].k.Ev[i]=0.0;/* Eigenversicherte S. ={0}*/
    VN[gOwnnr].DatenVN->Rk[2].k.Sw[i]=myrndf();/* Schadenws.=Zufall()*/
    VN[gOwnnr].DatenVN->Rk[2].k.Sh[i]=0.0;/* Schadenhoehe = {0}      */
   }
   /* fprintf(runreport,"Newinivn[%d] im Lauf[%d]\n",gOwnnr,rl);     */
 }                     /* END: if ( (rl >= 2) && (period == 1) )     */
} /* END: Newinivn */

/* ***************************************************************** */
/* class VN: PlanVN   Koordinationsfunktion der Verhaltensregeln.    */
/*           Sie nimmt dem Aufruf der Verhaltensregel vor, die dem   */
/*           VN zugeordnet ist. Kriterien: VR und logischer Zeitpunkt*/
/* ***************************************************************** */
act PlanVN  {
int i;                                           /* Schleifenzaehler */
gOwnnr   = Ownnr();             /* Ueber alle logischen Zeitpunkt    */
gperiod  = period;              /* wird geprueft, ob der VN dafuer in*/
glogtime = logtime;             /* seinem Aktionsvektor eine VR vor- */
for( i = 1; i <= MAXNLOG; i++ ) /* gesehen hat; dann wird diese VR   */
 {                              /* INDIREKT aufgerufen.              */
  if ( ( VN[ gOwnnr ].DatenVN->Ac[i].st != 0        ) &&
       ( VN[ gOwnnr ].DatenVN->Ac[i].lt == glogtime )
     )
   {
    (StratdVN[1].S[ VN[ gOwnnr ].DatenVN->Ac[i].st  ] )(); /* AUFRUF!*/
   } /* END: if */
 } /* END: for */
} /* END: act PlanVN */

/* ***************************************************************** */
/* class StratdVN: ESL-class zur Verwaltung der Verhaltensregeln der */
/*                 class VN. Wird von act <PlanVN> benoetigt, um aus */
/*                 Aktionsvektor die Verhaltensregel auszulesen      */
/* ***************************************************************** */
class StratdVN
{
 pact S[ MAXNLOG+1 ];
} subj[1] =
{
 val: Leer, Vrvn01, Vrvn02, Vrvn03, Vrvn04, Vrvn05, Vrvn06, Vrvn07
};

act Leer { fprintf(runreport,"VNLeer[%d](%2d)\n",gOwnnr, glogtime); }
/* ***************************************************************** */
/*            Die Verhaltensregeln der Versicherungsnehmer           */
/* ***************************************************************** */
/* ***************************************************************** */
/* act: Vrvn01:  Versicherungsnehmer   Verhaltensregel:   Zufall I   */
/*                                                                   */
/*                            vgl. Kapitel 3.3.2.1                   */
/* ***************************************************************** */
act Vrvn01 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,pf1[MAXVU+1],pf2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1;
int vr1,vr2,r1,r2;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1 = 0; r2 = 0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = 1;                                     /* Pflichtversiche-*/
     vr2 = 1;                                     /* rund waehlen    */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 1 aus den in der Periode ak-   */
       r1 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r1 < 1 ) || ( r1 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r1] == 0  ); /* iode neu bestimmt !!           */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 2 aus den in der Periode ak-   */
       r2 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r2 < 1 ) || ( r2 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r2] == 0  ); /* iode neu bestimmt !!           */
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = 1;                                     /* Pflichtversiche-*/
     vr2 = 1;                                     /* rund waehlen    */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 1 aus den in der Periode ak-   */
       r1 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r1 < 1 ) || ( r1 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r1] == 0  ); /* iode neu bestimmt !!           */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 2 aus den in der Periode ak-   */
       r2 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r2 < 1 ) || ( r2 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r2] == 0  ); /* iode neu bestimmt !!           */
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Falls EigemVS,ist*/
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   ;    /* Vp[] = 0.0 ini-  */
                                                 /* tialisiert       */
   /* Bei VR: SUCHE hier auch die Informationskosten addieren        */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn01      */

/* ***************************************************************** */
/* act: Vrvn02:  Versicherungsnehmer   Verhaltensregel: Zufall II    */
/*                                                                   */
/*                            vgl. Kapitel 3.3.2.1                   */
/* ***************************************************************** */
act Vrvn02 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,pf1[MAXVU+1],pf2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1;
int vr1,vr2,r1,r2;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1=0; r2=0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = ( e0 <= myrndf() );          /* Versicherungsstatus fuer  */
     vr2 = ( f0 <= myrndf() );          /* beide Risiken bestimmen   */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 1 aus den in der Periode ak-   */
       r1 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r1 < 1 ) || ( r1 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r1] == 0  ); /* iode neu bestimmt !!           */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 2 aus den in der Periode ak-   */
       r2 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r2 < 1 ) || ( r2 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r2] == 0  ); /* iode neu bestimmt !!           */
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = ( e1 <= myrndf() );          /* Versicherungsstatus fuer  */
     vr2 = ( f1 <= myrndf() );          /* beide Risiken bestimmen   */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 1 aus den in der Periode ak-   */
       r1 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r1 < 1 ) || ( r1 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r1] == 0  ); /* iode neu bestimmt !!           */
     do {                          /* Waehle Versicherer fuer Risiko */
      do {                         /* 2 aus den in der Periode ak-   */
       r2 = ( myrnd() % akvu ) + 1;/* tiven VUs aus. aktiVU[.] wird  */
      } while ( ( r2 < 1 ) || ( r2 > MAXVU ) ); /* von BAV jede Per- */
     } while ( aktiVU[r2] == 0  ); /* iode neu bestimmt !!           */
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Falls EigemVS,ist*/
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   ;    /* Vp[] = 0.0 ini-  */
                                                 /* tialisiert       */
   /* Bei VR: SUCHE hier auch die Informationskosten addieren        */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn02      */

/* ***************************************************************** */
/* act: Vrvn03:  Versicherungsnehmer   Verhaltensregel: Praeferenz   */
/*                                                                   */
/*                            vgl. Kapitel 3.3.2.2                   */
/* ***************************************************************** */
act Vrvn03 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,pf1[MAXVU+1],pf2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,m;
int vr1,vr2,i,r1,r2;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1 = 0; r2 = 0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = ( sw1 > e0       );    /* Versicherungsstatus fuer beide  */
     vr2 = ( sw2 > f0       );    /* Risiken aus subj. Wahrschlktn.  */
     r1  = 0; m = 0.0;            /* Praeferenzwahl fuer Risiko 1 :  */
     for(i=1;i<=MAXVU;i++)        /* Absolute Werbeaufwendungen der  */
      {                           /* in t aktiven VUs in pf1[]       */
       if ( aktiVU[i] == 1 )      /* sammeln und aufaddieren ...     */
        { pf1[i] = VU[i].DatenVU->Sp[1].l.Wa[gperiod];
          m = m + pf1[i];
        }
       else
        { pf1[i] = 0.0;  }
      }
     for(i=0;i<=MAXVU;i++ )       /* Die Praeferenzen aus relativen  */
      {                           /* Werbeaufwand in Sparte 1        */
       if (m != 0.0) { pf1[i] = pf1[i] / m ; }  /* berechnen         */
      }
     m = 0.0;
     for(i=0;i<=MAXVU;i++ )       /* Maximalen relativen Werbeaufwand*/
      {                           /* finden und den dazugehoerenden  */
       if ( pf1[i] > m )          /* Versicherer speichern           */
        { m  = pf1[i];
          r1 = i;
        }
      }
     if ( r1 == 0 )               /* Wenn kein Versicherer mit       */
      {                           /* pf1[] > 0.0 gefunden wurde,weil */
       do {                       /* kein VU Werbung betreibt, dann  */
        do {                      /* muss ein aktiver VU zufaellig   */
            r1 = ( myrnd() % akvu ) + 1; /* gewaehlt werden          */
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );
      }
     r2  = 0; m = 0.0;            /* Praeferenzwahl fuer Risiko 2 :  */
     for(i=1;i<=MAXVU;i++)        /* Absolute Werbeaufwendungen der  */
      {                           /* in t aktiven VUs in pf2[]       */
       if ( aktiVU[i] == 1 )      /* sammeln und aufaddieren ...     */
        { pf2[i] = VU[i].DatenVU->Sp[2].k.Wa[gperiod];
          m = m + pf1[i];
        }
       else
        { pf2[i] = 0.0;  }
      }
     for(i=0;i<=MAXVU;i++ )       /* Die Praeferenzen aus relativen  */
      {                           /* Werbeaufwand in Sparte 1        */
       if (m != 0.0) { pf2[i] = pf2[i] / m ; }  /* berechnen         */
      }
     m = 0.0;
     for(i=0;i<=MAXVU;i++ )       /* Maximalen relativen Werbeaufwand*/
      {                           /* finden und den dazugehoerenden  */
       if ( pf2[i] > m )          /* Versicherer speichern           */
        { m  = pf2[i];
          r2 = i;
        }
      }
     if ( r2 == 0 )               /* Wenn kein Versicherer mit       */
      {                           /* pf2[] > 0.0 gefunden wurde,weil */
       do {                       /* kein VU Werbung betreibt, dann  */
        do {                      /* muss ein aktiver VU zufaellig   */
            r2 = ( myrnd() % akvu ) + 1; /* gewaehlt werden          */
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );
      }
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = ( sw1 > e1       );    /* Versicherungsstatus fuer beide  */
     vr2 = ( sw2 > f1       );    /* Risiken aus subj. Wahrschlktn.  */
     a1  = 0; m = 0.0;            /* Praeferenzwahl fuer Risiko 1 :  */
     for(i=1;i<=MAXVU;i++)        /* Absolute Werbeaufwendungen der  */
      {                           /* in t aktiven VUs in pf1[]       */
       if ( aktiVU[i] == 1 )      /* sammeln und aufaddieren ...     */
        { pf1[i] = VU[i].DatenVU->Sp[1].l.Wa[gperiod];
          m = m + pf1[i];
        }
       else
        { pf1[i] = 0.0;  }
      }
     for(i=0;i<=MAXVU;i++ )       /* Die Praeferenzen aus relativen  */
      {                           /* Werbeaufwand in Sparte 1        */
       if (m != 0.0) { pf1[i] = pf1[i] / m ; }  /* berechnen         */
      }
     m = 0.0;
     for(i=0;i<=MAXVU;i++ )       /* Maximalen relativen Werbeaufwand*/
      {                           /* finden und den dazugehoerenden  */
       if ( pf1[i] > m )          /* Versicherer speichern           */
        { m  = pf1[i];
          r1 = i;
        }
      }
     if ( r1 == 0 )               /* Wenn kein Versicherer mit       */
      {                           /* pf1[] > 0.0 gefunden wurde,weil */
       do {                       /* kein VU Werbung betreibt, dann  */
        do {                      /* muss ein aktiver VU zufaellig   */
            r1 = ( myrnd() % akvu ) + 1; /* gewaehlt werden          */
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );
      }
     r2  = 0; m = 0.0;            /* Praeferenzwahl fuer Risiko 2 :  */
     for(i=1;i<=MAXVU;i++)        /* Absolute Werbeaufwendungen der  */
      {                           /* in t aktiven VUs in pf2[]       */
       if ( aktiVU[i] == 1 )      /* sammeln und aufaddieren ...     */
        { pf2[i] = VU[i].DatenVU->Sp[2].k.Wa[gperiod];
          m = m + pf1[i];
        }
       else
        { pf2[i] = 0.0;  }
      }
     for(i=0;i<=MAXVU;i++ )       /* Die Praeferenzen aus relativen  */
      {                           /* Werbeaufwand in Sparte 1        */
       if (m != 0.0) { pf2[i] = pf2[i] / m ; }  /* berechnen         */
      }
     m = 0.0;
     for(i=0;i<=MAXVU;i++ )       /* Maximalen relativen Werbeaufwand*/
      {                           /* finden und den dazugehoerenden  */
       if ( pf2[i] > m )          /* Versicherer speichern           */
        { m  = pf2[i];
          r2 = i;
        }
      }
     if ( r2 == 0 )               /* Wenn kein Versicherer mit       */
      {                           /* pf2[] > 0.0 gefunden wurde,weil */
       do {                       /* kein VU Werbung betreibt, dann  */
        do {                      /* muss ein aktiver VU zufaellig   */
            r2 = ( myrnd() % akvu ) + 1; /* gewaehlt werden          */
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );
      }
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Falls EigemVS,ist*/
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   ;    /* Vp[] = 0.0 ini-  */
                                                 /* tialisiert       */
   /* Bei VR: SUCHE hier auch die Informationskosten addieren        */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn03      */

/* ***************************************************************** */
/* act: Vrvn04:  Versicherungsnehmer   Verhaltensregel: Totale       */
/*                                                      Erinnerung   */
/*                            vgl. Kapitel 3.3.2.2                   */
/* ***************************************************************** */
act Vrvn04 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,sw1,sw2,a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,
      h0,h1,m;
int vr1,vr2,r1,r2,i;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1 = 0; r2 = 0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = ( sw1 > e0       );    /* Versicherungsstatus aus subjek- */
     vr2 = ( sw2 > f0       );    /* tiven Wahrscheinlichkeiten....  */
     r1 = 0; m = 1000.0;          /* Erinnerungswahl fuer Risiko 1:..*/
     for(i=1; i<=(gperiod-1) ;i++ )
      {
       if (VN[gOwnnr].DatenVN->Rk[1].l.Vs[i] == 1 ) /* Wenn VN in    */
        {         /* der Periode i versichert war und die Praemie    */
         if ( VN[gOwnnr].DatenVN->Rk[1].l.Vp[i] < m )/* kleiner war..*/
          {  /* ...als die nie erreichbare Praemie von 1000.0 ...    */
           m  = VN[gOwnnr].DatenVN->Rk[1].l.Vp[i];/* Praemie und ... */
           r1 = VN[gOwnnr].DatenVN->Rk[1].l.Vu[i];/* Anbieter merken */
          }                                       /* ... und         */
        }                                         /* ..weitersuchen. */
      }
     if ( r1 == 0 )                /* Falls trotzdem keine VU gefun- */
      {                            /* den wurde: Zufallswahl !       */
       do {
        do {
            r1 = ( myrnd() % akvu ) + 1;
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );
      }
     r2 = 0; m = 1000.0;          /* Erinnerungswahl fuer Risiko 2:..*/
     for(i=1; i<=(gperiod-1) ;i++ )
      {
       if (VN[gOwnnr].DatenVN->Rk[2].k.Vs[i] == 1 ) /* Wenn VN in    */
        {         /* der Periode i versichert war und die Praemie    */
         if ( VN[gOwnnr].DatenVN->Rk[2].k.Vp[i] < m )/* kleiner war..*/
          {  /* ...als die nie erreichbare Praemie von 1000.0 ...    */
           m  = VN[gOwnnr].DatenVN->Rk[2].k.Vp[i];/* Praemie und ... */
           r2 = VN[gOwnnr].DatenVN->Rk[2].k.Vu[i];/* Anbieter merken */
          }                                       /* ... und         */
        }                                         /* ..weitersuchen. */
      }
     if ( r2 == 0 )                /* Falls trotzdem keine VU gefun- */
      {                            /* den wurde: Zufallswahl !       */
       do {
        do {
            r2 = ( myrnd() % akvu ) + 1;
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );
      }
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = ( sw1 > e1       );    /* Versicherungsstatus aus subjek- */
     vr2 = ( sw2 > f1       );    /* tiven Wahrscheinlichkeiten....  */
     r1 = 0; m = 1000.0;          /* Erinnerungswahl fuer Risiko 1:..*/
     for(i=1; i<=(gperiod-1) ;i++ )
      {
       if (VN[gOwnnr].DatenVN->Rk[1].l.Vs[i] == 1 ) /* Wenn VN in    */
        {         /* der Periode i versichert war und die Praemie    */
         if ( VN[gOwnnr].DatenVN->Rk[1].l.Vp[i] < m )/* kleiner war..*/
          {  /* ...als die nie erreichbare Praemie von 1000.0 ...    */
           m  = VN[gOwnnr].DatenVN->Rk[1].l.Vp[i];/* Praemie und ... */
           r1 = VN[gOwnnr].DatenVN->Rk[1].l.Vu[i];/* Anbieter merken */
          }                                       /* ... und         */
        }                                         /* ..weitersuchen. */
      }
     if ( r1 == 0 )                /* Falls trotzdem keine VU gefun- */
      {                            /* den wurde: Zufallswahl !       */
       do {
        do {
            r1 = ( myrnd() % akvu ) + 1;
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );
      }
     r2 = 0; m = 1000.0;          /* Erinnerungswahl fuer Risiko 2:..*/
     for(i=1; i<=(gperiod-1) ;i++ )
      {
       if (VN[gOwnnr].DatenVN->Rk[2].k.Vs[i] == 1 ) /* Wenn VN in    */
        {         /* der Periode i versichert war und die Praemie    */
         if ( VN[gOwnnr].DatenVN->Rk[2].k.Vp[i] < m )/* kleiner war..*/
          {  /* ...als die nie erreichbare Praemie von 1000.0 ...    */
           m  = VN[gOwnnr].DatenVN->Rk[2].k.Vp[i];/* Praemie und ... */
           r2 = VN[gOwnnr].DatenVN->Rk[2].k.Vu[i];/* Anbieter merken */
          }                                       /* ... und         */
        }                                         /* ..weitersuchen. */
      }
     if ( r2 == 0 )                /* Falls trotzdem keine VU gefun- */
      {                            /* den wurde: Zufallswahl !       */
       do {
        do {
            r2 = ( myrnd() % akvu ) + 1;
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );
      }
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Falls EigemVS,ist*/
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   ;    /* Vp[] = 0.0 ini-  */
                                                 /* tialisiert       */
   /* Bei VR: SUCHE hier auch die Informationskosten addieren        */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn04      */

/* ***************************************************************** */
/* act: Vrvn05:  Versicherungsnehmer   Verhaltensregel:  Suche       */
/*                                                                   */
/*                            vgl. Kapitel 3.3.2.3                   */
/* ***************************************************************** */
act Vrvn05 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,p1[MAXVU+1],p2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,ik,m;
int vr1,vr2,r1,r2,i,j,k;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1 = 0; r2 = 0; ik = 0.0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = ( BAV[1].DatenBAV.Dg[0] <= e0);
     vr2 = ( BAV[1].DatenBAV.Dg[0] <= f0);
     for(i=1;i<=MAXVU;i++)                     /* Suchwahl: Risiko 1 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p1[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=g0;j++)       /* Jetzt Stichprobe mit dem Umfang g0  */
      {                       /* aus allen aktiven VUs ziehen:       */
       do {                   /* Doppelziehungen sind moeglich !     */
        do {
            r1 = ( myrnd() % akvu ) + 1;
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );       /* ... und die Ergeb-  */
       p1[r1] = VU[r1].DatenVU->Sp[1].l.Pr[gperiod]; /* nisse merken.*/
       ik = ik + BAV[1].DatenBAV.Sk[gperiod];
      }
     r1 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer aus-     */
       if ( p1[i] < m )       /* waehlen.                            */
        {
          m  = p1[i];
          r1 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
     for(i=1;i<=MAXVU;i++)                     /* Suchwahl: Risiko 2 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p2[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=h0;j++)       /* Jetzt Stichprobe mit dem Umfang h0  */
      {                       /* aus allen aktiven VUs ziehen:       */
       do {                   /* Doppelziehungen sind moeglich !     */
        do {
            r2 = ( myrnd() % akvu ) + 1;
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );       /* ... und die Ergeb-  */
       p2[r2] = VU[r2].DatenVU->Sp[2].k.Pr[gperiod]; /* nisse merken.*/
       ik = ik + BAV[1].DatenBAV.Sk[gperiod];
      }
     r2 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer aus-     */
       if ( p2[i] < m )       /* waehlen.                            */
        {
          m  = p2[i];
          r2 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = ( BAV[1].DatenBAV.Dg[0] <= e1);
     vr2 = ( BAV[1].DatenBAV.Dg[0] <= f1);
     for(i=1;i<=MAXVU;i++)                     /* Suchwahl: Risiko 1 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p1[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=g1;j++)       /* Jetzt Stichprobe mit dem Umfang g0  */
      {                       /* aus allen aktiven VUs ziehen:       */
       do {                   /* Doppelziehungen sind moeglich !     */
        do {
            r1 = ( myrnd() % akvu ) + 1;
           } while ( ( r1 < 1 ) || ( r1 > MAXVU ) );
          } while ( aktiVU[r1] == 0  );       /* ... und die Ergeb-  */
       p1[r1] = VU[r1].DatenVU->Sp[1].l.Pr[gperiod]; /* nisse merken.*/
       ik = ik + BAV[1].DatenBAV.Sk[gperiod];
      }
     r1 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer aus-     */
       if ( p1[i] < m )       /* waehlen.                            */
        {
          m  = p1[i];
          r1 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
     for(i=1;i<=MAXVU;i++)                     /* Suchwahl: Risiko 2 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p2[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=h1;j++)       /* Jetzt Stichprobe mit dem Umfang h0  */
      {                       /* aus allen aktiven VUs ziehen:       */
       do {                   /* Doppelziehungen sind moeglich !     */
        do {
            r2 = ( myrnd() % akvu ) + 1;
           } while ( ( r2 < 1 ) || ( r2 > MAXVU ) );
          } while ( aktiVU[r2] == 0  );       /* ... und die Ergeb-  */
       p2[r2] = VU[r2].DatenVU->Sp[2].k.Pr[gperiod]; /* nisse merken.*/
       ik = ik + BAV[1].DatenBAV.Sk[gperiod];
      }
     r2 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer aus-     */
       if ( p2[i] < m )       /* waehlen.                            */
        {
          m  = p2[i];
          r2 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Praemien in den  */
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   -    /* Sparten,         */
  ik                                        ;    /* Suchkosten       */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn05      */

/* ***************************************************************** */
/* act: Vrvn06:  Versicherungsnehmer   Verhaltensregel:  Beste       */
/*                                                       Information */
/*                            vgl. Kapitel 3.3.2.3                   */
/* ***************************************************************** */
act Vrvn06 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,p1[MAXVU+1],p2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,ik,m;
int vr1,vr2,i,j,k,r1,r2;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; ik = 0.0; r1 = 0; r2 = 0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = ( BAV[1].DatenBAV.Dg[0] <= e0);
     vr2 = ( BAV[1].DatenBAV.Dg[0] <= f0);
     for(i=1;i<=MAXVU;i++)    /* Minimum-Praemie :          Risiko 1 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p1[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=MAXVU;j++)    /* Praemieninformationen aller Ver-    */
      {                       /* sicherer der Periode holen und      */
       p1[j] = VU[j].DatenVU->Sp[1].l.Pr[gperiod]; /* die Kosten da  */
       ik = ik + BAV[1].DatenBAV.Sk[gperiod]; /* fuer merken ...     */
      }
     r1 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer waehlen..*/
       if ( (p1[i] < m) && (aktiVU[i] != 0) ) /* ..wenn dieser       */
        {                     /* Versicherer auch aktiv ist...       */
          m  = p1[i];
          r1 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
     for(i=1;i<=MAXVU;i++)    /* Minimum-Praemie :          Risiko 2 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p2[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=MAXVU;j++)    /* Praemieninformationen aller Ver-    */
      {                       /* sicherer der Periode holen und      */
       p2[j] = VU[j].DatenVU->Sp[2].k.Pr[gperiod]; /* die Kosten da  */
       ik = ik + BAV[1].DatenBAV.Sk[gperiod]; /* fuer merken ...     */
      }
     r2 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer waehlen..*/
       if ( (p2[i] < m) && (aktiVU[i] != 0) ) /* ..wenn dieser       */
        {                     /* Versicherer auch aktiv ist...       */
          m  = p2[i];
          r2 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = ( BAV[1].DatenBAV.Dg[0] <= e1);
     vr2 = ( BAV[1].DatenBAV.Dg[0] <= f1);
     for(i=1;i<=MAXVU;i++)    /* Minimum-Praemie :          Risiko 1 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p1[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=MAXVU;j++)    /* Praemieninformationen aller Ver-    */
      {                       /* sicherer der Periode holen und      */
       p1[j] = VU[j].DatenVU->Sp[1].l.Pr[gperiod]; /* die Kosten da  */
       ik = ik + BAV[1].DatenBAV.Sk[gperiod]; /* fuer merken ...     */
      }
     r1 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer waehlen..*/
       if ( (p1[i] < m) && (aktiVU[i] != 0) ) /* ..wenn dieser       */
        {                     /* Versicherer auch aktiv ist...       */
          m  = p1[i];
          r1 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
     for(i=1;i<=MAXVU;i++)    /* Minimum-Praemie :          Risiko 2 */
      {                       /* Weil ein Minimum gesucht wird: zu-  */
       p2[i] = 1000.0;        /* naechst Suchvektor auf 1000.0 init. */
      }
     for(j=1;j<=MAXVU;j++)    /* Praemieninformationen aller Ver-    */
      {                       /* sicherer der Periode holen und      */
       p2[j] = VU[j].DatenVU->Sp[2].k.Pr[gperiod]; /* die Kosten da  */
       ik = ik + BAV[1].DatenBAV.Sk[gperiod]; /* fuer merken ...     */
      }
     r2 = 0; m = 1000.0;      /* ... aus der gefundenen Stichprobe   */
     for(i=1;i<=MAXVU;i++)    /* das Minimum ermitteln und den       */
      {                       /* entsprechenden Versicherer waehlen..*/
       if ( (p2[i] < m) && (aktiVU[i] != 0) ) /* ..wenn dieser       */
        {                     /* Versicherer auch aktiv ist...       */
          m  = p2[i];
          r2 = i;
        }                     /* Mindestens EIN VU muss aktiv sein,  */
      }                       /* sonst ist a1 hier immer noch Null ! */
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Praemien in den  */
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   -    /* Sparten,         */
  ik                                        ;    /* Suchkosten       */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn06      */

/* ***************************************************************** */
/* act: Vrvn07:  Versicherungsnehmer   Verhaltensregel:  undefiniert */
/*                                                                   */
/*                            vgl. Kapitel 3.3.2.x                   */
/* ***************************************************************** */
act Vrvn07 {                       /* Vereinbarung der Hilfsvariable */
float s1,s2,pf1[MAXVU+1],pf2[MAXVU+1],sw1,sw2,a0,a1,b0,b1,c0,c1,
      d0,d1,e0,e1,f0,f1,g0,g1,h0,h1;
int vr1,vr2,r1,r2;
if(gperiod>=((VN[gOwnnr].DatenVN->Ap)*(VN[gOwnnr].DatenVN->Al[rl])))
 {/* LANGE IMS-Variable in KURZE Variable fuer VR uebersetzen        */
  a0 = VN[gOwnnr].DatenVN->Pv[0 ]; a1 = VN[gOwnnr].DatenVN->Pv[1 ];
  b0 = VN[gOwnnr].DatenVN->Pv[2 ]; b1 = VN[gOwnnr].DatenVN->Pv[3 ];
  c0 = VN[gOwnnr].DatenVN->Pv[4 ]; c1 = VN[gOwnnr].DatenVN->Pv[5 ];
  d0 = VN[gOwnnr].DatenVN->Pv[6 ]; d1 = VN[gOwnnr].DatenVN->Pv[7 ];
  e0 = VN[gOwnnr].DatenVN->Pv[8 ]; e1 = VN[gOwnnr].DatenVN->Pv[9 ];
  f0 = VN[gOwnnr].DatenVN->Pv[10]; f1 = VN[gOwnnr].DatenVN->Pv[11];
  g0 = VN[gOwnnr].DatenVN->Pv[12]; g1 = VN[gOwnnr].DatenVN->Pv[13];
  h0 = VN[gOwnnr].DatenVN->Pv[14]; h1 = VN[gOwnnr].DatenVN->Pv[15];
  sw1 = VN[gOwnnr].DatenVN->Rk[1].l.Sw[gperiod];
  sw2 = VN[gOwnnr].DatenVN->Rk[2].k.Sw[gperiod];
  vr1 = 0; vr2 = 0; r1 = 0; r2 = 0;
  /* Aktivitaetsmeldung an die Aggregattabellen der class BAV: ...   */
  BAV[1].DatenBAV.Vnag1[ gOwnnr                 ]++;
  BAV[1].DatenBAV.Vnag2[ VN[gOwnnr].DatenVN->Vr ]++;
  BAV[1].DatenBAV.Vnag3[ VN[gOwnnr].DatenVN->Vk ]++;
 if ( !( BAV[1].DatenBAV.As[gperiod] * BAV[1].DatenBAV.Ar[rl]))
  {                                         /* KEIN Aenderungsschock */
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a0 + b0 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c0 + d0 * normal() ); /* erzeugen  */
     /*
     vr1 = 0; HIER KOENNEN DIE EIGENENTWICKLUNGEN REALISIERT WERDEN
     vr2 = 0;
     r1  = 0;
     r2  = 0;
     */
   }                           /* END: else ( gperiod == 1 )         */
  }                       /* END: if ( !( BAV[1].Daten.As[gperiod]...*/
  else                         /* Aenderungsschock hat stattgefunden */
  {
   if ( gperiod == 1 )         /* Erste Periode: Startwerte benutzen */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     vr1 = VN[gOwnnr].DatenVN->Rk[1].l.Vs[1];     /* Status in erster*/
     vr2 = VN[gOwnnr].DatenVN->Rk[2].k.Vs[1];     /* Periode: ...    */
     r1  = VN[gOwnnr].DatenVN->Rk[1].l.Vu[1];     /* Versicherer in  */
     r2  = VN[gOwnnr].DatenVN->Rk[2].k.Vu[1];     /* erster Periode  */
   }                                    /* END:   if ( gperiod == 1 )*/
   else                     /* Periode > 1: Verhaltensregel anwenden */
   {
     s1  = ( sw1 > normal() ) * ( a1 + b1 * normal() ); /* Schaeden  */
     s2  = ( sw2 > normal() ) * ( c1 + d1 * normal() ); /* erzeugen  */
     /*
     vr1 = 0;  HIER KOENNEN DIE EIGENENTWICKLUNGEN REALISIERT WERDEN
     vr2 = 0;
     r1  = 0;
     r2  = 0;
     */
   }                                   /* END: else if (gperiod == 1)*/
  }                                    /* END: else Aenderungsschock */
  if ( vr1 == 1 )
   {                                         /* ABRECHNUNG: Risiko 1 */
    if ( s1 > 0.0   )
     {                          /* FALL:  Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod] -    /* und Schaden       */
       s1;                                      /* abziehen...       */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] =    /* Periodenschadens- */
       VU[r1].DatenVU->Sp[1].l.Sh[gperiod] +    /* summe um den Scha-*/
       s1;                                      /* den erhoehen      */
       VU[r1].DatenVU->Sp[1].l.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }  /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] =    /* Reserven um       */
       VU[r1].DatenVU->Sp[1].l.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];
       VU[r1].DatenVU->Sp[1].l.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Gehabten Versiche-*/
       r1;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r1].DatenVU->Sp[1].l.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: if ( vr1==1 )   */
   else
   {
    if ( s1 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[1].l.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[1].l.Vs[gperiod]= /* Versicherungssta- */
       vr1;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[1].l.Ev[gperiod]= /* Eigenversicherten */
       s1;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[1].l.Sh[gperiod]= /* Gehabten Schaden  */
       s1;                                      /* merken            */
     }                                     /* END: if ( s1 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                       /* END: else (s1 > 0.0  */
   }                                         /* END: else ( vr1==1 ) */
  if ( vr2 == 1 )
   {                                         /* ABRECHNUNG: Risiko 2 */
    if ( s2 > 0.0   )
     {                           /* FALL: Fremdversicherter Schaden: */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod] -    /* und Schaden       */
       s2;                                      /* abziehen...       */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] =    /* Periodenschadens- */
       VU[r2].DatenVU->Sp[2].k.Sh[gperiod] +    /* summe um den Scha-*/
       s2;                                      /* den erhoehen      */
       VU[r2].DatenVU->Sp[2].k.Sa[gperiod]++;   /* Schadenanzahl um  */
                                                /* eins erhoehen     */
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Fremdversicherter Nicht-Schaden */
                                                /* VU-Vektoren:      */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] =    /* Reserven um       */
       VU[r2].DatenVU->Sp[2].k.Rs[gperiod] +    /* Praemie erhoehen  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];
       VU[r2].DatenVU->Sp[2].k.Vn[gperiod]++;   /* Versichertenanzahl*/
                                                /* um eins erhoehen  */
                                                /* VN-Vektoren :     */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Gehabten Versiche-*/
       r2;                                      /* rer merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]= /* Gezahlte Praemie  */
       VU[r2].DatenVU->Sp[2].k.Pr[gperiod];     /* merken            */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Kein Schaden ge-  */
       0.0;                                     /* habt              */
     }                                      /* END: else (s2 > 0.0 ) */
   }                                        /* END: if ( vr2 == 1 )  */
   else
   {
    if ( s2 > 0.0   )
     {                           /* FALL: Eigenversicherter Schaden: */
       VN[gOwnnr].DatenVN->Rk[2].k.Vu[gperiod]= /* Keinen Versicherer*/
       0;                                       /* gehabt            */
       VN[gOwnnr].DatenVN->Rk[2].k.Vs[gperiod]= /* Versicherungssta- */
       vr2;                                     /* tus merken        */
       VN[gOwnnr].DatenVN->Rk[2].k.Ev[gperiod]= /* Eigenversicherten */
       s2;                                      /* Schaden merken    */
       VN[gOwnnr].DatenVN->Rk[2].k.Sh[gperiod]= /* Gehabten Schaden  */
       s2;                                      /* merken            */
     }                                     /* END: if ( s2 > 0.0   ) */
    else
     {                      /* FALL: Eigenversicherter Nicht-Schaden */
                                                /* NICHTS abzurechnen*/
     }                                     /* END: else (s2 > 0.0    */
   }                                       /* END: else ( vr2 == 1 ) */
  VN[gOwnnr].DatenVN->Vm[gperiod]           =    /* Kummuliertes Ver-*/
  VN[gOwnnr].DatenVN->Vm[gperiod-1]         -    /* moegen berechnen */
  s1                                        -
  s2                                        -
  VN[gOwnnr].DatenVN->Rk[1].l.Vp[gperiod]   -    /* Falls EigemVS,ist*/
  VN[gOwnnr].DatenVN->Rk[2].k.Vp[gperiod]   ;    /* Vp[] = 0.0 ini-  */
                                                 /* tialisiert       */
   /* Bei VR: SUCHE hier auch die Informationskosten addieren        */
   /* fprintf(runreport,
              "[%d,%d] R1[%2d] R2[%2d] V1[%1d] V2[%1d] %2.1f %2.1f\n",
              gOwnnr, gperiod, r1,r2,vr1,vr2,s1,s2);
    */
 }                                          /* END: IF (gperiod>=... */
}                                                /* END: Vrvn07      */

/* ***************************************************************** */
/*            Beginn der Service- und Menuroutinen                   */
/* ***************************************************************** */
/* ***************************************************************** */
/* func Mkload() : Laden einer Modellkonfiguration. Aus einer Datei  */
/*                 werden alle dynamischen ESL-Subjetke(VU,VN) an die*/
/*                 im Hauptspeicher reservierten Stellen geladen.    */
/* ***************************************************************** */
func Mkload() {
 int i;                                          /* Schleifenzaehler */
 clearScreen();
 printfAt( 1,24, "[ Marktkonfiguration laden ]");
 konfig = fopen("konfig.ims","rb");
 if ( konfig == (file *) 0)
   {
    fprintf(runreport,"func Mkload(): konfig.ims nicht geoeffnet\n");
   }
 if ( konfig != (file *) 0)
  {
   for(i=1;i<=MAXVU;i++)
    {
     if ( VU[i].DatenVU != (struct s1 *) 0 )
      {
       fread(VU[i].DatenVU, sizeof(struct s1), 1, konfig);
      }
    }
   for(i=1;i<=MAXVN;i++)
    {
     if ( VN[i].DatenVN != (struct s2 *) 0 )
      {
       fread(VN[i].DatenVN, sizeof(struct s2), 1, konfig);
      }
     }
   fread(&BAV[1].DatenBAV, sizeof(struct s7), 1, konfig);     
  fclose(konfig);
  for(i=1;i<=MAXVU;i++)       /* Automatische agvux[.]-Zuweisung an  */
   {                          /* die Aggregatdateien, die gebraucht  */
    BAV[1].DatenBAV.Vuag2[ VU[i].DatenVU->Vr ]++; /* werden          */
    BAV[1].DatenBAV.Vuag3[ VU[i].DatenVU->Vk ]++;
   }
  for( i = 1;  i <=    10 ; i++ )
   { if ( BAV[1].DatenBAV.Vuag2[i] > 0 ) { agvu2[i] = 1;} }
  for( i = 1;  i <=     3 ; i++ )
   { if ( BAV[1].DatenBAV.Vuag3[i] > 0 ) { agvu3[i] = 1;} }
  agvu4[1] = 1; /* Die Subjektklasse der Versicherer: immer erzeugen */    
  for(i=1;i<=MAXVN;i++)       /* Automatische agvnx[.]-Zuweisung an  */
   {                          /* die Aggregatdateien, die gebraucht  */
    BAV[1].DatenBAV.Vnag2[ VN[i].DatenVN->Vr ]++; /* werden          */
    BAV[1].DatenBAV.Vnag3[ VN[i].DatenVN->Vk ]++;
   }
  for( i = 1;  i <=     7 ; i++ )
   { if ( BAV[1].DatenBAV.Vnag2[i] > 0 ) { agvn2[i] = 1;} }
  for( i = 1;  i <=     3 ; i++ )
   { if ( BAV[1].DatenBAV.Vnag3[i] > 0 ) { agvn3[i] = 1;} }
  agvn4[1] = 1; /* Subjektklasse Versicherungsnehmer: immer erzeugen */
  load = 1; /* TAG-Variable fuer die Aktionen: MyinitVU,MyinitVN     */
  } /* end if ( konfig != (file *) 0) */
 waitKey();
} /* END: func Mkload() */

/* ***************************************************************** */
/* func Mksave() : Speichern einer Modellkonfiguration               */
/*                                                                   */
/*                                                                   */
/* ***************************************************************** */
func Mksave() {
 int i;                                          /* Schleifenzaehler */
 clearScreen();
 printfAt( 1,22, "[ Marktkonfiguration speichern ]");
 konfig = fopen("konfig.ims","wb");
 if ( konfig == (file *) 0)
  {
   fprintf(runreport,"func Mksave(): konfig.ims nicht geoeffnet\n");
  }
  else /* ( konfig != (file *) 0) */
  {
   for(i=1;i<=MAXVU;i++)
    {
     if ( VU[i].DatenVU != (struct s1 *) 0 )
      {
       fwrite(VU[i].DatenVU, sizeof(struct s1), 1, konfig);
      }
    }
   for(i=1;i<=MAXVN;i++)
    {
     if ( VN[i].DatenVN != (struct s2 *) 0 )
      {
       fwrite(VN[i].DatenVN, sizeof(struct s2), 1, konfig);
      }
    }         
    fwrite(&BAV[1].DatenBAV, sizeof(struct s7), 1, konfig);
   fclose(konfig);
  } /* END: else, if ( konfig == (file *) 0) */
 waitKey();
} /* END: func Mksave() */

/* ***************************************************************** */
/* func Bavauin() : Automatische Initialisierung der class BAV.      */
/*                  Wird von  allen funcs fuer die vordefinierten    */
/*                  Modelle verwendet.                               */
/* ***************************************************************** */
func Bavauin(p,l,k,z,r)
int    p;           /* Periode mit Aenderungssschock                 */
int    l;           /* Simulationslauf mit Aenderungsschock          */
float  k;           /* Kosten pro Suchschritt des VNs                */
float  z;           /* Zinssatz der Reservenverzinsung               */
int    r;           /* Sim.Wiederholungen zugelassen = 1, sonst 0    */
{
int j;              /* Schleifenzaehler                              */
 for( j = 1; j <= SIMLAENGE ; j++)  /* Beispiele :                   */
  {                                 /* Bavauin(100,100) keine Aender-*/
   if ( j < p )                     /* ungsschocks in keinem Lauf    */
    { BAV[1].DatenBAV.As[j] = 0; }  /* Bavauin(0,0) in jedem Lauf in */
    else                            /* jeder Periode Aenderungsschock*/
     { BAV[1].DatenBAV.As[j] = 1; } /* Bavauin(50,50) in den ersten  */
  }                                 /* 50 Laeufen KEIN Schock, in den*/
 for( j = 1; j <= SIMLAENGE ; j++)  /* letzten 50 Laeufen ab Periode */
  {                                 /* 50 in jeder Periode Aender-   */
   if ( j < l )                     /* ungsschock                    */
    { BAV[1].DatenBAV.Ar[j] = 0; }
    else
     { BAV[1].DatenBAV.Ar[j] = 1; }
  }
 for( j = 1; j <= SIMLAENGE; j++)
  {
   BAV[1].DatenBAV.Sk[j] = k;
   BAV[1].DatenBAV.Zs[j] = z;
  }
 BAV[1].DatenBAV.Rp = r;
} /* END: func Bavauin() */

/* ***************************************************************** */
/* func Vuauini() : Automatische Initialisierung einer Versicherung  */
/*                  Wird von  allen funcs fuer die vordefinierten    */
/*                  Modelle verwendet.                               */
/* ***************************************************************** */
func Vuauini(i,st,ap,al,a11,a12,a13,a21,a22,a23,p1,w1,p2,w2,
             v0,v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11,v12,v13,v14,v15 )
int i;             /* Nummer der Versicherung, die initialisiert wird*/
int st;            /* Nummer der Verhaltensregel, die VU ausfuehrt   */
int ap;            /* Aktivierungsperiode der Versicherung           */
int al;            /* Aktivierungslaeufe:alle < al: Al[j] = 1;sonst 0*/
float a11,a12,a13,a21,a22,a23;/* Anspruchsnivaus der Mark-Up Regeln  */
float p1,w1,p2,w2; /* Startwerte fuer Praemien, Werbung in 2 Sparten */
float v0,v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11,v12,v13,v14,v15; /* Die  */
                   /* Elemente des Parametervektors                  */
{
int j;                                /* Schleifenzaehler            */
 VU[i].DatenVU->Ac[1].st = st;        /* Verhaltensregel und ihr...  */
 VU[i].DatenVU->Ac[1].lt = 1;         /* Ausfuehrungszeitpunkt...    */
 for( j = 2; j <= MAXNLOG; j++ )      /* und den Rest des Aktions-   */
  {                                   /* vektors auf 0 initialisieren*/
   VU[i].DatenVU->Ac[j].lt  = 0;
   VU[i].DatenVU->Ac[j].st  = 0;
  }
 VU[i].DatenVU->Ap       = ap;        /* Aktivierungszeitpunkt       */
 for( j = 1; j <= SIMLAENGE; j++)     /* Aktivierungslaeufe          */
  {
   if ( j <= al )
   { VU[i].DatenVU->Al[j] = 1; }
   else
    { VU[i].DatenVU->Al[j] = 0; }
  }
 VU[i].DatenVU->Vr       = st;        /* Zuordnung zu den Aggregaten */
 VU[i].DatenVU->Vk       = vkrvu[st]; /* der Stufe II und III        */
 VU[i].DatenVU->A1[1] = a11;          /* Anspruchsniveaus der Sparten*/
 VU[i].DatenVU->A1[2] = a12;          /* NUR A[1..3] NICHT A[0]      */
 VU[i].DatenVU->A1[3] = a13;
 VU[i].DatenVU->A2[1] = a21;
 VU[i].DatenVU->A2[2] = a22;
 VU[i].DatenVU->A2[3] = a23;
 VU[i].DatenVU->Sp[1].l.Pr[1] = p1 ; /* Startwerte:Sparte 1 Praemien */
 VU[i].DatenVU->Sp[1].l.Wa[1] = w1 ; /*                     Werbung  */
 VU[i].DatenVU->Sp[2].k.Pr[1] = p2 ; /*            Sparte 2 Praemien */
 VU[i].DatenVU->Sp[2].k.Wa[1] = w2 ; /*                     Werbung  */
 VU[i].DatenVU->Pv[ 0] = v0;  VU[i].DatenVU->Pv[ 8] = v8 ; /* Initia-*/
 VU[i].DatenVU->Pv[ 1] = v1;  VU[i].DatenVU->Pv[ 9] = v9 ; /* lisie- */
 VU[i].DatenVU->Pv[ 2] = v2;  VU[i].DatenVU->Pv[10] = v10; /* rung   */
 VU[i].DatenVU->Pv[ 3] = v3;  VU[i].DatenVU->Pv[11] = v11; /* des    */
 VU[i].DatenVU->Pv[ 4] = v4;  VU[i].DatenVU->Pv[12] = v12; /* Para-  */
 VU[i].DatenVU->Pv[ 5] = v5;  VU[i].DatenVU->Pv[13] = v13; /* meter- */
 VU[i].DatenVU->Pv[ 6] = v6;  VU[i].DatenVU->Pv[14] = v14; /* vektors*/
 VU[i].DatenVU->Pv[ 7] = v7;  VU[i].DatenVU->Pv[15] = v15;
} /* END: func Vuauini() */

/* ***************************************************************** */
/* func Vnauini() : Automatische Initialisierung eines Versicherten  */
/*                  Wird von  allen funcs fuer die vordefinierten    */
/*                  Modelle verwendet.                               */
/* ***************************************************************** */
func Vnauini(i,st,ap,al,vs1,vu1,vs2,vu2,vm,
             v0,v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11,v12,v13,v14,v15 )
int i;             /* Nummer des Versicherten, der initialisiert wird*/
int st;            /* Nummer der Verhaltensregel, die VN ausfuehrt   */
int ap;            /* Aktivierungsperiode des Versicherten           */
int al;            /* Aktivierungslaeufe:alle < al: Al[j] = 1;sonst 0*/
int vs1,vu1,vs2,vu2; /* Startwerte: Versicherer,Status in 2 Sparten  */
float vm;          /* Startwert des Vermoegens des Versicherten      */
float v0,v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11,v12,v13,v14,v15; /* Die  */
                   /* Elemente des Parametervektors                  */
{
int j;                                /* Schleifenzaehler            */
 VN[i].DatenVN->Ac[1].st = st;        /* Verhaltensregel und ihr...  */
 VN[i].DatenVN->Ac[1].lt = 1;         /* Ausfuehrungszeitpunkt...    */
 for( j = 2; j <= MAXNLOG; j++ )      /* Rest des Aktionsvektors auf */
  {                                   /* {0} initialisieren...       */
   VN[i].DatenVN->Ac[j].lt = 0;
   VN[i].DatenVN->Ac[j].st = 0;
  }
 VN[i].DatenVN->Ap = ap;              /* Aktivierungsperiode = 1..   */
 for( j = 1; j <= SIMLAENGE; j++ )    /* Aktivierungslaeufe          */
  {                                   /* Beispiel: Vnauini(5,..,1,.):*/
   if ( j <= al)                      /* Versicherter 5 ist NUR im   */
    { VN[i].DatenVN->Al[j] = 1; }     /* ersten Lauf aktiv ...       */
    else
     { VN[i].DatenVN->Al[j] = 0; }
  }
 VN[i].DatenVN->Vr = st;              /* Zuordnung zu den Aggregaten */
 VN[i].DatenVN->Vk = vkrvn[st];       /* der Stufe II und III...     */
 VN[i].DatenVN->Rk[1].l.Vu[1]= vu1;   /* Startewerte Risiko 1: Status*/
 VN[i].DatenVN->Rk[1].l.Vs[1]= vs1;   /*                  Versicherer*/
 VN[i].DatenVN->Rk[2].k.Vu[1]= vu2;   /*             Risiko 2: Status*/
 VN[i].DatenVN->Rk[2].k.Vs[1]= vs2;   /*                  Versicherer*/
 VN[i].DatenVN->Vm[0] = vm;           /* Startvermoegen              */
 VN[i].DatenVN->Pv[ 0] = v0 ;  VN[i].DatenVN->Pv[ 8] = v8 ; /* Initi-*/
 VN[i].DatenVN->Pv[ 1] = v1 ;  VN[i].DatenVN->Pv[ 9] = v9 ; /* lisi- */
 VN[i].DatenVN->Pv[ 2] = v2 ;  VN[i].DatenVN->Pv[10] = v10; /* rung  */
 VN[i].DatenVN->Pv[ 3] = v3 ;  VN[i].DatenVN->Pv[11] = v11; /* des   */
 VN[i].DatenVN->Pv[ 4] = v4 ;  VN[i].DatenVN->Pv[12] = v12; /* Para- */
 VN[i].DatenVN->Pv[ 5] = v5 ;  VN[i].DatenVN->Pv[13] = v13; /* meter-*/
 VN[i].DatenVN->Pv[ 6] = v6 ;  VN[i].DatenVN->Pv[14] = v14; /*vektors*/
 VN[i].DatenVN->Pv[ 7] = v7 ;  VN[i].DatenVN->Pv[15] = v15;
} /* END: func Vnauini() */

/* ***************************************************************** */
/* func Vdefmd1() : Vordefinitiertes Modell 1                        */
/*                  Homogenes Angebot bei homogener Nachfrage        */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd1() {
 int j;                                 /* Schleifenzaehler          */
 Bavauin(100,100,0.0,0.0,0);/* In KEINER Periode, KEINEM Lauf Aen-   */
                            /*derungsschock, Suchkosten,Zins = 0.0   */
                            /* KEINE Wiederholungen                  */
 for( j = 1; j <= MAXVU; j++ )
  {
   Vuauini(j, 3, 1, 1, 0.0,0.0,0.0,0.0,0.0,0.0,  30.0,0.0,30.0,0.0,
           1.03,0.0 ,0.97,0.0 ,1.08,0.0 ,0.92,0.0 , /* Pramienreakt. */
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for( j = 1; j <= MAXVN; j++ )
  {
   Vnauini(j, 1, 1, 1, 0,0,0,0, 0.0,
           30.0, 0.0, 5.0, 0.0, 30.0, 0.0, 10.0, 0.0,  /* Schadenfkt.*/
            0.0, 0.0, 0.0, 0.0, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 agvu1[ 1] = 1; agvu1[17] = 1; /* Aggregaterzeugung:Versicherer: 1,17*/
 agvu2[ 3] = 1;                /* Alle VUs mit VR: Mark-Up I         */
 agvu3[ 2] = 1;                /* Alle VUs der VK Eigeninfo-regeln   */
 agvu4[ 1] = 1;                /* Alle VUs                           */
 agvn1[43] = 1;                /* Aggregaterzeugung:Versicherte: 43  */
 agvn2[ 1] = 1;                /* Alle VNs mit VR: Zufall I          */
 agvn3[ 1] = 1;                /* Alle VNs mit VK: Infofreie Regeln  */
 agvn4[ 1] = 1;                /* Alle VNs                           */
 clearScreen();
 printfAt( 1,14, "[ Homogenes Angebot bei homogener Nachfrage ]");
 printfAt( 5,15, "Modellkonfiguration:                            ");
 printfAt( 6,15, "Versicherer:         1 ... 25 : Mark Up I       ");
 printfAt( 7,15, "Versicherungsnehmer: 1 ... 200: Zufall I        ");
 printfAt( 8,15, "Besonderheiten:                                 ");
 printfAt( 9,15, " - Versicherer starten mit P1[0]=P2[0] = 30.0   ");
 printfAt(10,15, " - Versicherer legen keine Werbeausgaben fest   ");
 printfAt(11,15, " - Der Parametervektor fuer die Aendungsschock- ");
 printfAt(12,15, "   reaktion ist: (0..0)                         ");
 printfAt(13,15, " - Die Anspruchsniveaureaktion ist in den bei-  ");
 printfAt(14,15, "   den Sparten unterschiedlich                  ");
 printfAt(15,15, " - Die Versicherungsnehmer haben fuer beide     ");
 printfAt(16,15, "   Risiken unterschiedliche Schadenmodelle      ");
 printfAt(17,15, "Erzeugte Aggregatdateien von:                   ");
 printfAt(18,15, "VU[1], VU[17], VU-Verhaltensregel 3, allen VUs  ");
 printfAt(19,15, "die Verhaltensregeln mit Eigeninformation haben,");
 printfAt(20,15, "allen VUs, VN[1], VN-Verhaltensregel 1, allen   ");
 printfAt(21,15, "VNs mit informationsfreien Verhaltensregeln und ");
 printfAt(22,15, "allen VNs                                       ");
 waitKey(); waitKey();
} /* END: func Vdefmd1() */

/* ***************************************************************** */
/* func Vdefmd2() : Vordefinitiertes Modell 2                        */
/*                  Homogenes Angebot bei heterogener Nachfrage      */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd2() {
 int j;                                 /* Schleifenzaehler          */
 Bavauin(100,100,0.0,0.0,0); /* In KEINER Periode, KEINEM Lauf Aen-  */
                             /* derungsschock, Zins, Suchkosten=0.0  */
                             /* KEINE Wiederholungen                 */
 for( j = 1; j <= MAXVU; j++ )
  {                                                 /* Mark Up II    */
   Vuauini(j, 4, 1, 1, 0.0,0.0,0.0,0.0,0.0,0.0, 20.0,10.0,22.0,12.0,
           0.99,0.0 ,1.03,0.0 ,0.98,0.0 ,1.02,0.0 , /* Pramienreakt. */
           0.99,0.0 ,1.02,0.0 ,0.99,0.0 ,1.03,0.0 );/* Werbereaktion */
  }
 for( j = 1; j <= 100; j++ )
  {                                                    /* Zufall II  */
   Vnauini(j, 2, 1, 1, 0,0,0,0, 0.0,
           27.0, 0.0, 5.0, 0.0, 23.0, 0.0, 10.0, 0.0,  /* Schadenfkt.*/
            0.0, 0.0, 0.0, 0.0, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 101; j <= MAXVN; j++ )
  {                                                    /* Praeferenz */
   Vnauini(j, 3, 1, 1, 0,0,0,0, 0.0,
           23.0, 0.0, 5.0, 0.0, 27.0, 0.0,  5.0, 0.0,  /* Schadenfkt.*/
            0.5, 0.5, 0.5, 0.5,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 agvu1[ 4] = 1;                /* Aggregaterzeugung:Versicherer:  4  */
 agvu2[ 4] = 1;                /* Alle VUs mit VR: Mark-Up II        */
 agvu4[ 1] = 1;                /* Alle VUs                           */
 agvn1[56] = 1;                /* Aggregaterzeugung:Versicherte: 56  */
 agvn2[ 2] = 1;                /* Alle VNs mit VR: Zufall II         */
 agvn2[ 3] = 1;                /* Alle VNs mit VR: Praeferenz        */
 agvn4[ 1] = 1;                /* Alle VNs                           */
 clearScreen();
 printfAt( 1,14, "[ Homogenes Angebot bei heterogener Nachfrage ]");
 printfAt( 5,15, "Modellkonfiguration:                             ");
 printfAt( 6,15, "Versicherer:          1.. 25: Mark Up II         ");
 printfAt( 7,15, "Versicherungsnehmer:  1..100: Zufall II          ");
 printfAt( 8,15, "                    101..200: Praeferenz         ");
 printfAt( 9,15, "Besonderheiten:                                  ");
 printfAt(10,15, "- Die Praemienreaktionen der VUs sind in beiden  ");
 printfAt(11,15, "  Sparten unterschiedlich                        ");
 printfAt(12,15, "- Alle VUs haben die gleichen Startwerte         ");
 printfAt(13,15, "- VNs mit VR Zufall II haben groessere Schadener-");
 printfAt(14,15, "  wartungswerte bei Risiko 1, VNs mit VR Praefe- ");
 printfAt(15,15, "  renz haben groessere Schadenerwartung bei      ");
 printfAt(16,15, "  Risiko 2                                       ");
 printfAt(17,15, "- Nur die VNs mit der VR Praeferenz reagieren    ");
 printfAt(18,15, "  auf Werbeausgaben                              ");
 printfAt(19,15, "Erzeugte Aggregatdateien von:                    ");
 printfAt(20,15, "VU[4], allen VUs mit VR Mark Up II, allen VUs,   ");
 printfAt(21,15, "VN[56], allen VNs mit VR Zufall II und allen VNs ");
 printfAt(22,15, "mit VR Praeferenz, allen VNs                     ");
 waitKey(); waitKey();
} /* END: func Vdefmd2() */

/* ***************************************************************** */
/* func Vdefmd3() : Vordefinitiertes Modell 3                        */
/*                  Heterogenes Angebot bei homogener Nachfrage      */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd3() {
 int j;                                 /* Schleifenzaehler          */
 Bavauin(100,100,0.0,0.02,0); /* In KEINER Periode, KEINEM Lauf Aen- */
                            /* derungsschock, Zins = 2 Prozent,      */
                            /* KEINE Suchkosten und Wiederholungen   */
 for( j = 1; j <= 8; j++ )                          /* Mark Up III   */
  {
   Vuauini(j, 5, 1, 1, 0.0,0.0,0.06,0.0,0.0,0.06, 34.0, 0.0, 8.0, 0.0,
           1.008,0.0 ,0.99,0.0 ,1.008,0.0 ,0.99,0.0 , /* Pramienreakt. */
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for( j = 9; j <=16; j++ )                       /* Erwartungsschaden*/
  {
   Vuauini(j, 6, 1, 1, 0.0,0.0,0.0,0.0,0.0,0.0,   34.0, 0.0, 8.0, 0.0,
           1.01,0.0 ,1.0 ,0.0 ,1.01,0.0 ,1.00,0.0 , /* Pramienreakt. */
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for( j =17; j <=MAXVU; j++ )                       /* DUMPING       */
  {
   Vuauini(j, 7, 1, 1, 0.0,0.0,0.0,0.0,0.0,0.0,   34.0, 0.0, 8.0, 0.0,
           1.00,0.0 ,1.00,0.0 ,1.00,0.0 ,1.00,0.0 , /* Pramienreakt. */
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for( j = 1; j <= MAXVN; j++ )                  /* Zufall II         */
  {
   Vnauini(j, 2, 1, 1, 0,0, 0,0, 0.0,
           40.0, 0.0, 5.0, 0.0, 10.0, 0.0,  1.0, 0.0,  /* Schadenfkt.*/
            0.0, 0.0, 0.0, 0.0,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 agvu1[12] = 1;                /* Aggregaterzeugung:Versicherer:12   */
 agvu2[ 5] = 1;                /* Alle VUs mit VR: Mark-Up III       */
 agvu2[ 6] = 1;                /* Alle VUs mit VR: Erwartungsschaden */
 agvu2[ 7] = 1;                /* Alle VUs mit VR: Dumping           */
 agvn3[ 1] = 1;                /* Alle VUs in VK:1 (Info.freie VR)   */
 agvu4[ 1] = 1;                /* Alle VUs                           */
 agvn1[99] = 1;                /* Aggregaterzeugung:Versicherte: 99  */
 agvn2[ 2] = 1;                /* Alle VNs mit VR: Zufall II         */
 clearScreen();
 printfAt( 1,14, "[ Heterogenes Angebot bei homogener Nachfrage ]");
 printfAt( 5,15, "Modellkonfiguration:                            ");
 printfAt( 6,15, "Versicherer:          1..  8: Mark Up III       ");
 printfAt( 7,15, "                      9.. 16: Erwartungsschaden ");
 printfAt( 8,15, "                     17.. 25: Dumping           ");
 printfAt( 9,15, "Versicherungsnehmer:  1..200: Zufall II         ");
 printfAt(10,15, "Besonderheiten:                                 ");
 printfAt(11,15, "- Die VUs mit VR Mark Up III streben einen      ");
 printfAt(12,15, "  ueberdurchschnittlichen Marktanteil an        ");
 printfAt(13,15, "- Keine VU betreibt Werbung aber die verschie-  ");
 printfAt(14,15, "  denen VU-VRs haben gleiche Startwerte und     ");
 printfAt(15,15, "  unterschiedliche Preamienreaktionparameter    ");
 printfAt(16,15, "- Alle VUs[DUMPING] bieten immer genau die      ");
 printfAt(17,15, "  Minimalpraemie der Vorperiode an ohne Auf-    ");
 printfAt(18,15, "  oder Abschlaege                               ");
 printfAt(19,15, "Erzeugte Aggregatdateien von:                   ");
 printfAt(20,15, "Versicherung[12], alle VU-VR: Mark Up III, VU-VR");
 printfAt(21,15, "Erwartungsschaden, VU-VR:Dumping, VU-VK:Eigen-  ");
 printfAt(22,15, "information, VU-VK: Fremdinformation, alle VUs  ");
 printfAt(23,15, "VN[99] und alle VN                              ");
 waitKey(); waitKey();
} /* END: func Vdefmd3() */

/* ***************************************************************** */
/* func Vdefmd4() : Vordefinitiertes Modell 4                        */
/*                  Einfacher Aenderungsschock, homogene Nachfrage   */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd4() {
 int j;                                 /* Schleifenzaehler          */
 Bavauin( 50,0, 0.0, 0.02,1); /* Ab Periode 50 in jedem Lauf:  Aen-  */
                              /* derungsschock, Zins = 2 Prozent ,   */
                              /* KEINE Suchkosten, Wiederholungen    */
 for( j = 1; j <= MAXVU; j++ )
  {                                           /* Mark Up I           */
   Vuauini(j, 3, 1,100,0.0,0.0,0.05,0.0,0.0,0.05, 30.0,0.0,30.0,0.0,
           1.03,1.08,0.97,0.8 ,1.01,1.10,0.98,0.90, /* Pramienreakt. */
           1.01,1.03,0.98,0.97,1.03,1.08,0.97,0.8 );/* Werbereaktion */
  }
 for( j = 1; j <= MAXVN; j++ )
  {
   Vnauini(j, 3, 1,100,0,0,0,0, 0.0,          /* Praeferenz          */
           30.0,15.0,10.0,10.0, 30.0,55.0, 15.0,15.0,  /* Schadenfkt.*/
            0.5, 0.7, 0.5, 0.7,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 agvu1[  7] = 1;agvu1[19] = 1; /* Aggregaterzeugung:Versicherer:7,19 */
 agvu2[  5] = 1;               /* Alle VUs mit VR: Mark-Up III       */
 agvu4[  1] = 1;               /* Alle VUs                           */
 agvn1[119] = 1;               /* Aggregaterzeugung:Versicherte: 119 */
 agvn2[  3] = 1;               /* Alle VNs mit VR: Praeferenz        */
 agvn4[  1] = 1;               /* Alle VNs                           */
 clearScreen();
 printfAt( 1,13, "[ Einfacher Aenderungsschock, homogene Nachfrage ]");
 printfAt( 5,15, "Modellkonfiguration:                            ");
 printfAt( 6,15, "Versicherer:          1..25 : Mark Up I         ");
 printfAt( 7,15, "                      mit Aenderungsschock      ");
 printfAt( 8,15, "Versicherungsnehmer:  1..200: Praeferenz        ");
 printfAt( 9,15, "                      mit Aenderungsschock      ");
 printfAt(10,15, "Besonderheiten:                                 ");
 printfAt(11,15, "- Die VUs mit VR Mark Up I  streben ausge-      ");
 printfAt(12,15, "  glichene Reserven in beiden Sparten an        ");
 printfAt(13,15, "- Auch die Werbeaufwandsparameter sind durch den");
 printfAt(14,15, "  Aenderungsschock beeinflusst                  ");
 printfAt(15,15, "- Praemien und Schaeden reagieren in beiden     ");
 printfAt(16,15, "  Sparten unterschiedlich auf den Schock        ");
 printfAt(17,15, "- Der Schock beeinflusst die Statuswahlfunktion ");
 printfAt(18,15, "  und die Schadenfunktion beider Risiken        ");
 printfAt(19,15, "Erzeugte Aggregatdateien von:                   ");
 printfAt(20,15, "VU[7] und VU[19], alle VUs mit der Verhaltens-  ");
 printfAt(21,15, "regel: Mark Up I,alle VUs,VUs,VN[119] und alle  ");
 printfAt(22,15, "VN mit der Verhaltensregel: Praeferenz          ");
 waitKey(); waitKey();
} /* END: func Vdefmd4() */

/* ***************************************************************** */
/* func Vdefmd5() : Vordefinitiertes Modell 5                        */
/*                  Einfacher Aktivierungsschock, homogenes Angebot  */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd5() {
 int j;                                 /* Schleifenzaehler          */
 Bavauin(100,100,1.0,0.03,1
 ); /* In KEINER Periode, KEINEM Lauf Aen- */
                              /* derungsschock, Kosten pro Praemien- */
                              /* information = 1.0, Zins = 3 Prozent */
                              /* Wiederholungen                      */
 for( j = 1; j <= MAXVU; j++ )
  {                                           /* Erwartungsschaden   */
   Vuauini(j, 6, 1, 100, 0.0,0.0,0.0,0.0,0.0,0.0, 40.0,0.0,35.0,0.0,
           1.03,0.0 ,0.97,0.0 ,1.05,0.0 ,0.95,0.0 , /* Pramienreakt. */
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for( j = 1;   j <= 100  ; j++ )
  {
   Vnauini(j, 2, 1, 100, 0,0,0,0, 0.0,        /* Zufall II           */
           30.0, 0.0,20.0, 0.0, 30.0, 0.0,20.0 , 0.0,  /* Schadenfkt.*/
            0.5, 0.0, 0.5, 0.0, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 101; j <= MAXVN; j++ )
  {
   Vnauini(j, 1,50, 100, 0,0,0,0, 0.0,        /* Zufall I            */
           50.0, 0.0, 5.0, 0.0, 50.0, 0.0,  5.0, 0.0,  /* Schadenfkt.*/
            0.0, 0.0, 0.0, 0.0, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 for( j = 1; j <= MAXVU; j++ ) { agvu1[j] = 1; } /* Alle Einzel-VUs  */
 agvu4[  1] = 1;               /* Alle VUs                           */
 agvn2[  1] = 1;               /* Alle VNs mit VR: Zufall I          */
 agvn2[  2] = 1;               /* Alle VNs mit VR: Zufall II         */
 agvn4[  1] = 1;               /* Alle VNs                           */
 clearScreen();
 printfAt( 1,13, "[ Einfacher Aktivierungsschock, homogenes Angebot ]");
 printfAt( 5,15, "Modellkonfiguration:                            ");
 printfAt( 6,15, "Versicherer:          1..25 : Erwartungsschaden ");
 printfAt( 7,15, "Versicherungsnehmer:  1..100: Zufall II         ");
 printfAt( 8,15, "                    101..200: Zufall I, t > 50  ");
 printfAt( 9,15, "                    mit Aktivierungsschock      ");
 printfAt(10,15, "Besonderheiten:                                 ");
 printfAt(11,15, "- Die VUs haben fuer beide Sparten unterschied- ");
 printfAt(12,15, "  liche Startwerte in den Praemien              ");
 printfAt(13,15, "- Keine VU betreibt Werbung                     ");
 printfAt(14,15, "- Es findet nur ein Aktivierungsschock auf der  ");
 printfAt(15,15, "  Nachfrageseite statt, kein Aenderungsschock   ");
 printfAt(16,15, "- Die VNs[101..200], die in t>50 aktiviert wer- ");
 printfAt(17,15, "  den, haben andere Schadenparamter als die     ");
 printfAt(18,15, "  VNs[1..100]                                   ");
 printfAt(19,15, "Erzeugte Aggregatdateien von:                   ");
 printfAt(20,15, "Alle VUs (Aggregat I), alle VUs (Aggregat IV),  ");
 printfAt(21,15, "alle VNs mit VR[Zufall I] und VR[Zufall II] und ");
 printfAt(22,15, "alle VNs (Aggregat IV)                          ");
 waitKey(); waitKey();
} /* END: func Vdefmd5() */

/* ***************************************************************** */
/* func Vdefmd6() : Vordefinitiertes Modell 6                        */
/*                  Komplexer Marktschock: Die Wiedervereinigung     */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Vdefmd6() {
 int j;                                           /*Schleifenzaehler */
 Bavauin( 50,0, 0.8, 0.02,1); /* Ab Periode 50 in jedem Lauf:  Aen-  */
                              /* derungsschock, Kosten pro Praemien- */
                              /* information = 0.8, Zins = 2 Prozent */
                              /* Wiederholungen sind erlaubt         */
 for ( j =  1; j <=  2   ; j++)
  {                                               /* Zufall I        */
   Vuauini(j, 1,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,0.0,40.0,0.0,
           60.0,70.0,50.0,40.0,20.0,20.0,20.0,20.0, /*Pramienreaktion*/
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/*Werbereaktion  */
  }
 for ( j =  3; j <=  4   ; j++)
  {                                                /* Zufall II      */
   Vuauini(j, 2,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,10.0,40.0,10.0,
           30.0,40.0,5.0 ,7.0 ,30.0,40.0,5.0 ,8.0 , /*Pramienreaktion*/
           10.0,10.0,0.0 ,0.0 ,10.0,10.0,0.0 ,0.0 );/*Werbereaktion  */
  }
 for ( j =  5; j <=  7   ; j++)
  {                                               /* Mark Up I       */
   Vuauini(j, 3,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,10.0,40.0,10.0,
           1.03,1.1 ,0.97,0.9 ,1.04,1.05,0.97,0.99, /*Pramienreaktion*/
           1.03,1.1 ,0.97,0.9 ,1.08,1.01,0.92,0.99);/*Werbereaktion  */
  }
 for ( j =  8; j <= 10   ; j++)
  {                                               /* Mark Up II      */
   Vuauini(j, 4,1,100, 0.0,2.0,0.0,0.2,0.0,0.0,  40.0,10.0,40.0,10.0,
           1.008,1.01,0.99,0.98,1.008,1.01,0.99,0.98,/*Pramienreaktion*/
           1.008,1.01,0.97,1.0 ,1.05,1.0 ,0.95,1.0 );/*Werbereaktion  */
  }
 for ( j = 11; j <= 13   ; j++)
  {                                               /* Mark Up III     */
   Vuauini( j,5,1,100, 0.0,0.0,0.04,0.0,0.0,0.04,  40.0,10.0,40.0,10.0,
           1.01,1.02,0.99,0.98,1.008,1.01,0.99,0.98,/*Pramienreaktion*/
           1.02,1.03,0.98,1.01,1.02,1.03,0.98,1.0 );/*Werbereaktion  */
  }
                             /* VU[14] = Allianz: Erwartungsschaden */
 Vuauini( 14,6,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,10.0,40.0,10.0,
          1.02,1.03,0.98,0.99,1.02,1.01,0.98,0.99, /*Pramienreaktion*/
          1.0 ,1.06,1.03,1.06,1.0 ,1.06,1.03,1.06);/*Werbereaktion  */
 for ( j = 15; j <= 16   ; j++)
  {                                               /*Erwartungsschaden*/
   Vuauini( j,6,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,10.0,40.0,10.0,
           1.02,1.03,0.98,0.99,1.02,1.01,0.98,0.99, /*Pramienreaktion*/
           1.05,1.08,0.95,0.97,1.09,1.06,0.95,0.97);/*Werbereaktion  */
  }
 for ( j = 17; j <= 19   ; j++)
  {                                               /* Dumping         */
   Vuauini( j,7,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0, 0.0,40.0, 0.0,
           1.07,1.04,1.07,1.04,1.07,1.04,1.07,1.04, /*Pramienreaktion*/
           0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion */
  }
 for ( j = 20; j <= 22   ; j++)
  {                                               /* Durchschnitt    */
   Vuauini( j,8,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,10.0,40.0,10.0,
           0.0 ,0.0 ,1.0 ,1.0 ,0.0 ,0.0 ,1.0 ,1.0 ,/*Pramienreaktion */
           0.0 ,0.0 ,1.0 ,1.0 ,0.0 ,0.0 ,1.0 ,1.0 );/* Werbereaktion */
  }
 for ( j = 23; j <= MAXVU; j++)
  {                                               /* Angriff         */
   Vuauini( j,9,1,100, 0.0,0.0,0.0,0.0,0.0,0.0,  40.0,0.0,40.0,0.0,
         0.0 ,0.0 ,0.99,0.95,0.0 ,0.0 ,0.99,0.95, /* Pramienreaktion */
         0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 );/* Werbereaktion   */
  }
 for( j = 1;   j <= 15  ; j++ )
  {Vnauini( j,1,1,100, 0,0,0,0, 0.0,          /* Zufall I            */
           30.0,30.0, 5.0, 5.0, 30.0,30.0, 5.0 , 5.0,  /* Schadenfkt.*/
            0.0, 0.0, 0.0, 0.0, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 16;  j <= 30  ; j++ )
  {Vnauini( j,2,1,100, 0,0,0,0, 0.0,          /* Zufall II           */
           30.0,30.0, 5.0, 5.0, 30.0,30.0, 5.0 , 5.0,  /* Schadenfkt.*/
            0.5, 0.5, 0.5, 0.5, 0.0 , 0.0, 0.0 , 0.0); /* VR-Paramet.*/
  }
 for( j = 31;  j <= 60  ; j++ )
  {Vnauini( j,3,1,100, 0,0,0,0, 0.0,          /* Praeferenz          */
           30.0,30.0, 5.0, 5.0, 30.0,30.0,  5.0, 5.0,  /* Schadenfkt.*/
            0.3, 0.3, 0.3, 0.3,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 61;  j <= 90  ; j++ )
  {Vnauini( j,4,1,100, 0,0,0,0, 0.0,          /* Totale Erinnerung   */
           30.0,30.0, 5.0, 5.0, 30.0,30.0,  5.0, 5.0,  /* Schadenfkt.*/
            0.3, 0.3, 0.3, 0.3,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 91;  j <= 120 ; j++ )
  {Vnauini( j,5,1,100, 0,0,0,0, 0.0,          /* Suche               */
           30.0,30.0, 5.0, 5.0, 30.0,30.0,  5.0, 5.0,  /* Schadenfkt.*/
            0.3, 0.3, 0.3, 0.3,  8.0,10.0,  8.0,10.0); /* VR-Paramet.*/
  }
 for( j =121;  j <= 150 ; j++ )
  {Vnauini( j,6,1,100, 0,0,0,0, 0.0,          /* Beste Information   */
           30.0,30.0, 5.0, 5.0, 30.0,30.0,  5.0, 5.0,  /* Schadenfkt.*/
            0.5, 0.5, 0.5, 0.5,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j =151;  j <= 190 ; j++ )
  {Vnauini( j,3,50,100, 0, 0,0, 0, 0.0,       /* Praeferenz          */
           50.0,50.0,15.0,15.0, 50.0,50.0, 15.0,15.0,  /* Schadenfkt.*/
            0.9, 0.9, 0.9, 0.9,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }    /* Die aktivierten VNs gehen zunaechst alle zur Allianz       */
 for( j =191;  j<= MAXVN; j++ ) /* ..und haben andere Schadenparamtr.*/
  {Vnauini( j,2,50,100, 0, 0,0, 0, 0.0,       /* Zufall II           */
           50.0,50.0,15.0,15.0, 50.0,50.0, 15.0,15.0,  /* Schadenfkt.*/
            0.9, 0.9, 0.9, 0.9,  0.0, 0.0,  0.0, 0.0); /* VR-Paramet.*/
  }
 for( j = 0; j <= MAXVU; j++ ) { agvu1[j] = 0; } /* Alle Aggregat-   */
 for( j = 0; j <= 10;    j++ ) { agvu2[j] = 0; } /* vektoren auf Null*/
 for( j = 0; j <= 3;     j++ ) { agvu3[j] = 0; } /* setzen, damit bei*/
 for( j = 0; j <= 1;     j++ ) { agvu4[j] = 0; } /* wiederholter Mo- */
 for( j = 0; j <= MAXVN; j++ ) { agvn1[j] = 0; } /* dellwahl nicht   */
 for( j = 0; j <= 7;     j++ ) { agvn2[j] = 0; } /* die Aggregate des*/
 for( j = 0; j <= 3;     j++ ) { agvn3[j] = 0; } /* letzten Modells  */
 for( j = 0; j <= 1;     j++ ) { agvn4[j] = 0; } /* erzeugt werden   */
 agvu1[ 14] = 1;               /* Aggregaterzeugung:VU[14] = Allianz */
 for( j = 1; j <= 9; j++ ) { agvu2[j] = 1; } /* Alle VU-Aggregate der*/
 for( j = 1; j <= 3; j++ ) { agvu3[j] = 1; } /* Stufe II und III     */
 agvu4[  1] = 1;               /*                   Alle Versicherer */
 for( j = 1; j <= 6; j++ ) { agvn2[j] = 1; } /* Alle Aggregate der   */
 for( j = 1; j <= 3; j++ ) { agvn3[j] = 1; } /* Stufe II und III     */
 agvn4[1] = 1;                 /*          Alle Versicherungsnehmer  */
 clearScreen();
 printfAt( 1,13, "[ Komplexer Marktschock: Die Wiedervereinigung ]");
 printfAt( 5,15, "Modellkonfiguration:                            ");
 printfAt( 6,15, "Versicherer:                                    ");
 printfAt( 7,15, "   1..  2: Zufall I    14..16: Erwartungsschaden");
 printfAt( 8,15, "   3..  4: Zufall II   17..19: Dumping          ");
 printfAt( 9,15, "   5..  7: Mark Up I   20..22: Durchschnitt     ");
 printfAt(10,15, "   8.. 10: Mark Up II  23..25: Angriff          ");
 printfAt(11,15, "  11.. 13: Mark Up III                          ");
 printfAt(12,15, "Versicherungssnehmer:                           ");
 printfAt(13,15, "   1.. 15: Zufall I                             ");
 printfAt(14,15, "  16.. 30: Zufall II                            ");
 printfAt(15,15, "  31.. 60: Praeferenz                           ");
 printfAt(16,15, "  61.. 90: Totale Erinnerung                    ");
 printfAt(17,15, "  91..120: Suche                                ");
 printfAt(18,15, " 121..150: Beste Information                    ");
 printfAt(19,15, " 151..180: Praeferenz        , t > 50           ");
 printfAt(20,15, " 181..200: Zufall II,        , t > 50           ");
 printfAt(21,15, "Aenderungsschock: bei VUs und VNs in t = 50     ");
 printfAt(22,15, "Weitere Informationen: siehe Kapitel 5.4. ff.   ");
 waitKey(); waitKey();
} /* END: func Vdefmd6() */

/* ***************************************************************** */
/* func Erstvu()  : Versicherer erstellen                            */
/*                                                                   */
/*                  Aufgerufen von func Moderst()                    */
/* ***************************************************************** */
func Erstvu() {
 int j,ende;                           /* Lokale Variable vereinbaren*/
 int i;                                /* Schleifenzaehler           */
 float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,
       pr1t1,wa1t1,pr2t1,wa2t1,an1,an2;
 int st,ap,al;
do { /* while ( ende != 1) */
 clearScreen();                        /* Maske aufbauen             */
 box( 0, 0, 8,80); box( 8, 0, 8,80); box(16, 0, 8,80);
 box( 0, 0, 3,80); box( 8, 0, 2,80); box(16, 0, 2,80);
 box( 0, 0,24,40); box( 0,40,24,40);
 printfAt( 1,25, "[ Versicherer konfigurieren ]");
 printfAt( 2,10, "Versicherer          : ");
 printfAt( 2,50, "Startwerte d. Sparten: ");
 printfAt( 9,10, "Aktivierungsschockparamter: ");
 printfAt( 9,50, "Anspruchsniveaus     : ");
 printfAt(17,10, "Vor Aenderungsschock : ");
 printfAt(17,50, "Nach Aenderungsschock: ");
 printfAt( 4,10, "VR[                  ]");
 printfAt( 5,10, "Verhaltensregelklasse: ");
 printfAt( 6,10, "Aggregatdatei(0=nein): ");
 printfAt( 4,50, "Praemie, Sparte 1    : ");
 printfAt( 5,50, "Werbung, Sparte 1    : ");
 printfAt( 6,50, "Praemie, Sparte 2    : ");
 printfAt( 7,50, "Werbung, Sparte 2    : ");
 printfAt(11,10, "Aktivierungslauf     : ");
 printfAt(12,10, "Aktivierungsperiode  : ");
 printfAt(11,50, "Fuer Sparte 1        : ");
 printfAt(12,50, "Fuer Sparte 2        : ");
 printfAt(19,10, "a  :              e  : ");
 printfAt(20,10, "b  :              f  : ");
 printfAt(21,10, "c  :              g  : ");
 printfAt(22,10, "d  :              h  : ");
 printfAt(19,50, "a* :              e* : ");
 printfAt(20,50, "b* :              f* : ");
 printfAt(21,50, "c* :              g* : ");
 printfAt(22,50, "d* :              h* : ");
 do {                             /* Zu bearbeitenden VU erfragen    */
     printfAt( 2,33,"[    ]");scanfAt( 2,34,"%d",&j);
    } while ( ( j < 1 ) || ( j > MAXVU) );
 st    = VU[ j ].DatenVU->Ac[1].st;         /* Daten auslesen        */
 ap    = VU[ j ].DatenVU->Ap;
 for( i = SIMLAENGE ; i >= 1 ; i--)   /* Aktivierungslaeufe          */
  { if (VU[j].DatenVU->Al[i] == 0) { al = i - 1; } }
 pr1t1 = VU[ j ].DatenVU->Sp[1].l.Pr[1];
 pr2t1 = VU[ j ].DatenVU->Sp[2].k.Pr[1];
 wa1t1 = VU[ j ].DatenVU->Sp[1].l.Wa[1];
 wa2t1 = VU[ j ].DatenVU->Sp[2].k.Wa[1];
 switch(st) /* ... nach der Abhaengigkeit der Verhaltensregel...     */
  {
   case 3: /* Anspruchsniveau fuer MARK-UP I, II oder III auslesen...*/
      an1 = VU[j].DatenVU->A1[1]; an2 = VU[j].DatenVU->A2[1];
    break;
   case 4:
      an1 = VU[j].DatenVU->A1[2]; an2 = VU[j].DatenVU->A2[2];
    break;
   case 5:
      an1 = VU[j].DatenVU->A1[3]; an2 = VU[j].DatenVU->A2[3];
    break;
   default:
      an1 = 0.0                 ; an2 = 0.0                 ;
    break;
  } /* END: switch(st) */
 a0 = VU[ j ].DatenVU->Pv[0 ]; a1 = VU[ j ].DatenVU->Pv[1 ];
 b0 = VU[ j ].DatenVU->Pv[2 ]; b1 = VU[ j ].DatenVU->Pv[3 ];
 c0 = VU[ j ].DatenVU->Pv[4 ]; c1 = VU[ j ].DatenVU->Pv[5 ];
 d0 = VU[ j ].DatenVU->Pv[6 ]; d1 = VU[ j ].DatenVU->Pv[7 ];
 e0 = VU[ j ].DatenVU->Pv[8 ]; e1 = VU[ j ].DatenVU->Pv[9 ];
 f0 = VU[ j ].DatenVU->Pv[10]; f1 = VU[ j ].DatenVU->Pv[11];
 g0 = VU[ j ].DatenVU->Pv[12]; g1 = VU[ j ].DatenVU->Pv[13];
 h0 = VU[ j ].DatenVU->Pv[14]; h1 = VU[ j ].DatenVU->Pv[15];
                                          /* Daten ausgeben          */
 printfAt( 4, 13,"%18s" , vrvunm[st]); /* Voller Name der VR         */
 printfAt( 5, 34,"%1d"  , vkrvu[st] );
 printfAt( 6, 34,"%1d"  , agvu1[j]  );
 printfAt( 4, 73,"%3.1f", pr1t1     );
 printfAt( 5, 73,"%3.1f", wa1t1     );
 printfAt( 6, 73,"%3.1f", pr2t1     );
 printfAt( 7, 73,"%3.1f", wa2t1     );
 switch(st) /*... nach der Abhaengigkeit der Verhaltensregel...      */
  {
   case 3: /* Anspruchsniveau fuer MARK-UP I                         */
    printfAt( 9,50, "VR[ MARK-UP I   ] ");
    printfAt(11,74, "%3.2f", an1); printfAt(12,74, "%3.2f", an2);
    break;
   case 4:
    printfAt( 9,50, "VR[ MARK-UP II  ] ");
    printfAt(11,74, "%3.2f", an1); printfAt(12,74, "%3.2f", an2);
    break;
   case 5:
    printfAt( 9,50, "VR[ MARK-UP III ] ");
    printfAt(11,74, "%3.2f", an1); printfAt(12,74, "%3.2f", an2);
    break;
   default:
    printfAt( 9,50, "[Kein Anspruchsniveau ] ");
    printfAt(11,50, "                             ");
    printfAt(12,50, "                             ");           
    break;
  } /* END: switch(st) */
 printfAt(11,34,"%3d",al);
 printfAt(12,34,"%3d",ap);
 printfAt(19,15,"%3.2f",a0); printfAt(19,33,"%3.2f",e0);
 printfAt(20,15,"%3.2f",b0); printfAt(20,33,"%3.2f",f0);
 printfAt(21,15,"%3.2f",c0); printfAt(21,33,"%3.2f",g0);
 printfAt(22,15,"%3.2f",d0); printfAt(22,33,"%3.2f",h0);
 printfAt(19,55,"%3.2f",a1); printfAt(19,73,"%3.2f",e1);
 printfAt(20,55,"%3.2f",b1); printfAt(20,73,"%3.2f",f1);
 printfAt(21,55,"%3.2f",c1); printfAt(21,73,"%3.2f",g1);
 printfAt(22,55,"%3.2f",d1); printfAt(22,73,"%3.2f",h1);
 do {                    /* Neue Parameter abfragen und  pruefen ... */
     printfAt( 4,34,"[    ]");
     scanfAt(  4,35, "%d", &st);
    } while ( ( st < 1 ) || ( st > 10 ) );
 printfAt( 4, 13,"%18s" , vrvunm[st]); /* Voller Name der VR         */
 printfAt( 5, 34,"%1d"  , vkrvu[st] );
 do {
     printfAt( 6,34,"[    ]"); scanfAt(  6,35, "%d", &agvu1[j]);
    } while ( ( agvu1[j] < 0 ) || ( agvu1[j] > 1 ) );
 do {
     printfAt( 4,73,"[    ]"); scanfAt(  4,74, "%f", &pr1t1 );
    } while ( ( pr1t1 < 0.0 ) || ( pr1t1 > 100.0 ) );
 do {
     printfAt( 5,73,"[    ]"); scanfAt(  5,74, "%f", &wa1t1 );
    } while ( ( wa1t1 < 0.0 ) || ( wa1t1 > 100.0 ) );
 do {
     printfAt( 6,73,"[    ]"); scanfAt(  6,74, "%f", &pr2t1 );
    } while ( (  pr2t1 < 0.0 ) || (  pr2t1 > 100.0 ) );
 do {
     printfAt( 7,73,"[    ]"); scanfAt(  7,74, "%f", &wa2t1 );
    } while ( ( wa2t1  < 0.0 ) || ( wa2t1 > 100.0 ) );
 do {
     printfAt(11,34,"[    ]"); scanfAt( 11,35, "%d", &al    );
    } while ( (    al  < 1   ) || (    al > 100   ) );
 do {
     printfAt(12,34,"[    ]"); scanfAt( 12,35, "%d", &ap    );
    } while ( (    ap  < 1   ) || (    ap > 100   ) );
 switch(st)
  {
   case 3: /* Anspruchsniveau fuer MARK-UP I  (Reserven)             */
    printfAt( 9,50, "Anspruchsniveaus     :  ");                        
    printfAt(11,50, "Fuer Sparte 1        : ");
    printfAt(12,50, "Fuer Sparte 2        : ");
    do {
        printfAt(11,73,"[    ]"); scanfAt( 11,74, "%f", &an1   );
       } while ( (    an1 < -1000.0 ) || (   an1 > 1000.0 ) );
    do {
        printfAt(12,73,"[    ]"); scanfAt( 12,74, "%f", &an2   );
       } while ( (    an2 < -1000.0 ) || (   an2 > 1000.0 ) );
    break;
   case 4: /* Anspruchsniveau fuer MARK-UP II (Nettowechsler)        */
    printfAt( 9,50, "Anspruchsniveaus     :  ");
    printfAt(11,50, "Fuer Sparte 1        : ");
    printfAt(12,50, "Fuer Sparte 2        : ");
    do {
        printfAt(11,73,"[    ]"); scanfAt( 11,74, "%f", &an1   );
       } while ( (    an1 <   -50.0 ) || (   an1 >   50.0 ) );
    do {
        printfAt(12,73,"[    ]"); scanfAt( 12,74, "%f", &an2   );
       } while ( (    an2 <   -50.0 ) || (   an2 >   50.0 ) );
    break;
   case 5:  /* Anspruchsniveau fuer MARK-UP III (Marktanteil)         */
    printfAt( 9,50, "Anspruchsniveaus     :  ");                                                
    printfAt(11,50, "Fuer Sparte 1        : ");
    printfAt(12,50, "Fuer Sparte 2        : ");   
    do {
        printfAt(11,73,"[    ]"); scanfAt( 11,74, "%f", &an1   );
       } while ( (    an1 <     0.0 ) || (   an1 >    1.0 ) );
    do {
        printfAt(12,73,"[    ]"); scanfAt( 12,74, "%f", &an2   );
       } while ( (    an2 <     0.0 ) || (   an2 >    1.0 ) );
    break;
   default:
    printfAt( 9,50, "[Kein Anspruchsniveau ] ");
    printfAt(11,50, "                             ");
    printfAt(12,50, "                             ");
    break;
  } /* END: switch(st) */
  do {
      printfAt(19,15,"[    ]"); scanfAt( 19,16, "%f", &a0    );
     } while ( (     a0 <     0.0 ) || (    a0 >  100.0 ) );
  do {
      printfAt(20,15,"[    ]"); scanfAt( 20,16, "%f", &b0    );
     } while ( (     b0 <     0.0 ) || (    b0 >  100.0 ) );
  do {
      printfAt(21,15,"[    ]"); scanfAt( 21,16, "%f", &c0    );
     } while ( (     c0 <     0.0 ) || (    c0 >  100.0 ) );
  do {
      printfAt(22,15,"[    ]"); scanfAt( 22,16, "%f", &d0    );
     } while ( (     d0 <     0.0 ) || (    d0 >  100.0 ) );
  do {
      printfAt(19,33,"[    ]"); scanfAt( 19,34, "%f", &e0    );
     } while ( (     e0 <     0.0 ) || (    e0 >  100.0 ) );
  do {
      printfAt(20,33,"[    ]"); scanfAt( 20,34, "%f", &f0    );
     } while ( (     f0 <     0.0 ) || (    f0 >  100.0 ) );
  do {
      printfAt(21,33,"[    ]"); scanfAt( 21,34, "%f", &g0    );
     } while ( (     g0 <     0.0 ) || (    g0 >  100.0 ) );
  do {
      printfAt(22,33,"[    ]"); scanfAt( 22,34, "%f", &h0    );
     } while ( (     h0 <     0.0 ) || (    h0 >  100.0 ) );
  do {
      printfAt(19,55,"[    ]"); scanfAt( 19,56, "%f", &a1    );
     } while ( (     a1 <     0.0 ) || (    a1 >  100.0 ) );
  do {
      printfAt(20,55,"[    ]"); scanfAt( 20,56, "%f", &b1    );
     } while ( (     b1 <     0.0 ) || (    b1 >  100.0 ) );
  do {
      printfAt(21,55,"[    ]"); scanfAt( 21,56, "%f", &c1    );
     } while ( (     c1 <     0.0 ) || (    c1 >  100.0 ) );
  do {
      printfAt(22,55,"[    ]"); scanfAt( 22,56, "%f", &d1    );
     } while ( (     d1 <     0.0 ) || (    d1 >  100.0 ) );
  do {
      printfAt(19,73,"[    ]"); scanfAt( 19,74, "%f", &e1    );
     } while ( (     e1 <     0.0 ) || (    e1 >  100.0 ) );
  do {
      printfAt(20,73,"[    ]"); scanfAt( 20,74, "%f", &f1    );
     } while ( (     f1 <     0.0 ) || (    f1 >  100.0 ) );
  do {
      printfAt(21,73,"[    ]"); scanfAt( 21,74, "%f", &g1    );
     } while ( (     g1 <     0.0 ) || (    g1 >  100.0 ) );
  do {
      printfAt(22,73,"[    ]"); scanfAt( 22,74, "%f", &h1    );
     } while ( (     h1 <     0.0 ) || (    h1 >  100.0 ) );
 switch(st)                 /* Aufruf der Initialisierungsfunktion : */
  {
   case 3: /* Anspruchsniveau fuer MARK-UP I  (Reserven)             */
   Vuauini( j,st,al,ap,an1,an2,0.0,0.0,0.0,0.0,pr1t1,wa1t1,pr2t1,wa2t1,
           a0  ,  a1,  b0,  b1,  c0,  c1,  d0,  d1, /*Pramienreaktion*/
           e0  ,  e1,  f0,  f1,  g0,  g1,  h0,  h1);/*Werbereaktion  */
    break;
   case 4: /* Anspruchsniveau fuer MARK-UP II (Nettowechsler)        */
   Vuauini( j,st,al,ap,0.0,0.0,an1,an2,0.0,0.0,pr1t1,wa1t1,pr2t1,wa2t1,
           a0  ,  a1,  b0,  b1,  c0,  c1,  d0,  d1, /*Pramienreaktion*/
           e0  ,  e1,  f0,  f1,  g0,  g1,  h0,  h1);/*Werbereaktion  */
    break;
   case 5: /* Anspruchsniveau fuer MARK-UP III (Marktanteil)         */
   Vuauini( j,st,al,ap,0.0,0.0,0.0,0.0,an1,an2,pr1t1,wa1t1,pr2t1,wa2t1,
           a0  ,  a1,  b0,  b1,  c0,  c1,  d0,  d1, /*Pramienreaktion*/
           e0  ,  e1,  f0,  f1,  g0,  g1,  h0,  h1);/*Werbereaktion  */
    break;
   default:
    break;
  } /* END: switch(st) */
 for(i=1;i<=MAXVU;i++)       /* Automatische agvux[.]-Zuweisung an   */
  {                          /* die Aggregatdateien, die gebraucht   */
   BAV[1].DatenBAV.Vuag2[ VU[j].DatenVU->Vr ]++; /* werden           */
   BAV[1].DatenBAV.Vuag3[ VU[j].DatenVU->Vk ]++;
  }
 for( i = 1;  i <=    10 ; i++ )
  { if ( BAV[1].DatenBAV.Vuag2[i] > 0 ) { agvu2[i] = 1;} }
 for( i = 1;  i <=     3 ; i++ )
  { if ( BAV[1].DatenBAV.Vuag3[i] > 0 ) { agvu3[i] = 1;} }
 agvu4[1] = 1; /* Die Subjektklasse der Versicherer: immer erzeugen  */
 printfAt(24,35,"[ [1] Ruecksprung [0] Weitere VU [    ]  ]");
 scanfAt( 24,70, "%d", &ende);
 } while ( ende != 1);
} /* END: func Erstvu() */

/* ***************************************************************** */
/* func Erstvn()  : Versicherungsnehmer erstellen                    */
/*                                                                   */
/*                  Aufgerufen von func Moderst()                    */
/* ***************************************************************** */
func Erstvn() {
 int j,ende;                           /* Lokale Variable vereinbaren*/
 int i;                                /* Schleifenzaehler           */
 int vr1,vr2,r1,r2, st,ap,al;
 float a0,a1,b0,b1,c0,c1,d0,d1,e0,e1,f0,f1,g0,g1,h0,h1,vm;
 do { /* while ende != 1 */
 clearScreen();                        /* Maske aufbauen             */
 box( 0, 0, 8,80); box( 8, 0, 8,80); box(16, 0, 8,80);
 box( 0, 0, 3,80); box( 8, 0, 2,80); box(16, 0, 2,80);
 box( 0, 0,24,40); box( 0,40,24,40);
 printfAt( 1,22, "[ Versicherungsnehmer konfigurieren ]");
 printfAt( 2,10, "Versicherungsnehmer  : ");
 printfAt( 2,50, "Startwerte d. Risiken: ");
 printfAt( 9,10, "Aktivierungsschockparamter: ");
 printfAt( 9,50, "Anfangsausstattung   : ");
 printfAt(17,10, "Vor Aenderungsschock : ");
 printfAt(17,50, "Nach Aenderungsschock: ");
 printfAt( 4,10, "VR[                  ]");
 printfAt( 5,10, "Verhaltensregelklasse: ");
 printfAt( 6,10, "Aggregatdatei(0=nein): ");
 printfAt( 4,50, "Status      Risiko 1 : ");
 printfAt( 5,50, "Versicherer Risiko 1 : ");
 printfAt( 6,50, "Status      Risiko 2 : ");
 printfAt( 7,50, "Versicherer Risiko 2 : ");
 printfAt(11,10, "Aktivierungslauf     : ");
 printfAt(12,10, "Aktivierungsperiode  : ");
 printfAt(11,50, "Gesamtvermoegen      : ");
 printfAt(19,10, "a  :              e  : ");
 printfAt(20,10, "b  :              f  : ");
 printfAt(21,10, "c  :              g  : ");
 printfAt(22,10, "d  :              h  : ");
 printfAt(19,50, "a* :              e* : ");
 printfAt(20,50, "b* :              f* : ");
 printfAt(21,50, "c* :              g* : ");
 printfAt(22,50, "d* :              h* : ");
 do {                             /* Zu bearbeitenden VN erfragen    */
     scanfAt( 2,33,"%d",&j);
    } while ( ( j < 1 ) || ( j > MAXVN) );
 st    = VN[ j ].DatenVN->Ac[1].st;         /* Daten auslesen        */
 ap    = VN[ j ].DatenVN->Ap;
 for( i = SIMLAENGE ; i >= 1 ; i--)   /* Aktivierungslaeufe          */
  { if (VN[j].DatenVN->Al[i] == 0) { al = i - 1; } }
 vr1 = VN[ j ].DatenVN->Rk[1].l.Vs[1];
 vr2 = VN[ j ].DatenVN->Rk[2].k.Vs[1];
 r1  = VN[ j ].DatenVN->Rk[1].l.Vu[1];
 r2  = VN[ j ].DatenVN->Rk[2].k.Vu[1];
 vm = VN[ j ].DatenVN->Vm[1];
 a0 = VN[ j ].DatenVN->Pv[0 ]; a1 = VN[ j ].DatenVN->Pv[1 ];
 b0 = VN[ j ].DatenVN->Pv[2 ]; b1 = VN[ j ].DatenVN->Pv[3 ];
 c0 = VN[ j ].DatenVN->Pv[4 ]; c1 = VN[ j ].DatenVN->Pv[5 ];
 d0 = VN[ j ].DatenVN->Pv[6 ]; d1 = VN[ j ].DatenVN->Pv[7 ];
 e0 = VN[ j ].DatenVN->Pv[8 ]; e1 = VN[ j ].DatenVN->Pv[9 ];
 f0 = VN[ j ].DatenVN->Pv[10]; f1 = VN[ j ].DatenVN->Pv[11];
 g0 = VN[ j ].DatenVN->Pv[12]; g1 = VN[ j ].DatenVN->Pv[13];
 h0 = VN[ j ].DatenVN->Pv[14]; h1 = VN[ j ].DatenVN->Pv[15];
                                          /* Daten ausgeben          */
 printfAt( 4, 13,"%18s" , vrvnnm[st]); /* Voller Name der VR         */
 printfAt( 5, 34,"%1d"  , vkrvn[st] );
 printfAt( 6, 34,"%1d"  , agvn1[j]  );
 printfAt( 4, 73,"%2d"  , vr1       );
 printfAt( 5, 73,"%2d"  , r1        );
 printfAt( 6, 73,"%2d"  , vr2       );
 printfAt( 7, 73,"%2d"  , r2        );
 printfAt(11, 74,"%4.2f", vm        );
 printfAt(11, 34,"%3d"  ,al);
 printfAt(12, 34,"%3d"  ,ap);
 printfAt(19, 15,"%3.2f",a0); printfAt(19,33,"%3.2f",e0);
 printfAt(20, 15,"%3.2f",b0); printfAt(20,33,"%3.2f",f0);
 printfAt(21, 15,"%3.2f",c0); printfAt(21,33,"%3.2f",g0);
 printfAt(22, 15,"%3.2f",d0); printfAt(22,33,"%3.2f",h0);
 printfAt(19, 55,"%3.2f",a1); printfAt(19,73,"%3.2f",e1);
 printfAt(20, 55,"%3.2f",b1); printfAt(20,73,"%3.2f",f1);
 printfAt(21, 55,"%3.2f",c1); printfAt(21,73,"%3.2f",g1);
 printfAt(22, 55,"%3.2f",d1); printfAt(22,73,"%3.2f",h1);
 do {                    /* Neue Parameter abfragen und  pruefen ... */
     printfAt( 4,34,"[    ]");
     scanfAt(  4,35, "%d", &st);
    } while ( ( st < 1 ) || ( st > 7 ) );
 printfAt( 4, 13,"%18s" , vrvnnm[st]); /* Voller Name der VR         */
 printfAt( 5, 34,"%1d"  , vkrvn[st] );
 do {
     printfAt( 6,34,"[    ]"); scanfAt(  6,35, "%d", &agvn1[j]);
    } while ( ( agvn1[j] < 0 ) || ( agvn1[j] > 1 ) );
 do {
     printfAt( 4,73,"[    ]"); scanfAt(  4,74, "%d", &vr1   );
    } while ( ( vr1   < 0   ) || ( vr1   >    1  ) );
 do {
     printfAt( 5,73,"[    ]"); scanfAt(  5,74, "%d", &r1    );
    } while ( ( r1    < 0   ) || ( r1    > MAXVU ) );
 do {
     printfAt( 6,73,"[    ]"); scanfAt(  6,74, "%d", &vr2   );
    } while ( (  vr2   < 0   ) || (  vr2   >  1    ) );
 do {
     printfAt( 7,73,"[    ]"); scanfAt(  7,74, "%d", &r2    );
    } while ( ( r2     < 0   ) || ( r2    > MAXVU ) );
 do {
     printfAt(11,34,"[    ]"); scanfAt( 11,35, "%d", &al    );
    } while ( (    al  < 1   ) || (    al > 100   ) );
 do {
     printfAt(12,34,"[    ]"); scanfAt( 12,35, "%d", &ap    );
    } while ( (    ap  < 1   ) || (    ap > 100   ) );
 do {
     printfAt(11,73,"[    ]"); scanfAt( 11,74, "%f", &vm    );
    } while ( (    vm  <     0.0 ) || (   vm  > 50000.0) );
 do {
     printfAt(19,15,"[    ]"); scanfAt( 19,16, "%f", &a0    );
    } while ( (     a0 <     0.0 ) || (    a0 >  100.0 ) );
 do {
     printfAt(20,15,"[    ]"); scanfAt( 20,16, "%f", &b0    );
    } while ( (     b0 <     0.0 ) || (    b0 >  100.0 ) );
 do {
     printfAt(21,15,"[    ]"); scanfAt( 21,16, "%f", &c0    );
    } while ( (     c0 <     0.0 ) || (    c0 >  100.0 ) );
 do {
     printfAt(22,15,"[    ]"); scanfAt( 22,16, "%f", &d0    );
    } while ( (     d0 <     0.0 ) || (    d0 >  100.0 ) );
 do {
     printfAt(19,33,"[    ]"); scanfAt( 19,34, "%f", &e0    );
    } while ( (     e0 <     0.0 ) || (    e0 >  100.0 ) );
 do {
     printfAt(20,33,"[    ]"); scanfAt( 20,34, "%f", &f0    );
    } while ( (     f0 <     0.0 ) || (    f0 >  100.0 ) );
 do {
     printfAt(21,33,"[    ]"); scanfAt( 21,34, "%f", &g0    );
    } while ( (     g0 <     0.0 ) || (    g0 >  100.0 ) );
 do {
     printfAt(22,33,"[    ]"); scanfAt( 22,34, "%f", &h0    );
    } while ( (     h0 <     0.0 ) || (    h0 >  100.0 ) );
 do {
     printfAt(19,55,"[    ]"); scanfAt( 19,56, "%f", &a1    );
    } while ( (     a1 <     0.0 ) || (    a1 >  100.0 ) );
 do {
     printfAt(20,55,"[    ]"); scanfAt( 20,56, "%f", &b1    );
    } while ( (     b1 <     0.0 ) || (    b1 >  100.0 ) );
 do {
     printfAt(21,55,"[    ]"); scanfAt( 21,56, "%f", &c1    );
    } while ( (     c1 <     0.0 ) || (    c1 >  100.0 ) );
 do {
     printfAt(22,55,"[    ]"); scanfAt( 22,56, "%f", &d1    );
    } while ( (     d1 <     0.0 ) || (    d1 >  100.0 ) );
 do {
     printfAt(19,73,"[    ]"); scanfAt( 19,74, "%f", &e1    );
    } while ( (     e1 <     0.0 ) || (    e1 >  100.0 ) );
 do {
     printfAt(20,73,"[    ]"); scanfAt( 20,74, "%f", &f1    );
    } while ( (     f1 <     0.0 ) || (    f1 >  100.0 ) );
 do {
     printfAt(21,73,"[    ]"); scanfAt( 21,74, "%f", &g1    );
    } while ( (     g1 <     0.0 ) || (    g1 >  100.0 ) );
 do {
     printfAt(22,73,"[    ]"); scanfAt( 22,74, "%f", &h1    );
    } while ( (     h1 <     0.0 ) || (    h1 >  100.0 ) );
 Vnauini( j,st,al, ap, vr1, r1,vr2, r2,vm,
          a0 , a1 , b0 , b1 , c0  , c1 , d0  , d1 ,
          e0 , e1 , f0 , f1 ,  g0 , g1 ,  h0 , h1 );
 for(i=1;i<=MAXVN;i++)       /* Automatische agvnx[.]-Zuweisung an   */
  {                          /* die Aggregatdateien, die gebraucht   */
   BAV[1].DatenBAV.Vnag2[ VN[j].DatenVN->Vr ]++; /* werden           */
   BAV[1].DatenBAV.Vnag3[ VN[j].DatenVN->Vk ]++;
  }
 for( i = 1;  i <=     7 ; i++ )
  { if ( BAV[1].DatenBAV.Vnag2[i] > 0 ) { agvn2[i] = 1;} }
 for( i = 1;  i <=     3 ; i++ )
  { if ( BAV[1].DatenBAV.Vnag3[i] > 0 ) { agvn3[i] = 1;} }
 agvn4[1] = 1; /* Subjektklasse Versicherungsnehmer: immer erzeugen  */
 printfAt(24,35,"[ [1] Ruecksprung [0] Weiterer VN [    ] ]");
 scanfAt( 24,70, "%d", &ende);
 } while ( ende != 1);
}

/* ***************************************************************** */
/* func Erstmkt() : Allgemeine Marktparameter konfigurieren          */
/*                                                                   */
/*                  Aufgerufen von func Moderst()                    */
/* ***************************************************************** */
func Erstmkt() {
 int i;                                  /* Schleifenzaehler         */
 int a, b, e;
 float c, d;
 clearScreen();
 printfAt( 1,25, "[ Allgemeine Marktparameter konfigurieren ]");
 printfAt( 5,10, "Periode mit Aenderungsschock   : > "); /* Maske... */
 printfAt( 8,10, "Lauf    mit Aenderungsschock   : > "); /* aufbauen */
 printfAt(11,10, "Kosten pro Praemieninformation :   ");
 printfAt(14,10, "Periodenzinssatz               :   ");
 printfAt(17,10, "Wiederholungslaeufe,1:Ja,0:Nein:   ");
 for( i =  SIMLAENGE ; i >= 1; i--)                      /* Daten an-*/
  { if ( BAV[1].DatenBAV.As[i] == 1 )  { a = i ; }  }    /* zeigen   */
 printfAt( 5,50, "%3d",a);
 for( i =  SIMLAENGE ; i >= 1; i--)
  { if ( BAV[1].DatenBAV.Ar[i] == 1 )  { b = i ; }  }
 printfAt( 8,50, "%3d",b);
 printfAt(11,50, "%01.2f",BAV[1].DatenBAV.Sk[1]);
 printfAt(14,50, "%01.2f",BAV[1].DatenBAV.Zs[1]);
 printfAt(17,50, "%1d"   ,BAV[1].DatenBAV.Rp   );
 do {                          /* Neue Werte einlesen und pruefen ...*/
     printfAt( 5,60,"[       ]");  scanfAt( 5,62, "%d", &a);
    } while ( ( a < 1 ) || ( a > 100 ) );
 do {
     printfAt( 8,60,"[       ]");  scanfAt( 8,62, "%d", &b);
    } while ( ( b < 1 ) || ( b > 100 ) );
 do {
     printfAt(11,60,"[       ]");  scanfAt(11,62, "%f", &c);
    } while ( ( c < 0.0) || ( c > 10.0) );
 do {
     printfAt(14,60,"[       ]");  scanfAt(14,62, "%f", &d);
    } while ( ( d < 0.0) || ( d > 1.0) );
 do {
     printfAt(17,60,"[       ]");  scanfAt(17,62, "%d", &e);
    } while ( ( e < 0  ) || ( e > 1  ) );
 Bavauin( a, b, c, d, e); /* Initialisierungsroutine aufrufen        */
/* Moderst();  Ruecksprung zum vorherigen Menue                      */
}

/* ***************************************************************** */
/* func Moderst() : Modell erstellen                                 */
/*                                                                   */
/*                  Aufgerufen von func Mkbear()                     */
/* ***************************************************************** */
func Moderst() {
 int j;                                /* Auswahlvariable            */
 clearScreen();
 printfAt( 1,30, "[ Modell erstellen ]");
 printfAt( 9,12, "[1] Versicherer konfigurieren                      ");
 printfAt(12,12, "[2] Versicherungsnehmer konfigurieren              ");
 printfAt(15,12, "[3] Allgemeine Marktparameter konfigurieren        ");
 printfAt(18,12, "[4] Zum Menue [ Marktkonfiguration bearbeiten ]    ");
 do {
     printfAt(20,12,"[ ] "); scanfAt(20,13,"%d",&j);
    } while ( ( j < 1 ) || ( j > 4 ) );
 switch(j)
  {
   case 1: /* Versicherer konfigurieren */
      Erstvu();
     break;
   case 2: /* Versicherungsnehmer konfigurieren */
      Erstvn();
     break;
   case 3: /* Allgemeine Marktparameter konfigurieren */
      Erstmkt();
     break;
   case 4: /* Zum Vormenue */
       Mkbear();
     break;
   default:
     printfAt(24,2, "UNBEKANNTE AUSWAHL!");
     break;
 } /* END: switch(j)  */
} /* END: Moderst() */

/* ***************************************************************** */
/* func Mkbear(): Modellkonfiguration auswaehlen oder erstellen      */
/*                                                                   */
/*                Aufgerufen von func Mainmenu()                     */
/* ***************************************************************** */
func Mkbear() {
 int j;                                /* Auswahlvariable            */
 clearScreen();
 printfAt( 1,21, "[ Marktkonfiguration bearbeiten ]");
 printfAt( 2,10, "Vordefinierte Modelle ohne Schocks   ");
 printfAt( 4,12, "[1] Homogenes Angebot bei homogener Nachfrage      ");
 printfAt( 6,12, "[2] Homogenes Angebot bei heterogener Nachfrage    ");
 printfAt( 8,12, "[3] Heterogenes Angebot bei homogener Nachfrage    ");
 printfAt(10,10, "Vordefinierte Modelle mit Schocks                  ");
 printfAt(12,12, "[4] Einfacher Aenderungsschock, homogene Nachfrage ");
 printfAt(14,12, "[5] Einfacher Aktivierungsschock, homogenes Angebot");
 printfAt(16,12, "[6] Komplexer Marktschock: Die Wiedervereinigung   ");
 printfAt(18,10, "Selbstdefinierte Modelle                           ");
 printfAt(20,12, "[7] Modell erstellen                               ");
 printfAt(22,12, "[8] Zum Hauptmenu                                  ");
 do {
     printfAt(23,12,"[ ] "); scanfAt(23,13,"%d",&j);
    } while ( ( j < 1 ) || ( j > 8 ) );
 switch(j)
  {
   case 1:                  /* Vordefiniertes Modell 1 auswaehlen ...*/
     Vdefmd1();
     break;
   case 2:                  /* Vordefiniertes Modell 2 auswaehlen ...*/
     Vdefmd2();
     break;
   case 3:                  /* Vordefiniertes Modell 3 auswaehlen ...*/
     Vdefmd3();
     break;
   case 4:                  /* Vordefiniertes Modell 4 auswaehlen ...*/
     Vdefmd4();
     break;
   case 5:                  /* Vordefiniertes Modell 5 auswaehlen ...*/
     Vdefmd5();
     break;
   case 6:                  /* Vordefiniertes Modell 6 auswaehlen ...*/
     Vdefmd6();             /* Das Modell der Wiedervereinigung      */
     break;
   case 7:                  /* Selbstdefiniertes Modell erstellen ...*/
     Moderst();
     break;
   case 8:                  /* Zurueck zum Hauptmenu ...             */
     Mainmenu();
     break;
   default:
     printfAt(24,2, "UNBEKANNTE AUSWAHL!");
     break;
 } /* END: switch(j)  */
} /* END: func Mkbear() */

/* ***************************************************************** */
/* func Starts(): Eingabe von Periodenanzahl und Anzahl der Laeufe   */
/*                                                                   */
/*                Aufgerufen von func Mainmenu()                     */
/* ***************************************************************** */
func Starts() {
 int j;
 clearScreen();
 printfAt( 6,15,"Sollen bisher erzeugte Aggregatdateien     ");
 printfAt( 7,15,"geloescht werden? [1] Ja [0] Nein : [     ]");
 do {
     scanfAt( 7,54, "%d", &j);
    } while ( ( j < 0  ) || ( j > 1  ) );
 if ( j == 1 )
  {
   #if defined(PC386)
    system("del imsv*.dat");
   #endif
   #if defined(UNIX)
    system("rm imsv*.dat");
   #endif
  }
 clearScreen(); box(22,0,2,80);
  do
  {
   printfAt(23,3,"Periodenanzahl der Einzelsimulation eingeben: [   ]");
   scanfAt(23,50,"%d", &sl);
  } while ( (sl < 1 ) || ( sl > SIMLAENGE ) );
 if ( BAV[1].DatenBAV.Rp == 1 ) /* Wiederholungen sind erlaubt ... */
  {
   do
    {
     printfAt(23,3,"Anzahl der Simulationslaeufe eingeben       : [   ]");
     scanfAt(23,50,"%d", &al);
    } while ( (al < 1 ) || ( al > SIMLAENGE ) );
   printfAt(23,3,"                                                   ");
  } /* END: if ( BAV[1].DatenBAV.Rp == 1 ) */
  rl  = 1;
  clearScreen();
  box(8,8,14,36);
  printfAt(10,10,"Aktuelle Periode:                ");
  printfAt(11,10,"Aktueller Lauf  :                ");
  printfAt(12,10,"Bisher berechnet:        Prozent ");
  printfAt(15,10,"Version         : %8s",version    );
  printfAt(17,10,"I M S   (c) Martin Koehler       ");
  printfAt(18,10,"Institut fuer Versicherungs-     ");
  printfAt(19,10,"betriebslehre und -informatik    ");
  printfAt(20,10,"Universitaet Hannover            ");
} /* END: func Starts() */

/* ***************************************************************** */
/* func Analyvu() : Analyse der Simulationsergebnisse der            */
/*                  Versicherer                                      */
/*                  Aufgerufen von func Analy()                      */
/* ***************************************************************** */
func Analyvu() {
 int ende=0;
 int a,b,c,i,k,j,l,m;
 int attrib[13]; /* 1..12 = Attribut, das geplottet wird = Daten-    */
                 /* spalte in der .dat-Datei                         */
                               /* Aggregatauswahl der Versicherungen */
 int lagvu1[MAXVU+1], lagvu2[10], lagvu3[4], lagvu4[2];
 static char *vuattr[] = { "                      ",
  "Praemie,      Sparte 1", "Werbung,      Sparte 1",
  "Reserven,     Sparte 1", "Versicherte,  Sparte 1",
  "Schadenzahl,  Sparte 1", "Schadensumme, Sparte 1",
  "Praemie,      Sparte 2", "Werbung,      Sparte 2",
  "Reserven,     Sparte 2", "Versicherte,  Sparte 2",
  "Schadenzahl,  Sparte 2", "Schadensumme, Sparte 2" };
 file *t;                                /* temporaere GNUplot-Datei */
 char fname[13];                         /* GNUplot Dateiname        */
 for ( i = 1; i <= MAXVU; i++) { lagvu1[i] = 0; } /* Lokale Vektoren */
 for ( i = 1; i <=  9   ; i++) { lagvu2[i] = 0; } /* fuer die Wahl   */
 for ( i = 1; i <=  3   ; i++) { lagvu3[i] = 0; } /* der Aggregate   */
 for ( i = 0; i <=  1   ; i++) { lagvu4[i] = 0; } /* auf Null setzen */
 for ( i = 0; i <= 12   ; i++) { attrib[i] = 0; }
 do { /* BEGIN: while ( ende == 1 ) */
  clearScreen();
  printfAt( 1,15, "[ Modellergebnis der Versicherer analysieren ]");
  t = fopen("temp.gnu","w+t");    /* Entweder Datei neu anlegen oder */
  if ( t == (file *) 0 )          /* bestehende Datei ueberschreiben */
   {
    fprintf(runreport,"Analyvu(): Kann temp.gnu nicht oeffnen\n");
   }
   else
    {
     fclose(t);                   /* ... und wieder schliessen...    */
    }
  do {
      printfAt( 3, 5,"Aggregatstufe: I[1], II[2], III[3], IV[4][  ]");
       scanfAt( 3,47,"%d",&a);
     } while ( ( a < 1 ) || ( a > 4 ) );
  switch(a)
   {
    case 1:
      printfAt( 4, 5,"Erzeugte Aggregate der Einzelversicherungen:");
      k=0;
      for( i=1; i<=MAXVU;i++)       /* Aggregate Stufe I darstellen  */
       {
        if ( agvu1[i] == 1)
         {
          printfAt(5,5+7*k,"VU[%02d] ",i);                       
          k++;
         }
       }
      for( i=1; i<=MAXVU;i++)       /* ... und abfragen ...          */
       {
        if ( agvu1[i] == 1)
         {
          do {
           printfAt( 6, 5,
            "VU[%02d] nicht plotten[0], plotten[1], replotten[2][ ]",i);
            scanfAt( 6,55,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvu1[i] = k;
         }
       }
     break;
    case 2:
      printfAt( 4, 5,"Erzeugte Aggregate der Verhaltensregeln    :");
      k = 0;
      for(i = 1; i <= 9; i++)
       {
        if ( agvu2[i] == 1)
         {
          printfAt(5+k,5,"VR[%02d] %s",i,vrvunm[i]);
          k++;
         }
       }
      for( i = 1; i <= 9; i++)      /* ... und abfragen ...          */
       {
        if ( agvu2[i] == 1)
         {
          do {
           printfAt( 15,5,
            "VR[%02d] nicht plotten[0], plotten[1], replotten[2][ ]",i);
            scanfAt( 15,55,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvu2[i] = k;
         }
       }
     break;
    case 3:
      printfAt( 4, 5,"Erzeugte Aggregate der Regelklassen        :");
      k = 0;
      for( i = 1; i <= 3; i++)
       {
        if ( agvu3[i] == 1)
         {
          printfAt(5,5+7*k,"VK[%02d] ",i);
          k++;
         }
       }
      for( i = 1; i <= 3;i++)       /* ... und abfragen ...          */
       {
        if ( agvu3[i] == 1)
         {
          do {
           printfAt(  9,5,
            "VK[%02d] nicht plotten[0], plotten[1], replotten[2][ ]",i);
            scanfAt(  9,55,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvu3[i] = k;
         }
       }
     break;
    case 4:
      printfAt( 4, 5,"Erzeugte Aggregate der Subjektklasse       :");
      if ( agvu4[1] == 1)
       {
        printfAt( 5, 5,"Aggregat der Subjektklasse VU erzeugt");
       }
      do {
       printfAt( 6, 5, "Sk[1] nicht plotten[0], plotten[1], replotten[2][ ]",i);
            scanfAt( 6,54,"%d",&k);
         } while ( ( k < 0 )  || ( k > 2 ) );
      lagvu4[1] = k;
     break;
   }
  k=0;
  do {                             /* Attribute = Spalten auswaehlen */
      clearScreen();
      for( i = 1; i <= 12; i++ )
       {
        printfAt( 5+i,10,"[%02d] %s", i, vuattr[i] );
       }
      do {
          printfAt(18,10,"Attributnummer [  ]");
           scanfAt(18,26,"%d",&j);
         } while ( ( j < 0 )  || ( j > 12) );
      attrib[j] = 1;   /* ..weil in erster Spalte die Periode steht..*/
      m=j;
      l=j+1;       /* ... auf j wird weiter unter wieder zugegriffen */
     } while ( k != 0 );
   do {
       printfAt(21,10,"Simulationslauf: [1] .... [%03d]         [   ]",rl);
        scanfAt(21,52,"%d",&c);
      } while ( ( c < 1 ) || ( c > rl ) );
   t = fopen("temp.gnu","a+t");  /* GNUplot-Datei beschreiben        */
   if ( t == (file *) 0 )
    {
     fprintf(runreport,"Analyvu(): Kann temp.gnu nicht oeffnen\n");
    }
    else
     {
      fprintf(t,"# IMS v1.0 GNUplot-Steuerdatei\n");
      for( i = 1; i <= MAXVU; i++)
       {
        if (lagvu1[i] != 0 )       /* Versicherer i wird gedruckt !  */
         {
          fprintf(t,"set title  'IMS: Versicherer: VU[%02d]' \n",i);
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vuattr[m]);
          switch( lagvu1[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvu1nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvu1nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvu1[i] != 0 )*/
       } /* END: for( i = 1; i <= MAXVU; i++) */
      for( i = 1; i <=     9; i++)
       {
        if (lagvu2[i] != 0 )       /* Verhaltensregel i drucken   !  */
         {
          fprintf(t,"set title  'IMS: Verhaltensregel[%s]'\n",vrvunm[i]);
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vuattr[m]);
          switch( lagvu2[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvu2nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvu2nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvu2[i] != 0 )*/
       } /* END: for( i = 1; i <=     9; i++) */
      for( i = 1; i <=     3; i++)
       {
        if (lagvu3[i] != 0 )       /* Verhaltensregelklasse i drucken*/
         {
          switch(i)
           {
            case 1:
              fprintf(t,"set title  'IMS: Informationsfreie VRs'\n");
             break;
            case 2:
              fprintf(t,"set title  'IMS: VRs mit Eigeninformation'\n");
             break;
            case 3:
              fprintf(t,"set title  'IMS: VRs mit Fremdinformation'\n");
             break;
           }
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vuattr[m]);
          switch( lagvu3[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvu3nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvu3nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvu3[i] != 0 )*/
       } /* END: for( i = 1; i <=     3; i++) */
       if (lagvu4[1] != 0 )       /* Subjekteklassse der VUs drucken*/
        {
         fprintf(t,"set title  'IMS: Subjektklasse VUs'\n");
         fprintf(t,"set xlabel 'Periode'\n");
         fprintf(t,"set ylabel '%s'\n", vuattr[m]);
         switch( lagvu4[1] )
          {
           case 1:
            fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                   (c-1)*sl, c*sl, agvu4nm[1], l );
            break;
           case 2:
            fprintf(t,"replot       '%s' using 1:%d with lines\n",
                       agvu4nm[1], l );
            break;
          } /* END: switch( lagvu4[1] ) */
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
        } /* END: if (lagvu4[1] != 0 ) */
     } /* END:  switch(a) */
  fclose(t);
  system("gnuplot temp.gnu");
  #if defined(PC386)
   system("del temp.gnu");
  #endif
  #if defined(UNIX)
   system("rm temp.gnu");
  #endif
  clearScreen();
  do {
      printfAt(23,10,"ENDE [1], weitere Grafiken [0] [ ]");
       scanfAt(23,42,"%d",&ende);
     } while ( ( ende < 0 )  || ( ende > 1) );
  } while ( ende != 1 );
} /* END: func Analyvu() */

/* ***************************************************************** */
/* func Analyvn() : Analyse der Simulationsergebnisse der            */
/*                  Versicherungsnehmer                              */
/*                  Aufgerufen von func Analy()                      */
/* ***************************************************************** */
func Analyvn() {
 int ende=0;
 int a,b,c,i,k,j,l,m;
 int attrib[12]; /* 1..11 = Attribut, das geplottet wird = Daten-    */
                 /* spalte in der .dat-Datei                         */
                           /* Aggregatauswahl der Versicherungsnehmer*/
 int lagvn1[MAXVN+1], lagvn2[7],  lagvn3[4], lagvn4[2];
 char *vnattr[] = { "                      ",
                    "Gewaehlte Versicherung,     Risiko 1",
                    "Status,                     Risiko 1",
                    "Gezahlte Praemie,           Risiko 1",
                    "Selbstversicherte Schaeden, Risiko 1",
                    "Gesamtschaeden,             Risiko 1",
                    "Gewaehlte Versicherung,     Risiko 2",
                    "Status,                     Risiko 2",
                    "Gezahlte Praemie,           Risiko 2",
                    "Selbstversicherte Schaeden, Risiko 2",
                    "Gesamtschaeden,             Risiko 2",
                    "Periodenendvermoegen                " };
 file *t;                                /* temporaere GNUplot-Datei */
 char fname[13];                         /* GNUplot Dateiname        */
 for ( i = 1; i <= MAXVN; i++) { lagvn1[i] = 0; } /* Lokale Vektoren */
 for ( i = 1; i <=  6   ; i++) { lagvn2[i] = 0; } /* fuer die Wahl   */
 for ( i = 1; i <=  3   ; i++) { lagvn3[i] = 0; } /* der Aggregate   */
 for ( i = 0; i <=  1   ; i++) { lagvn4[i] = 0; } /* auf Null setzen */
 for ( i = 0; i <= 12   ; i++) { attrib[i] = 0; }
 do { /* BEGIN: while ( ende == 1 ) */
  clearScreen();
  printfAt( 1,15, "[ Modellergebnis der Versicherten analysieren ]");
  t = fopen("temp.gnu","w+t");    /* Entweder Datei neu anlegen oder */
  if ( t == (file *) 0 )          /* bestehende Datei ueberschreiben */
   {
    fprintf(runreport,"Analyvn(): Kann temp.gnu nicht oeffnen\n");
   }
   else
    {
     fclose(t);                   /* ... und wieder schliessen...    */
    }
  do {
      printfAt( 3, 5,"Aggregatstufe: I[1], II[2], III[3], IV[4][  ]");
       scanfAt( 3,47,"%d",&a);
     } while ( ( a < 1 ) || ( a > 4 ) );
  switch(a)
   {
    case 1:
      printfAt( 4, 5,"Erzeugte Aggregate der Einzelversicherten  :");
      k=0;          
      for( i=1; i<=MAXVN;i++)       /* Aggregate Stufe I darstellen  */
       {
        if ( agvn1[i] == 1)
         {
          printfAt(5,5+7*k,"VN[%03d] ",i);
          k++;
         }
       }
      for( i=1; i<=MAXVN;i++)       /* ... und abfragen ...          */
       {
        if ( agvn1[i] == 1)
         {
          do {
           printfAt( 6, 5,
            "VN[%03d] nicht plotten[0], plotten[1], replotten[2][   ]",i);
            scanfAt( 6,57,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvn1[i] = k;
         }
       }
     break;
    case 2:
      printfAt( 4, 5,"Erzeugte Aggregate der Verhaltensregeln    :");
      k = 0;
      for(i = 1; i <= 6; i++)
       {
        if ( agvn2[i] == 1)
         {
          printfAt(5+k,5,"VR[%02d] %s",i,vrvnnm[i]);
          k++;
         }
       }
      for( i = 1; i <= 6; i++)      /* ... und abfragen ...          */
       {
        if ( agvn2[i] == 1)
         {
          do {
           printfAt( 15, 5,
            "VR[%02d] nicht plotten[0], plotten[1], replotten[2][   ]",i);
            scanfAt( 15,58,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvn2[i] = k;
         }
       }
     break;
    case 3:
      printfAt( 4, 5,"Erzeugte Aggregate der Regelklassen        :");
      k = 0;
      for( i = 1; i <= 3; i++)
       {
        if ( agvn3[i] == 1)
         {
          printfAt(5,5+7*k,"VK[%02d] ",i);
          k++;
         }
       }
      for( i = 1; i <= 3;i++)       /* ... und abfragen ...          */
       {
        if ( agvn3[i] == 1)
         {
          do {
           printfAt(  9,5,
            "VK[%02d] nicht plotten[0], plotten[1], replotten[2][   ]",i);
            scanfAt(  9,55,"%d",&k);
             } while ( ( k < 0 )  || ( k > 2 ) );
          lagvn3[i] = k;
         }
       }
     break;
    case 4:
      printfAt( 4, 5,"Erzeugte Aggregate der Subjektklasse       :");
      if ( agvn4[1] == 1)
       {
        printfAt( 5, 5,"Aggregat der Subjektklasse VN erzeugt");
       }
      do {
       printfAt( 6, 5, 
            "Sk[1] nicht plotten[0], plotten[1], replotten[2][   ]",i);
            scanfAt( 6,55,"%d",&k);
         } while ( ( k < 0 )  || ( k > 2 ) );
      lagvn4[1] = k;
     break;
   }
  k=0;
  do {                             /* Attribute = Spalten auswaehlen */
      clearScreen();
      for( i = 1; i <= 11; i++ )
       {
        printfAt( 5+i,10,"[%02d] %s", i, vnattr[i] );
       }
      do {
          printfAt(18,10,"Attributnummer [   ]");
           scanfAt(18,26,"%d",&j);
         } while ( ( j < 0 )  || ( j > 11) );
      attrib[j] = 1;   /* ..weil in erster Spalte die Periode steht..*/
      m=j;
      l=j+1;       /* ... auf j wird weiter unter wieder zugegriffen */
     } while ( k != 0 );
   do {
       printfAt(21,10,"Simulationslauf: [1] .... [%03d]         [   ]",rl);
        scanfAt(21,52,"%d",&c);
      } while ( ( c < 1 ) || ( c > rl ) );
   t = fopen("temp.gnu","a+t");  /* GNUplot-Datei beschreiben        */
   if ( t == (file *) 0 )
    {
     fprintf(runreport,"Analyvn(): Kann temp.gnu nicht oeffnen\n");
    }
    else
     {
      fprintf(t,"# IMS v1.0 GNUplot-Steuerdatei\n");
      for( i = 1; i <= MAXVN; i++)
       {
        if (lagvn1[i] != 0 )      /* Versicherter i wird gedruckt !  */
         {
          fprintf(t,"set title  'IMS: Versicherter: VN[%03d]' \n",i);
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vnattr[m]);
          switch( lagvn1[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvn1nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvn1nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvn1[i] != 0 )*/
       } /* END: for( i = 1; i <= MAXVN; i++) */
      for( i = 1; i <=     6; i++)
       {
        if (lagvn2[i] != 0 )       /* Verhaltensregel i drucken   !  */
         {
          fprintf(t,"set title  'IMS: Verhaltensregel[%s]'\n",vrvnnm[i]);
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vnattr[m]);
          switch( lagvn2[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvn2nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvn2nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvn2[i] != 0 )*/
       } /* END: for( i = 1; i <=     6; i++) */
      for( i = 1; i <=     3; i++)
       {
        if (lagvn3[i] != 0 )       /* Verhaltensregelklasse i drucken*/
         {
          switch(i)
           {
            case 1:
              fprintf(t,"set title  'IMS: Informationsfreie VRs'\n");
             break;
            case 2:
              fprintf(t,"set title  'IMS: VRs mit Eigeninformation'\n");
             break;
            case 3:
              fprintf(t,"set title  'IMS: VRs mit Fremdinformation'\n");
             break;
           }
          fprintf(t,"set xlabel 'Periode'\n");
          fprintf(t,"set ylabel '%s'\n", vnattr[m]);
          switch( lagvn3[i] )
           {
            case 1:
             fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                    (c-1)*sl, c*sl, agvn3nm[i], l );
             break;
            case 2:
             fprintf(t,"replot       '%s' using 1:%d with lines\n",
                        agvn3nm[i], l );
             break;
           }
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
         } /* END: if (lagvn3[i] != 0 )*/
       } /* END: for( i = 1; i <=     3; i++) */
       if (lagvn4[1] != 0 )       /* Subjekteklassse der VUs drucken*/
        {
         fprintf(t,"set title  'IMS: Subjektklasse VNs'\n");
         fprintf(t,"set xlabel 'Periode'\n");
         fprintf(t,"set ylabel '%s'\n", vnattr[m]);
         switch( lagvn4[1] )
          {
           case 1:
            fprintf(t,"plot [%d:%d] '%s' using 1:%d with lines\n",
                   (c-1)*sl, c*sl, agvn4nm[1], l );
            break;
           case 2:
            fprintf(t,"replot       '%s' using 1:%d with lines\n",
                       agvn4nm[1], l );
            break;
          } /* END: switch( lagvn4[1] ) */
           #if defined(UNIX)
            fprintf(t,"pause(-1) '<ENTER...>'\n");
           #endif
        } /* END: if (lagvn4[1] != 0 ) */
     } /* END:  switch(a) */
  fclose(t);
  system("gnuplot temp.gnu");
  #if defined(PC386)
   system("del temp.gnu");
  #endif
  #if defined(UNIX)
   system("rm temp.gnu");
  #endif
  clearScreen();
  do {
      printfAt(23,10,"ENDE [1], weitere Grafiken [0] [ ]");
       scanfAt(23,42,"%d",&ende);
     } while ( ( ende < 0 )  || ( ende > 1) );
  } while ( ende != 1 );
} /* END: func Analyvn() */

/* ***************************************************************** */
/* func Analy() : Analyse der Simulationsergebnisse                  */
/*                                                                   */
/*                Aufgerufen von func Mainmenu()                     */
/* ***************************************************************** */
func Analy() {
 int j;                                          /* Schleifenzaehler */
 /* for(;;)             ENDLOSschleife, die ueber [4] verlassen wird
  { */
   clearScreen();
   printfAt( 1,25, "[ Modellergebnis analysieren ]");
   printfAt( 7,10, "[1] Grafische Analyse der Versicherer         ");
   printfAt( 9,10, "[2] Grafische Analyse der Versicherungsnehmer ");
   printfAt(11,10, "[3] Grafiken interaktiv erstellen             ");
   printfAt(13,10, "[4] Zurueck zum Hauptmenu                     ");
   do {
       printfAt(15,10,"[ ] "); scanfAt(15,11,"%d",&j);
      } while ( ( j < 1 )  || ( j > 4));
   switch(j)
    {
     case 1:                    /* Grafische Analyse der Versicherer */
        Analyvu();
      break;
     case 2:            /* Grafische Analyse der Versicherungsnehmer */
        Analyvn();
      break;
     case 3:                        /* Grafiken interaktiv erstellen */
        system("gnuplot");          /* .. d.h. GNUplot starten       */
        break;
     case 4:                                /* Zurueck zum Hauptmenu */
        Mainmenu();
      break;
     default:
        printfAt(23,10, "ERROR: unbekannte Auswahl!");
      break;
    } /* END: switch(j) */
 /*  }  END: for(;;) */
}

/* ***************************************************************** */
/* func Pginfo() : Programminformation                               */
/*                                                                   */
/*                 Aufgerufen von func Mainmenu()                    */
/* ***************************************************************** */
func Pginfo() {
 clearScreen();
 printfAt( 1,27,"[ Programminformation ]");
 printfAt( 3,10,"      I M S     The Insurance Market Simulation       ");
 printfAt( 5,10," Simulationsprogramm zur Analyse von exogenen Schocks ");
 printfAt( 6,10," auf Versicherungsmaerkten im Rahmen der Dissertation:");
 printfAt( 8,10,"      Eine Computersimulation zur Analyse der         ");
 printfAt( 9,10,"      Auswirkungen von exogenen Schocks auf           ");
 printfAt(10,10,"      Versicherungsmaerkte - am Beispiel der          ");
 printfAt(11,10,"      deutschen Wiedervereinigung                     ");
 printfAt(13,10,"      Dipl-Oek. Martin Koehler                        ");
 printfAt(14,10,"      Institut fuer Versicherungsbetriebslehre        ");
 printfAt(15,10,"      der Universitaet Hannover                       ");
 printfAt(17,10,"  Referent  : Prof. Dr. J.-M. Graf von der Schulenburg");
 printfAt(18,10,"              Universitaet Hannover, FB Wirtschaft    ");
 printfAt(19,10,"  Koreferent: Prof. Dr. P. Stahlecker                 ");
 printfAt(20,10,"              Universitaet Hamburg,  FB Wirtschaft    "); 
 waitKey(); waitKey();
}
                                                                          
/* ***************************************************************** */
/* func Pgende() : Programmende                                      */
/*                                                                   */
/*                 Aufgerufen von func Mainmenu()                    */
/* ***************************************************************** */
func Pgende() {
 clearScreen();
 Freemem();
 fprintf(runreport,"********** IMS-Reportdatei ENDE *********\n");
 fclose(runreport);                      /* REPORTDATEI schliessen ! */
 printfAt(24,2,"[ Programm-ENDE ]");
 waitKey(); waitKey(); closeScreen(); cls();
 exit(0);                                /* C-Funktion aus clib      */
} /* END: func Pgende() */

/* ***************************************************************** */
/* func Mainmenu() : Hauptmenu                                       */
/*                                                                   */
/*                   Aufgerufen von func Init()                      */
/* ***************************************************************** */
func Mainmenu() {
 int j, startsim = 0 ;
 openScreen();
 while ( startsim == 0 )                  /* HAUPTKONTROLL-SCHLEIFE */
  {
   clearScreen();
   printfAt( 1,23, "[ IMS Insurance Market Simulation ]");
   printfAt( 5,20, "[1] Modell laden                        ");
   printfAt( 7,20, "[2] Modell speichern                    ");
   printfAt( 9,20, "[3] Modell auswaehlen und bearbeiten    ");
   printfAt(11,20, "[4] Modell simulieren                   ");
   printfAt(13,20, "[5] Modellergebnis analysieren          ");
   printfAt(15,20, "[6] Programminformation                 ");
   printfAt(17,20, "[7] Programm beenden                    ");
   do {
       printfAt(19,20,"[ ] "); scanfAt(19,21,"%d",&j);
      } while ( ( j<1) || (j>7));
   switch(j)
   {
   case 1: /* Modell laden    */
     Mkload();
     break;
   case 2: /* Modell speichern*/
     Mksave();
     break;
   case 3: /* Modell auswaehlen und bearbeiten */
     Mkbear();
     break;
   case 4: /* Modell simulieren */
     Starts();
     startsim = 1;
     break;
   case 5: /* Modellergebnis analysieren  */
     Analy();
     break;
   case 6: /* Programminformation         */
     Pginfo();
     break;
   case 7: /* Programmende                */
     Pgende();
     break;
   default:
     printfAt(24,2,"UNBEKANNTE AUSWAHL!");
     break;
  } /* end CASE ...*/
 } /* end while startsim ... */
} /* END: func Mainmenu ... */

/* ***************************************************************** */
/* func Opendata() : Initialisierung der des Zufallszahlengenerators */
/*                   auf dem die anderen Generatoren aussetzen.      */
/*                   Oeffnen der Reportdatei der Programmablaufkontr.*/
/* ***************************************************************** */
func Opendata() {
 int        seed;       /* Startwert des Zufallszahlengenerators     */
 time_t     x;          /* in time.h definierte Strukturvariable     */
 struct tm *t;
 time(&x);              /* Bestimmung des Startwertes der Zufalls-   */
 t = gmtime(&x);        /* zahlengeneratoren aus der Zeit            */
 seed = (t->tm_sec +1) * (t->tm_min +1) * (t->tm_mday+1);
 srand(seed);           /* Startwert der Generatoren setzen ...      */
 runreport = fopen("imsreport.dat","w");  /* Oeffnen der Reportdatei */
 setvbuf(stdout,(char)NULL, _IONBF,0);    /* Datenpufferung ...      */
 setvbuf(runreport,(char)NULL, _IONBF,0); /* ..ausschalten...        */
 if ( runreport == (file *) 0)
  {
    printf("func Opendata(): Kann imsreport.dat nicht oeffnen.\n");
  }
  else                  /* Dateikopf der Programmablaufkontrolldatei */
   {                    /* schreiben ...                             */
    fprintf(runreport,"IMS Version %s (c) mk, compiled on  %s %s\n\n",
                        version, __DATE__,__TIME__);
    fprintf(runreport,
       "********************** IMS-Reportdatei *******************\n");
    fprintf(runreport,"Seed : %d    \n",seed);
   }  /* END: if ( runreport == (file *) 0) */
} /* END: func Opendata() */

/* ***************************************************************** */
/* func Freemem(): Gibt den in func Getmem() angeforderten Speicher  */
/*                 wieder frei und schreibt eventuelle Fehler in die */
/*                 Reportdatei                                       */
/* ***************************************************************** */
func Freemem() {
int i;
  for(i=1;i<=MAXVU;i++)
   {
    if ( VU[i].DatenVU != (struct s1 *) 0 )
     {
      free( VU[i].DatenVU  );
      fprintf(runreport,"%ld Bytes von VU[%d] freigegeben\n",
                                      (long) sizeof(struct s1),i);
     gmem = gmem - (long) sizeof(struct s1);
     fprintf(runreport,"Bisher allocierter Speicher: %ld Bytes\n",gmem);
     }
     else
     {
      fprintf(runreport,"Kein Speicher von VU[%d] freigegeben\n", i);
     }
    }
   for(i=1;i<=MAXVN;i++)
   {
    if ( VN[i].DatenVN != (struct s2 *) 0 )
     {
      free( VN[i].DatenVN  );
      fprintf(runreport,"%ld Bytes von VN[%d] freigegeben\n",
                           (long) sizeof(struct s2),i);
     gmem = gmem - (long) sizeof(struct s2);
     fprintf(runreport,"Bisher allocierter Speicher: %ld Bytes\n",gmem);
     }
     else
     {
      fprintf(runreport, "Kein Speicher von VN[%d] freigegeben\n",i);
     }
    }
} /* END: func Freemem() */

/* ***************************************************************** */
/* func Getmem() : Funktion zum anfordern von Heap-Space fuer die dy-*/
/*                 namischen ESL-Subjekte der class VU und class VN. */
/*                                                                   */
/* ***************************************************************** */
func Getmem() {
int i;                                  /* Schleifenzaehler          */
if ( load == 0 )
{
 for(i=1;i<=MAXVU;i++)
  {
   VU[i].DatenVU = (struct s1 *) 0;
   VU[i].DatenVU = (struct s1 *) malloc(sizeof(struct s1));
   if ( VU[i].DatenVU != (struct s1 *) 0 )
    {
      gmem = gmem + (long) sizeof(struct s1);
    }
    else /* if ( VU[i].DatenVU == (struct s1 *) 0 )*/
    {
     fprintf(runreport,"Kein Speicher allociert fuer VU[%d]\n", i);
    }
  } /* for(i=1;i<=MAXVU;i++) */
 fprintf(runreport,"Speicher fuer %d VUs: %ld Bytes\n",MAXVU,gmem);
 for(i=1;i<=MAXVN;i++)
  {
   VN[i].DatenVN = (struct s2 *) 0;
   VN[i].DatenVN = (struct s2 *) malloc(sizeof(struct s2));
    if ( VN[i].DatenVN != (struct s2 *) 0 )
     {
      gmem = gmem + (long) sizeof(struct s2);
     }
    else
    {
     fprintf(runreport,"Kein Speicher allociert fuer VN[%d]\n", i);
    }
  } /* END: for(i=1;i<=MAXVN;i++)*/
  fprintf(runreport,"Speicher fuer %d VNs: %ld Bytes\n",MAXVN,gmem);
 } /* end if ( load == 1) */
} /* END: func Getmem() */

/* ***************************************************************** */
/* func Init(): Wird von ess.c(main()) aus aufgerufen. Startet vor   */
/*              dem 1. Lauf das Hauptmenue und kehrt ueber ess.c(main*/
/*              ()) und Fini() wieder hier hin zurueck               */
/* ***************************************************************** */
func Init()              /* jumpback wird in imsdata.c auf 0 initia- */
{                        /* lisiert. Wird beim ERSTEN Lauf auf 1 ge- */
 if ( jumpback == 0 )    /* setzt, damit der Speicher fuer die dyn-  */
 {                       /* amischen Subjekte NICHT doppelt angefor- */
  Opendata();            /* dert wird und die Reportdatei nur im er- */
  jumpback=1;            /* sten Lauf geoeffnet wird.                */
  Getmem();
 }
 Mainmenu();
} /* END: func Init() */

/* ***************************************************************** */
/* func Fini(): Pruef-Funktion fuer Simulationsende. Wenn Fini() be- */
/*              endet ist, wird in ess.c(main()) der naechste Durch- */
/*              lauf gestartet und die func Init() wieder gestartet  */
/* ***************************************************************** */
func Fini()
{
 float prozent;
 if ( period <= sl )
  {
   printfAt(10,28,"%3d",period);
   printfAt(11,28,"%3d",rl    );
   if ( sl * al != 0)
   {
    prozent=100.0*((float)((rl-1)*sl+period))/((float)sl*(float)al);
    printfAt(12,28,"%3.2f",prozent);
   }
   else
   {
    if ( sl != 0 )
     {
      prozent=100.0*((float)((rl-1)*sl+period))/((float)sl);
      printfAt(12,28,"%3.2f",prozent);
     }
   }
   return(GO);
  }
  else
  {
   if ( rl < al )
    {
     period  = 1; /* VORHER: period  = 0 ! */
     logtime = 0;
     rl++;
     return(GO);
    }
   else
   {
    printfAt(22,12,"[ Simulation abgeschlossen ]");
    waitKey();waitKey();
    /*  rl  = 1; */
    period  = 1;
    logtime = 0;
    jumpback=1;
    return(STOP);
   }
  }
} /* END: func Fini()  */
