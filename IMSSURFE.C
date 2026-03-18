#include <stdio.h>
#include <stdarg.h>

#define cls() \
 printf("\033[2J");

#define gotoxy(z,s) \
 printf("\033[%d;%dH",z,s);

#define printfAt(x,y,format,args...) \
 gotoxy(x,y); printf(format, ## args);

#define scanfAt(z,s,format,args...) \
 gotoxy(z,s); fflush(stdin); fscanf(stdin, format, ## args);
  
#define request(z, s, breite, format, args...) \
 box(z-1,s-1,2,breite+2); fflush(stdin); scanfAt(z,s,format, ## args);

void closeScreen()
{      
 cls();
}

void waitKey()
{
 char c;
 fflush(stdin);
 printfAt(24,71,"[ ENTER ]");
 scanfAt(24,79,"%c",&c);        
 printfAt(24,71,"*********");
}
 
void box(int x, int y, int breite, int hoehe)
{
 int i;
 for(i=x;i<=(x+breite);i++)
 {
  gotoxy(i,y);       printf("*");
  gotoxy(i,y+hoehe); printf("*");
 }
 for(i=y;i<=(y+hoehe);i++)
 {
  gotoxy(x,i);        printf("*");
  gotoxy(x+breite,i); printf("*");
 }
}

void openScreen()
{
 cls();
 box(0,0,24,80);
}

void clearScreen()
{               
 cls();
 box(0,0,24,80);                
}

