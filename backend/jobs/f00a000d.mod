MODULE ImageDraw
  ! Generated 2026-10-06 12:16 for ABB IRB 120: 2 strokes
  PERS tooldata tPen:=[TRUE,[[0,0,120.0],[1,0,0,0]],[0.3,[0,0,60.0],[1,0,0,0],0,0,0]];
  PERS wobjdata wPaper:=[FALSE,TRUE,"",[[260,-60,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
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
    MoveL Offs(pOrigin,40.6,89.7,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,40.6,89.7,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,38.4,88.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,39.1,31.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,118.6,31.0,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,120.9,32.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,120.1,89.0,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,40.6,89.7,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,40.6,89.7,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,43.6,86.0,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,43.6,86.0,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,115.7,86.0,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,117.2,84.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,117.2,36.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,115.7,34.7,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,43.6,34.7,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,42.1,36.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,42.1,84.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,43.6,86.0,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,43.6,86.0,15.0),vApproach,z5,tPen\WObj:=wPaper;
  ENDPROC

ENDMODULE