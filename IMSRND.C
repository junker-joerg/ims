
/* Gleichverteilte Zufallsvariable: ganzzahlig                              */
int myrnd()
{ return( rand() % 65535); }                  

/* Gleichverteile Zufallsvariable: 0.0 ... 1.0                              */ 
double myrndf()
{ return ( ( (float) rand() ) / ( 1.0 * 65535.0)  ); }

/* Negativ exponetial verteilte Zufallszahlen */
double expvt(double beta)
{ double h;  
  h = 1.0 - myrndf() ;
 return( - (1.0/beta) * log(h)); 
}


double normal()
{
 int k;
 double n,i ;
 n = -6.0;
 for(k=0;k<=11;k++)
 {
  i = myrndf();
  n = n + i;
 }
 return( n/(double)k );
}

float normal2()
{
 float u1,u2,v1,v2,w,x1,x2,y;
 do {
 u1 = myrndf(); /* Gleichverteilte Zufallsvariable im Intervall 0..1 */
 u2 = myrndf();
 v1 = 2 * u1 - 1.0;
 v2 = 2 * u2 - 1.0;
 w  = v1 * v1 + v2 * v2;
 } while ( w > 1.0 );
 y  = sqrt( (-2.0 * (log (w))) / w );
 x1 = v1 * y;
 x2 = v2 * y;
 return(x1);
}
