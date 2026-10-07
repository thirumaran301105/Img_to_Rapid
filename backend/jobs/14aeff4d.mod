MODULE ImageDraw
  ! Generated 2026-10-06 12:06 for ABB GoFa CRB 15000: 2 strokes
  PERS tooldata tPen:=[TRUE,[[0,0,120.0],[1,0,0,0]],[0.3,[0,0,60.0],[1,0,0,0],0,0,0]];
  PERS wobjdata wPaper:=[FALSE,TRUE,"",[[400,-110,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
  CONST robtarget pOrigin:=[[0,0,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST jointtarget jHome:=[[0,0,0,0,30,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST speeddata vDraw:=[40,100,5000,1000];
  CONST speeddata vApproach:=[20,100,5000,1000];
  CONST speeddata vTravel:=[200,200,5000,1000];

  PROC DrawImage()
    ConfL\Off;
    ConfJ\Off;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
    Part1;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
  ENDPROC

  PROC Part1()
    MoveL Offs(pOrigin,74.8,166.8,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,74.8,166.8,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,70.5,163.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,72.0,56.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,223.8,54.7,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,228.0,57.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,226.6,165.3,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,74.8,166.8,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,74.8,166.8,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,80.5,159.7,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,80.5,159.7,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,218.1,159.7,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,220.9,156.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,220.9,64.6,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,218.1,61.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,80.5,61.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,77.6,64.6,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,77.6,156.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,80.5,159.7,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,80.5,159.7,15.0),vApproach,z5,tPen\WObj:=wPaper;
  ENDPROC

ENDMODULE